from setuptools import setup, find_packages
from __version__ import __version__

setup(
    name='w2u-cli',
    version=__version__,
    description='CLI client to control the watch2upload tool',
    url='https://github.com/davidfialho14/watch2upload_client',
    license='MIT',
    author='David Fialho',
    author_email='fialho.david@protonmail.com',

    packages=find_packages(),

    install_requires=[],
)
