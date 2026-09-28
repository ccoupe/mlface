Mlface compares an image (containing a face) and compares it to a list of
known 'people' and returns the name of the person or 'None'.

mlface can be run as a Docker container or as a standalone, systemd managed
application. It listens on a websocket on port 4785. A base64 encoded jpg is sent to '/' path.
A json response is returned which contains the name if matched. A face enclosing 
rectangle is returned, assume there is a face.

{'details': {'plug': 'face', 'name': 'face', 'reason': 'face', 
  'matrices': [{'x': 64, 'y': 333, 'width': 132, 'height': 265,
   'tag': 'cecil', 'confidence': 1.0}], 
   'imgWidth': 640, 'imgHeight': 480, 'time': 0.041136}
}

Docker required the ccoupe:dlib image with requires the

# Bigboy is newest.
'''$ docker run -dp 4785:4785 -v /home/ccoupe/known_faces:/known_faces --runtime nvidia -e TZ=America/Boise --restart=always --name=mlface ccoupe/mlface
```

# Stoic is older and needs nvidia-docker 
$ nvidia-docker build --progress=plain -t ccoupe/mlface .
$ nvidia-docker run -dp 4785:4785 -v /home/ccoupe/Projects/known_faces:/known_faces -e TZ=America/Boise \
--name=mlface ccoupe/mlface

# Bronco is newer and just uses docker
$ docker build -t ccoupe/mlface --progress=plain .
$ docker run -dp 4785:4785 -v /home/ccoupe/Projects/known_faces:/known_faces --runtime nvidia -e TZ=America/Boise --restart=always --name=mlface ccoupe/mlface
#
# asahi
$ docker run -dp 4785:4785 -v /home/ccoupe/known_faces:/known_faces  -e TZ=America/Boise --restart=always --name=mlface fcrecog-arm64


known_faces/<name1>/<pic1>.jpg, known_faces/<name1>/<pic2>.jpg,,,
  known_faces/<name2>/<pic1>.jpg,,, 
  known_faces/<name3>/<pic1>.jpg,,,
