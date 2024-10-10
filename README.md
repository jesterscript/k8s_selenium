## Selenium Test Environment with K8s Pods and Pytest
System basically uses Remote Webdriver to execute test cases on the standalone selenium drivers inside a K8s cluster.
### Overview
![insider drawio](https://github.com/user-attachments/assets/61959335-fecf-401e-a698-a0a2883dd3e1)
### Usage

Make sure you have the following installed:

- Python 3.x
- Required libraries (install them using `pip install -r requirements_manage.txt`)

Comment start_test section in **manage.py** script to only deploy Tests Pod and Chrome Node Pods:

```python
if __name__ == "__main__":
  config.load_kube_config()
  chrome_pods = ChromeNodePods(node_count=3)
  tests_pod = TestsPod()
  chrome_pods.deploy()
  tests_pod.deploy()
  # tests_pod.start_test(
  #     chrome_pods.get_chrome_pod(), "test_insider.py", test_case="test_sanity"
  # )
```
Execute **manage.py**
```bash
  python3 manage.py
```
Script checks if Pods are already created, if so deletes them before re-creating. Output :
```bash
  ----------------------------------------------------------------------------------------------------
  Checking/deleting existing pods for ['chrome-pod-deployment', 'chrome-pod-service']
  Deployment deleted.
  Service deleted.
  Deployment created.
  Service created.
  ----------------------------------------------------------------------------------------------------
  Checking/deleting existing pods for ['tests-pod']
  Pod deleted.
  Waiting Tests pod to be terminated.
  Waiting Tests pod to be terminated.
  Waiting Tests pod to be terminated.
  Waiting Tests pod to be terminated.
  Waiting Tests pod to be terminated.
  Waiting Tests pod to be terminated.
  Waiting Tests pod to be terminated.
  Waiting Tests pod to be terminated.
  Waiting Tests pod to be terminated.
  Waiting Tests pod to be terminated.
  Pod created.
```
List current pods :
```bash
 ~/ge/sel  kubectl get pod -o wide                                  ✔  41s  minikube ⎈  17:51:03
NAME                                          READY   STATUS    RESTARTS   AGE     IP             NODE       NOMINATED NODE   READINESS GATES
selenium-chrome-deployment-86b94c4456-9xpgj   1/1     Running   0          7m50s   10.244.0.110   minikube   <none>           <none>
selenium-chrome-deployment-86b94c4456-t7c2d   1/1     Running   0          7m50s   10.244.0.111   minikube   <none>           <none>
selenium-chrome-deployment-86b94c4456-z7x2m   1/1     Running   0          7m50s   10.244.0.109   minikube   <none>           <none>
tests                                         1/1     Running   0          7m14s   10.244.0.112   minikube   <none>           <none>
```
Starting a test
Comment start_test section in **manage.py** script to only deploy Tests Pod and Chrome Node Pods:

```python
if __name__ == "__main__":
  config.load_kube_config()
  chrome_pods = ChromeNodePods(node_count=3)
  tests_pod = TestsPod()
  chrome_pods.deploy()
  tests_pod.deploy()
  tests_pod.start_test(
    chrome_pods.get_chrome_pod(), "test_insider.py", test_case="test_sanity"
  )
```
Start test function waits for tests and chrome pods to be up and running. Then executes:
```bash
pytest test_insidier.py::'test_case' --chromeip="CHROME_POD_IP"
```
Output :
```bash
Waiting for chrome nodes to be running.
STDOUT:
============================= test session starts ==============================
platform linux -- Python 3.10.15, pytest-8.3.3, pluggy-1.5.0
rootdir: /tests-app
collected 1 item

test_insider.py
STDOUT:
.
STDOUT:
                                                        [100%]
STDOUT:


========================= 1 passed in 66.63s (0:01:06) =========================
```

### Conclusion / Missing Points

Thank you for checking out this project.
- Couldn't get a chance for AWS deployment.
- Tests are not fully optimized, I mostly focused on the architecture.
- Have a good day.

