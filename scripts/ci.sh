#!/bin/bash

# Simple CI script: run style & type checks for the repository
# - Runs pycodestyle but ignores the "line too long" error (E501)
# - Runs mypy for static type checks
# Usage: run from repository root: `./scripts/ci.sh`

ERR=0

echo "Running pycodestyle ..."
python -m pycodestyle \
	--ignore=E501 \
	--show-source --statistics \
	--exclude=.venv,.venv_x64,flicker/assets/resources_rc.py \
	.

if [ $? -ne 0 ]; then
	ERR=1
fi

echo "Running mypy type checks ..."
python -m mypy --exclude "\.venv|.venv_x64|flicker/assets/resources_rc\.py" .
if [ $? -ne 0 ]; then
	ERR=1
fi

if [ $ERR -eq 0 ]; then
	echo "All checks passed."
	exit 0
else
	echo "One or more checks failed."
	echo "If tools are missing, install with: \`python -m pip install pycodestyle mypy\`"
	exit 1
fi
