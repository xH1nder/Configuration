@echo off
echo Test good script
python src\main.py --script start_good.txt
echo Test bad script, must stop on error
python src\main.py --script start_bad.txt
echo Test missing script, must show error
python src\main.py --script no_file.txt
echo Done
