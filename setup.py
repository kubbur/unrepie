from setuptools import setup, find_packages

setup(
    name="unrepie",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "wiringpi",
        "paramiko",
        "pexpect"
    ],
    entry_points={
        "console_scripts": [
            "unrepie=unrepie.main:main"
        ]
    },
    include_package_data=True,
    package_data={
        "": ["*.json"],
    },
    author="kubbur.digital",
    author_email="unrepie@kubbur.digital",
    description="A tool to manage an Unraid server from a Raspberry Pi with a relay hat.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kubbur/unrepie",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
