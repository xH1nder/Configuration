@echo off
echo Test minimal VFS
python src\main.py --vfs vfs_min.json --log log_vfs1.xml --script start_vfs.txt
echo Test small VFS
python src\main.py --vfs vfs_small.json --log log_vfs2.xml --script start_vfs.txt
echo Test deep VFS, 3 levels
python src\main.py --vfs vfs_deep.json --log log_vfs3.xml --script start_vfs.txt
echo Test bad VFS, must show error
python src\main.py --vfs vfs_bad.json --log log_vfs4.xml --script start_vfs.txt
echo Test missing VFS, must show error
python src\main.py --vfs no_such.json --log log_vfs5.xml --script start_vfs.txt
echo Done
