@echo off
echo Test log only
python src\main.py --log log1.xml
echo Test log + good script
python src\main.py --log log2.xml --script start_good.txt
echo Done
