from setuptools import setup, find_packages

setup(
    name="Breathe",
    version="0.1",
    description="Speech recognition extension library",
    author="Mike Roberts",
    author_email="mike.roberts.2k10@googlemail.com",
    license="MIT",
    #   url              = "",
    packages=["breathe"],
    install_requires=["dragonfly2"],
)

