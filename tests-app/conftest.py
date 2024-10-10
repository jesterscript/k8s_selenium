# Pytest config file to get chrome node pod ip as argument.

def pytest_addoption(parser):
    parser.addoption("--chromeip", action="store", default="default name")