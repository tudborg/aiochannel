#!/usr/bin/env bash
# I stole this from falcon (falconframework.org)
find $1 \( -name '*.c' -or -name '*.so' -or -name '*.pyc' \) -delete
