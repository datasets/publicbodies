from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='publicbodies.brfederal',
      version=version,
      description="Imports Brazilian federal government structure into publicbodies csv file",
      long_description="""\
A collection of scripts that load the Brazilian federal government organizational structure xml dump file into a csv file in the format used by publicbodies.org.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='government organizations publicbodies',
      author='Augusto Herrmann',
      author_email='augusto.herrmann@gmail.com',
      url='',
      license='GPL-3.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'lxml>=2.2.4',
          'nltk>=2.0b8s',
          'phonenumberslite>=6.1.0',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
