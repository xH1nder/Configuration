@echo off
echo Test all params together
python src\main.py --vfs vfs.json --log log_all.xml --script start_good.txt
echo Test short form with =
python src\main.py --vfs=vfs.json --log=log_all2.xml --script=start_bad.txt
echo Done
