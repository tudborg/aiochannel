
#
# Stolen from Falcon (falconframework.org)
#
import imp
import io
from os import path
from setuptools import setup, find_packages

ROOT_DIR = path.abspath(path.dirname(__file__))

SRC_DIR = path.join(ROOT_DIR, 'aiochannel')
VERSION = imp.load_source('version', path.join(SRC_DIR, 'version.py'))
VERSION = VERSION.__version__
README = path.join(ROOT_DIR, 'README.md')

REQUIRES = []

try:
    from pypandoc import convert

    def read_md(f):
        return convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")

    def read_md(f):
        return io.open(README, 'r', encoding='utf-8').read()

LONG_DESCRIPTION = read_md(README)

packages = find_packages(exclude=['tests'])

setup(
    name='aiochannel',
    version=VERSION,
    description='asyncio Channels (closable queues) inspired by golang',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='asyncio aio chan channel gochan',
    author='Henrik Tudborg',
    author_email='henrik@tud.org',
    url='github.com/tbug/aiochannel',
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRES,
    setup_requires=[],
    license='Apache 2.0'
)
