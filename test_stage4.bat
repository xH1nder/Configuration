@echo off
echo Test stage4 with deep VFS
python src\main.py --vfs vfs_deep.json --log log_stage4.xml --script start_stage4.txt
echo Test errors on stage4
python src\main.py --vfs vfs_deep.json --script start_bad.txt
echo Done
