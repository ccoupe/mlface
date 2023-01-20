#!/bin/bash
# 
# nvidia-docker run -dp 4785:4785 --mount source=known_faces,target=/known_faces --name=mlface ccoupe:mlface
#
cd /usr/local/lib/mlface
/usr/bin/python3 mlface.py --dir=/known_faces
