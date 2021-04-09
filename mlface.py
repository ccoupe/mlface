# 
#
# websocket server on port 4785, recieves an jpg image
# matches the face(s) in the image to some 'known' faces
# returns a json with match values
#
import sys
import json
import argparse
import warnings
from datetime import datetime
import time, threading, sched
import socket
import os
#from lib.Settings import Settings
#from lib.Constants import State, Event
import logging
import logging.handlers
import asyncio
import websockets
#import websocket
import cv2
import numpy as np
import face_recognition
import os.path
import pwd
import grp
import base64	

# Globals
settings = None
applog = None
isPi = False
muted = False
five_min_thread = None
debug = False;

KNOWN_FACES_DIR = '/usr/local/lib/mlface/known_faces'
UNKNOWN_FACES_DIR = '/usr/local/lib/mlface/unknown_faces'
TOLERANCE = 0.6
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = 'cnn'  # default: 'hog', other one can be 'cnn' - CUDA accelerated (if available) deep-learning pretrained model
known_faces = []
known_names = []

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def init_models():
  # We oranize known faces as subfolders of KNOWN_FACES_DIR
  # Each subfolder's name becomes our label (name)
  global log, known_faces, known_names
  for name in os.listdir(KNOWN_FACES_DIR):
  
    # Next we load every file of faces of known person
    for filename in os.listdir(f'{KNOWN_FACES_DIR}/{name}'):
      log.info('working on {}/{}'.format(name,filename))
      # Load an image
      image = face_recognition.load_image_file(f'{KNOWN_FACES_DIR}/{name}/{filename}')
        
      # Get 128-dimension face encoding
      # Always returns a list of found faces, for this purpose we take first face only (assuming one face per image as you can't be twice on one image)
      try:
        encoding = face_recognition.face_encodings(image)[0]
        
        # Append encodings and name
        known_faces.append(encoding)
        known_names.append(name)
      except:
        log.info(f"can't find a face in {name}/{filename}")
      
def update_models(name, image):
  global log, known_faces, known_names
  td = f'{KNOWN_FACES_DIR}/{name}' 
  if not os.path.exists(td):
    os.mkdir(td)
  fp = f'{td}/{name}.jpg'
  f = open(fp, 'wb')
  f.write(image)
  f.close()
  # we are root, change the file ownership 
  uid = pwd.getpwnam("ccoupe").pw_uid
  gid = grp.getgrnam("root").gr_gid
  os.chown(fp, uid, gid)
  os.chmod(fp, 0o664)
  log.info(f'created {fp}')
  img = face_recognition.load_image_file(fp)
  try:
    encoding = face_recognition.face_encodings(img)[0]
    # Append encodings and name
    known_faces.append(encoding)
    known_names.append(name)
    log.info(f'updated running models')
  except:
    log.info(f'is there a face in {fp}')

  
  
def long_timer_fired():
  global five_min_thread
  #mycroft_mute_status()
  #five_min_thread = threading.Timer(5 * 60, long_timer_fired)
  #five_min_thread.start()
  exit()

def five_min_timer():
  global five_min_thread
  print('creating long timer')
  five_min_thread = threading.Timer(1.5 * 60, long_timer_fired)
  five_min_thread.start()
    
# ---- websocket server - send payload to mqtt ../reply/set
  
async def wss_on_message(ws, path):
  global hmqtt, settings, log
  #log.info(f'wake up {path}')
  message = await ws.recv()
  start_time = datetime.now()
  imageBytes = base64.b64decode(message)
  # get the image sent to us. Send it thru the matcher, 
  # TODO: write to memory chunk instead of file
  o = open("/tmp/face.jpg","wb")
  o.write(imageBytes)
  o.close()
  image = face_recognition.load_image_file("/tmp/face.jpg")
  img_width = image.shape[1]
  img_height = image.shape[0]
  # This time we first grab face locations - we'll need them to draw boxes
  locations = face_recognition.face_locations(image, model=MODEL)
  
  # Now since we know loctions, we can pass them to face_encodings as second argument
  # Without that it will search for faces once again slowing down whole process
  encodings = face_recognition.face_encodings(image, locations)
  
  # We passed our image through face_locations and face_encodings, so we can modify it
  # First we need to convert it from RGB to BGR as we are going to work with cv2
  image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
  
  # But this time we assume that there might be more faces in an image - we can find faces of different people
  mats = []
  nm = None
  for face_encoding, face_location in zip(encodings, locations):
    
    # We use compare_faces (but might use face_distance as well)
    # Returns array of True/False values in order of passed known_faces
    results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
    
    # Since order is being preserved, we check if any face was found then grab index
    # then label (name) of first matching known face withing a tolerance
    
    # TODO test with multiple known faces. Good luck getting that.
    if True in results: 
      if nm is None: 
        nm = known_names[results.index(True)]
      m = {'x': face_location[0], 'y': face_location[1], 
            'width': face_location[2], 'height': face_location[3],
            'tag': nm, 'confidence': 1.00}
      #log.info(f'image has {nm} from {face_location}')
      mats.append(m)
  

  # locations is an array of tuples (x,y,w,h probably)
  end_time = datetime.now()
  el = end_time - start_time
  et = el.total_seconds()

  #log.info(f'locations {locations}')
  dt = {"details": { 'plug': 'face', 'name': 'face', 'reason': 'face',
    'matrices': mats, 'imgWidth': img_width, 'imgHeight': img_height,
    'time' : et}
    }
  if len(encodings) > 0:
    log.info(f'found {nm} in image, took: {et}')
  else:
    log.info(f'no face for image, took: {et}')
  
  await ws.send(json.dumps(dt))

def wss_server_init(port):
  global wss_server, log
  #wss_server = websockets.serve(wss_on_message, '192.168.1.2', port)
  wss_server = websockets.serve(wss_on_message, get_ip(), port)

    
def main():
  global isPi, settings, log, wss_server
  # process cmdline arguments
  loglevels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
  ap = argparse.ArgumentParser()
  #ap.add_argument("-c", "--conf", required=True, type=str,
  #  help="path and name of the json configuration file")
  ap.add_argument("-p", "--port", action='store', type=int, default='4785',
  nargs='?', help="server port number, 4785 is default")
  ap.add_argument("-s", "--syslog", action = 'store_true',
    default=False, help="use syslog")
  args = vars(ap.parse_args())
  
  # logging setupd$
  # Note websockets is very chatty at DEBUG level. Sigh.
  log = logging.getLogger('mlface')
  if args['syslog']:
    log.setLevel(logging.INFO)
    handler = logging.handlers.SysLogHandler(address = '/dev/log')
    # formatter for syslog (no date/time or appname.
    formatter = logging.Formatter('%(name)s-%(levelname)-5s: %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
  else:
    logging.basicConfig(level=logging.INFO,datefmt="%H:%M:%S",format='%(asctime)s %(levelname)-5s %(message)s')
  
  isPi = os.uname()[4].startswith("arm")
  log.info('loading models')
  init_models()


  wss_server_init(args['port'])
  five_min_timer()
  asyncio.get_event_loop().run_until_complete(wss_server)
  asyncio.get_event_loop().run_forever()

  # do something magic to integrate the event loops? 
  while True:
    time.sleep(5)

if __name__ == '__main__':
  sys.exit(main())

