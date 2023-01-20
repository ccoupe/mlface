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

$ nvidia-docker build -t ccoupe:mlface .

$ nvidia-docker run -dp 4785:4785 -v /home/ccoupe/Projects/mlface/known_faces:/known_faces \
--name=mlface ccoupe:mlface

     OR
     
$ nvidia-docker run -dp 4785:4785 --mount source=known_faces,target=/known_faces --name=mlface ccoupe:mlface

if you like your volume in /var/lib/docker/volumes/ - I don't because it
should be accessable to a user account, not just root.
