@echo off
echo Test stage5 good flow
python src\main.py --vfs vfs_stage5.json --log log_stage5.xml --script start_stage5.txt
echo Test stage5 errors
python src\main.py --vfs vfs_stage5.json --script start_bad.txt
echo Done
