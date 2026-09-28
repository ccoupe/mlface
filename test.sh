#!/bin/bash
source /home/ccoupe/.bashrc
source /usr/local/bin/virtualenvwrapper.sh
cd /usr/local/lib/mlface/
workon py3
echo 'Any error will be apparent'
echo 'Bronco.local:'
python3 test.py --host 192.168.1.2
echo 'Bigboy.local:'
python3 test.py --host bigboy.local
# echo 'asahi.local:'
# python3 test.py --host asahi.local
#echo 'mini2.local:'
#python3 test.py --host mini2.local
echo 'nassy.allhat.org:'
python3 test.py --host nassy
