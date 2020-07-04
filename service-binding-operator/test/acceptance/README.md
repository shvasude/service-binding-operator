# How to execute the script

## This is called in prepare-env.sh under hack/check-python
pip install requirements.txt

## Use this make file command to check the test/acceptance python behave framework is a clean code
make check-code-style

## Use this command to run the test
behave -v --no-capture --no-capture-stderr test/acceptance/features/