# How to execute the script
pip install requirements.txt
behave -v -o "$(pwd)/bdd-report" --no-capture --no-capture-stderr test/acceptance/features/