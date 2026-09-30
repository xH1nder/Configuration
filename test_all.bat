@echo off
echo Test all params together
python src\main.py --vfs vfs_deep.json --log log_all.xml --script start_good.txt
echo Test all params with bad script
python src\main.py --vfs vfs_deep.json --log log_all2.xml --script start_bad.txt
echo Done
