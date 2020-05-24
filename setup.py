
from setuptools import setup, find_namespace_packages

DEPENDENCIES = [
    "anthill-common>=0.2.4"
]

setup(
    name='anthill-discovery',
    package_data={
      "anthill.discovery": ["anthill/discovery/sql", "anthill/discovery/static"]
    },
    version='0.2',
    description='A dynamic server discovery service for Anthill platform',
    author='desertkun',
    license='MIT',
    author_email='desertkun@gmail.com',
    url='https://github.com/anthill-platform/anthill-discovery',
    namespace_packages=["anthill"],
    include_package_data=True,
    packages=find_namespace_packages(include=["anthill.*"]),
    zip_safe=False,
    install_requires=DEPENDENCIES
)
