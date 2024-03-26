from setuptools import find_packages, setup

setup(
    name='pyircsdk',
    packages=find_packages(include=['pyircsdk', 'event']),
    version='0.0.1',
    description='pyIRCSDK is a Python library for creating IRC bots and clients. It is designed to provide granular access to raw mesages and to provide an event emitter like interface for handling messages.',
    author='Bludot',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)