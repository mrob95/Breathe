import os

def pytest_configure(config):
    os.environ['BREATHE_TESTING'] = "True"

def pytest_unconfigure(config):
    del os.environ['BREATHE_TESTING']