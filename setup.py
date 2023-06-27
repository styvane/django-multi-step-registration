import sys

from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand

from registration import get_version


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    package_dir={"registration": "registration"},
    packages=find_packages(exclude="test_app"),
    tests_require=["pytest-django"],
    cmdclass={"test": PyTest},
    include_package_data=True,
)
