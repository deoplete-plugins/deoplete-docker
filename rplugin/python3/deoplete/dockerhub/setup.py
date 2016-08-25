#!/usr/bin/env python

import os

from setuptools import setup
import dockerhub

base = os.path.dirname(__file__)
fp = open(os.path.join(base, 'dockerhub', '__init__.py'))
fp.close()

setup(name='dockerhub',
      version='0.0.1.dev0',
      license='MIT',
      author='zchee aka Koichi Shiraishi',
      author_email='zchee@gmail.com',
      url='https://github.com/zchee/py-dockerhub',
      packages=['dockerhub'],
      )
