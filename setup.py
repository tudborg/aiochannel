import imp
from os import path
from setuptools import setup, find_packages

ROOT_DIR = path.abspath(path.dirname(__file__))

SRC_DIR = path.join(ROOT_DIR, 'aiochannel')
VERSION = imp.load_source('version', path.join(SRC_DIR, 'version.py'))
VERSION = VERSION.__version__
README = path.join(ROOT_DIR, 'README.rst')

REQUIRES = []

with open(README) as f:
    LONG_DESCRIPTION = f.read()

packages = find_packages(exclude=['tests'])

setup(
    name='aiochannel',
    version=VERSION,
    description='asyncio Channels (closable queues) inspired by golang',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords='asyncio aio chan channel gochan',
    author='Henrik Tudborg',
    author_email='henrik@tudb.org',
    url='https://github.com/tbug/aiochannel',
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRES,
    setup_requires=[],
    license='Apache 2.0'
)
