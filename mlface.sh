#!/bin/bash
#source ~/anaconda3/etc/profile.d/conda.sh
#eval "$(conda shell.bash hook)"
#conda activate py3
source `which virtualenvwrapper.sh`
workon py3
cd /usr/local/lib/mlface
/usr/bin/python3 mlface.py -s
