pip install -r requirements.txt
pyinstaller --clean main.spec

mv dist/*.exe .
rm -fr dist build
