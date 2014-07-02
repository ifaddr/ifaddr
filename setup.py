from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name = 'ifaddr',
    version = '0.1.0',
    description='Enumerates all IP addresses on all network adapters of the system.',
    long_description=long_description,
    author='Stefan C. Mueller',
    author_email='stefan.mueller@fhnw.ch',
    url='https://github.com/smurn/ifaddr',
    packages = find_packages(),
    install_requires = ['ipaddress'],
)
