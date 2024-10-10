"""Management module."""

import time
import os
import yaml
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from kubernetes.stream import stream

CONF_FOLDER = "k8s"
APIS_N_KINDS = {
    "Deployment": client.AppsV1Api,
    "Service": client.CoreV1Api,
    "Pod": client.CoreV1Api,
}

# Utility functions


def load_resource_yaml(file_path):
    """Simply load YAML file.

    Args:
        file_path (_type_): _description_

    Returns:
        _type_: _description_
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


class K8Resource:
    """Base class for Pod classes."""

    def __init__(self) -> None:
        """Init."""
        self.yaml_configs: list = []
        self.replica_count: int = 1
        self.resource_name: str = None
        self.namespace: str = "default"

    def _load_resources(self):
        """Store resources from related configs."""
        self._resources = [
            load_resource_yaml(os.path.join(CONF_FOLDER, pod_conf + ".yaml"))
            for pod_conf in self.yaml_configs
        ]

    def delete(self):
        """Delete related resources."""
        print(f"Checking/deleting existing pods for {self.yaml_configs}")
        for resource in self._resources:
            self.resource_name = resource["metadata"]["name"]
            self.namespace = resource["metadata"]["namespace"]
            try:
                kind = resource["kind"]
                api = APIS_N_KINDS[kind]()
                getattr(api, f"delete_namespaced_{kind.lower()}")(
                    name=self.resource_name, namespace=self.namespace
                )
                print(f"{kind} deleted.")
            except KeyError:
                print("Unsupported kind : " + kind)
            except ApiException as e:
                if e.status == 404:
                    print(kind + " not found.")
                else:
                    print(f"Error deleting {kind}: {e}")

    def deploy(self):
        """Deploy releated resources."""
        self.delete()
        time.sleep(5)
        for resource in self._resources:
            try:
                kind = resource["kind"]
                if kind == "Deployment":
                    resource["spec"]["replicas"] = self.replica_count
                api = APIS_N_KINDS[kind]()
                getattr(api, f"create_namespaced_{kind.lower()}")(
                    namespace=self.namespace, body=resource
                )
                print(f"{kind} created.")
            except KeyError:
                print("Unsupported kind : " + kind)
            except ApiException as e:
                if e.status == 409:
                    print(kind + " already exists.")
                else:
                    print(f"Error creating {kind}: {e}")


class ChromeNodePods(K8Resource):
    """Chrome node pods class."""

    def __init__(self, node_count: int = 1) -> None:
        """Init and apply node_count logic."""
        if node_count not in range(1, 5):
            raise RuntimeError("Chrome node pod count must be in [1, 5]")
        super().__init__()
        self.yaml_configs = ["chrome-pod-deployment", "chrome-pod-service"]
        self.replica_count: int = node_count
        self._load_resources()

    def get_chrome_pod(self) -> str:
        """Get available chrome pod ip.

        Raises:
            Exception: _description_

        Returns:
            str: _description_
        """
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(self.namespace)
        for pod in pods.items:
            if "chrome" in pod.metadata.name and pod.status.phase == "Running":
                return pod.status.pod_ip
        raise Exception("No available selenium chrome pods found.")


class TestsPod(K8Resource):
    """Tests Pod class."""

    def __init__(self) -> None:
        """Init."""
        super().__init__()
        self.yaml_configs = ["tests-pod"]
        self._load_resources()

    def get_test_pod(self):
        """Get running Tests pod name.

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(self.namespace)
        for pod in pods.items:
            if "tests" in pod.metadata.name and pod.status.phase == "Running":
                return pod.metadata.name
        raise Exception("No available selenium chrome pods found.")

    def start_test(
        self, target_chrome_pod_ip: str, test_module: str, test_case: str = None
    ):
        """Send execute pytest command to Tests pod.

        Args:
            target_chrome_pod_ip (str): _description_
            test_module (str): _description_
            test_case (str, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_
        """
        core_v1 = client.CoreV1Api()

        # Generate pytest command
        # pytest test_insider.py::test_sanity --chromeip="X.X.X.X"
        exec_command = [
            "pytest",
            test_module if not test_case else f"{test_module}::{test_case}",
            f"--chromeip={target_chrome_pod_ip}",
        ]

        resp = stream(
            core_v1.connect_get_namespaced_pod_exec,
            self.get_test_pod(),
            self.namespace,
            command=exec_command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
            _preload_content=False,
        )

        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                print(f"STDOUT: \n{resp.read_stdout()}")
            if resp.peek_stderr():
                print(f"STDERR: \n{resp.read_stderr()}")

        resp.close()

        if resp.returncode != 0:
            raise Exception("Script failed")

    def delete(self):
        """Tests pod deletion could be longer, wait until it's gone."""
        super().delete()
        v1 = client.CoreV1Api()
        terminated = False
        while not terminated:
            pods = v1.list_namespaced_pod(self.namespace)
            for pod in pods.items:
                if "tests" in pod.metadata.name and pod.status.phase in [
                    "Running",
                    "Terminating",
                ]:
                    print("Waiing tests pod to be terminated.")
                    time.sleep(3)
                    break
            else:
                terminated = True


if __name__ == "__main__":
    config.load_kube_config()
    chrome_pods = ChromeNodePods(node_count=3)
    tests_pod = TestsPod()
    chrome_pods.deploy()
    tests_pod.deploy()
    tests_pod.start_test(
        chrome_pods.get_chrome_pod(), "test_insider.py", test_case="test_sanity"
    )
