import os

def pytest_configure(config):
    os.environ['BREATHE_TESTING'] = "True"
    os.environ['BREATHE_REBUILD_COMMAND'] = "rebuild everything test"

def pytest_unconfigure(config):
    del os.environ['BREATHE_TESTING']
    del os.environ['BREATHE_REBUILD_COMMAND']