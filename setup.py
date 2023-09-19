"""
Setup script to build the site_index.
"""

import re
import shutil
from setuptools import setup, find_packages

with open('version') as f:
    buff = f.read()
    version = re.search('(\d+\.\d+\.\d+)', buff).groups()[0]

with open('readme.md') as f:
    buff = f.read()
    description = buff.split('\n')[2].strip()
    long_description = buff.strip()

shutil.copyfile('./readme.md', 'pysiteindex/readme.md')

setup(
    name='pysiteindex'
    , version=version
    , description=description
    , author='Tod Haren'
    , author_email='tod.haren@gmail.com'
    , url='NA'
    , packages=find_packages()
    # , package_dir={'':'src'}
    , entry_points={
        'console_scripts' : ['pysi=pysiteindex.__main__:cli',]
        }
)