# 
# test.py 
#   trys a known picture and an unknown picture
#   against the websocker. 
import sys
import websocket  # pip3 install websocket-client
import base64
import json
import argparse

def get_name(uri, bfr):
  ws = websocket.WebSocket()
  ws.connect(uri, timeout=10)
  ws.send(base64.b64encode(bfr))
  reply = ws.recv()
  ws.close()
  return reply
  
def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("-p", "--port", action='store', type=int, default='4785',
      nargs='?', help="server port number, 4785 is default")
  ap.add_argument("--host", action='store', type=str, default='192.168.1.2',
      nargs='?', help="host ip number, 192.168.1.2 is default")
  
  args = vars(ap.parse_args())
  
  uri = f"ws://{args['host']}:{args['port']}"
  
  fp = './known_faces/cecil/13.jpg'
  f = open(fp, 'rb')
  img = f.read()
  f.close()
  rp = json.loads(get_name(uri, img))
  #print(rp)
  det = rp['details']
  #print('Details',det)
  found = False
  for mat in det['matrices']:
      #print('Mat', mat)
      #print("IsCecil", mat['tag'])
      if mat['tag'] == 'cecil':
        found = True
  if not found:
    print(f"FAILED known {rp['details']['time']} secs")
  else:
    print(f"Known : {rp['details']['time']} secs")

  fp = './unknown.jpg'
  f = open(fp, 'rb')
  img = f.read()
  f.close()
  rp = json.loads(get_name(uri, img))
  print(f"Unknown : {rp['details']['time']} secs")


if __name__ == '__main__':
  sys.exit(main())
