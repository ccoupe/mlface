#!/bin/bash
source /home/ccoupe/.bashrc
source /usr/local/bin/virtualenvwrapper.sh
cd /usr/local/lib/mlface/
workon py3
echo 'Any error will be apparent'
echo 'Bronco.local:'
python3 test.py --host 192.168.1.2
echo 'Stoic.local:'
python3 test.py --host stoic.local
echo 'Mini.local:'
python3 test.py --host mini.local
