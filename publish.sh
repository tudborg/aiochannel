#!/usr/bin/env bash



if [ -z "$username" ]; then
    read -p "PyPI User: " username
fi
if [ -z "$password" ]; then
    read -s -p "PyPI Pass: " password
fi

echo -e "
[distutils]
index-servers =
    pypi
[pypi]
repository=https://pypi.python.org/pypi
username:${username}
password:${password}
" > ~/.pypirc

#python setup.py bdist_egg upload
python setup.py sdist --formats=gztar,zip upload
# python setup.py bdist_wheel upload
