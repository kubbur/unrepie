from setuptools import setup, find_packages

setup(
    name='unrepie',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask==2.0.1',
        'Werkzeug==2.0.1',
        'paramiko==2.7.2',
        'ping3==3.0.0',
        'six==1.16.0'
    ],
    entry_points={
        'console_scripts': [
            'unrepie=main:run'
        ]
    }
)
