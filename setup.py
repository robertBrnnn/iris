from setuptools import setup, find_packages
from setuptools.command.install import install
from pip.req import parse_requirements
from os.path import normpath, join, abspath, dirname, expanduser, exists
from os import getcwd, sep, pardir, makedirs
from shutil import copyfile
import os
import stat

base = getcwd()
install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="Iris-Mail-Client",
    version="0.2",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={'': ['static/*', 'iris.ini', 'storage.txt']},
    install_requires=reqs,
    include_package_data=True,
    author="Robert J. Brennan",
    author_email="robert.brnnn@gmail.com",
    description="Iris email client...",
    license="GPL-3.0",
    data_files=[('/usr/share/applications', ['conf/iris.desktop', ]),
                ('/usr/share/pixmaps', ['conf/iris.png', ])],
    classifiers={
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Office/Business',
    },
    entry_points={
        'console_scripts': [
            'iris = iris.__main__:main',
        ],
        'gui_scripts': [
            'iris = iris.__main__:main',
        ]
    },
)
