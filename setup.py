from setuptools import setup, find_packages

import ciprs_reader

import site
import sys
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

setup(name="ciprs_reader", version=ciprs_reader.VERSION, packages=find_packages())
