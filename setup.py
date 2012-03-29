# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 by Enrique Pérez Arnaud <enriquepablo@gmail.com>
#
# This file is part of nlproject.
#
# The nlproject is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The nlproject is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with any part of the nlproject.
# If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

setup(
    name = "nl",
    version = "0.102",
    url = 'http://http://enriquepablo.github.com/nlproject/',
    license = 'GPL',
    description = "A python library that provides a production system with an API modelled on the natural language",
    author = 'Enrique Perez Arnaud',
    author_email = 'enriquepablo@gmail.com',
    packages = find_packages('.'),
    package_dir = {'': '.'},
    classifiers = [
                   "Topic :: Scientific/Engineering :: Artificial Intelligence",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules"
                  ],
    zip_safe = False,
    dependency_links = [
    ],
    install_requires = ['setuptools>=0.6c11',
                        'python-daemon',
                        'ply',],
    entry_points = {
          'console_scripts': ['npldaemon = nl.npldaemon:main',
                              'nlpy = nl.nlpy:main'],
          },
#        'console_scripts':
#            [ 'plot_ph22 = nl.examples.physics22:plotPh22', ],
)
