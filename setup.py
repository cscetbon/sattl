from setuptools import setup, find_packages

setup(
    name="sattl",
    version="0.2.0",
    long_description_content_type="text/markdown",
    url="https://github.com/cscetbon/sattl",
    author="Cyril Scetbon",
    author_email="@cscetbon",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        "console_scripts": [
            "sattl = sattl.cli:run"
        ]
    },
    packages=find_packages(exclude=["doc", "tests"]),
    project_urls={
        "Source": "https://github.com/cscetbon/sattl",
    },
)
