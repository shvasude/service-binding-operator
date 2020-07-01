
directories=${directories:-"./test/acceptance/features"}

function prepare_venv() {
    python3 -m venv venv && source venv/bin/activate
    for req in $(find . -name 'requirements.txt'); do
        python3 "$(which pip3)" install -q -r $req;
    done
    python3 "$(which pip3)" install -q pydocstyle pyflakes vulture radon
}