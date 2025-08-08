@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Starting License Maker...
python license_maker_gui.py

pause 