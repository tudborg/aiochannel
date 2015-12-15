
#
# Stolen from Falcon (falconframework.org)
#
import imp
import io
import os
from os import path
from setuptools import setup, find_packages

MYDIR = path.abspath(os.path.dirname(__file__))

VERSION = imp.load_source('version', path.join('.', 'aiochannel', 'version.py'))
VERSION = VERSION.__version__

REQUIRES = []

LONG_DESCRIPTION = io.open(os.path.join(MYDIR, 'README.md'), 'r', encoding='utf-8').read()

setup(
    name='aiochannel',
    version=VERSION,
    description='',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='asyncio aio chan channel gochan',
    author='Henrik Tudborg',
    author_email='henrik@tud.org',
    url='github.com/tbug/aiochannel',
    packages=find_packages(exclude=['test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRES,
    setup_requires=[]
)
