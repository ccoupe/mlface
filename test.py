# 
# test.py 
#   trys a known picture and an unknown picture
#   against the websocker. 
import sys
import websocket  # pip3 install websocket-client
import base64

def get_name(uri, bfr):
  ws = websocket.WebSocket()
  ws.connect(uri, timeout=10)
  ws.send(base64.b64encode(bfr))
  reply = ws.recv()
  ws.close()
  return reply
  
def main():
  # hardcoded for me and my machines and network.
  host = 'bronco.local'
  port = 4785
  uri = f'ws://{host}:{port}'
  fp = './known_faces/cecil/13.jpg'
  f = open(fp, 'rb')
  img = f.read()
  f.close()
  print("Known:")
  rp = get_name(uri, img)
  print(rp)

  fp = './unknown.jpg'
  f = open(fp, 'rb')
  img = f.read()
  f.close()
  print("Unknown:")
  rp = get_name(uri, img)
  print(rp)


if __name__ == '__main__':
  sys.exit(main())
