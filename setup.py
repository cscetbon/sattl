from setuptools import setup, find_packages

setup(
    name="sattl",
    version="0.1.0",
    long_description_content_type="text/markdown",
    url="https://github.com/2uinc/sattl",  # Optional
    author="2U, Inc.",
    author_email="developers@2u.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={
        "console_scripts": [
            "sattl = sattl.cli:run"
        ]
    },
    packages=find_packages(exclude=["doc", "tests"]),
    project_urls={
        "Source": "https://github.com/2uinc/sattl",
    },
)
