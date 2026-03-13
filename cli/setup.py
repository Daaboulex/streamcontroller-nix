from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-streamcontroller",
    version="0.1.0",
    description="CLI harness for StreamController — manage Stream Deck pages, buttons, plugins, and settings",
    author="cli-anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-streamcontroller=cli_anything.streamcontroller.streamcontroller_cli:main",
        ],
    },
)
