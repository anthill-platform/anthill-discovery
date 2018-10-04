
from setuptools import setup, find_packages

DEPENDENCIES = [
    "anthill-common"
]

setup(
    name='anthill-discovery',
    package_data={
      "anthill.discovery": ["anthill/discovery/sql", "anthill/discovery/static"]
    },
    setup_requires=["pypigit-version"],
    git_version="0.1.0",
    description='A dynamic server discovery service for Anthill platform',
    author='desertkun',
    license='MIT',
    author_email='desertkun@gmail.com',
    url='https://github.com/anthill-platform/anthill-discovery',
    namespace_packages=["anthill"],
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    install_requires=DEPENDENCIES
)
