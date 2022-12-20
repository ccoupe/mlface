#!/bin/bash
export HOME=/Users/ccoupe/
export USER=ccoupe
source /Users/ccoupe/.bash_profile
cd /usr/local/lib/mlface
conda activate py38
python3 mlface.py
