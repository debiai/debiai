#!/bin/bash

# Remove previous build and dist directories
rm -rf build dist backend.egg-info

# Generated source distribution and wheel distribution
python3 setup.py sdist bdist_wheel

# Install the package
pip install .

# Run the package
debiai-start
