cmake `
    -S .\algorithm\ `
    -B .\algorithm\build `
    -G "Ninja"

cmake --build .\algorithm\build

python -m venv .\gui\.venv
.\gui\.venv\Scripts\Activate.ps1
pip install -r .\gui\requirements.txt