# mlface_mps.py
#
# websocket server on port 4785, receives an image (containing a face)
# matches the face(s) in the image to some 'known' faces using PyTorch and MPS (Metal Performance Shaders) on Apple Silicon
# returns a json with match values
#
import sys
import json
import argparse
from datetime import datetime
import asyncio
import websockets
import os
import logging
import base64
import torch
import numpy as np
from PIL import Image
import io
from facenet_pytorch import MTCNN, InceptionResnetV1

# Globals
log = None
mtcnn = None
resnet = None
known_faces_dir = ''
known_embeddings = []
known_names = []

# Initialize PyTorch to use Apple Silicon GPU (MPS)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

def init_models():
    global log, known_embeddings, known_names, known_faces_dir, mtcnn, resnet
    log.info(f"Loading reference models on {device}...")
    
    # MTCNN for face detection/alignment, InceptionResnetV1 for embedding extraction
    # Due to MPS adaptive pool issue in PyTorch's interpolate(mode='area'), MTCNN must run on CPU
    # By increasing min_face_size from 20 to 40, we skip processing the largest image pyramids for huge speedup
    mtcnn = MTCNN(keep_all=True, device='cpu', min_face_size=40)
    
    # InceptionResnetV1 runs fine on MPS, and we use FP16 for extra speed
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device).half()
    
    log.info(f"Scanning known faces from directory: {known_faces_dir}")
    if not os.path.exists(known_faces_dir):
        log.warning(f"Directory {known_faces_dir} does not exist!")
        return

    for name in os.listdir(known_faces_dir):
        name_dir = os.path.join(known_faces_dir, name)
        if not os.path.isdir(name_dir):
            continue
            
        for filename in os.listdir(name_dir):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                continue
                
            fp = os.path.join(name_dir, filename)
            log.info(f'Processing reference image: {name}/{filename}')
            try:
                img = Image.open(fp).convert('RGB')
                # Extract face tensor and move to device
                face_tensor = mtcnn(img)
                if face_tensor is not None:
                    # face_tensor has shape [num_faces, 3, 160, 160] or [3, 160, 160]
                    # Ensure batch dimension
                    if face_tensor.dim() == 3:
                        face_tensor = face_tensor.unsqueeze(0)
                        
                    # Calculate reference 512-dim embedding on M2 GPU
                    embedding = resnet(face_tensor.to(device).half()).detach().cpu().numpy()[0]
                    known_embeddings.append(embedding)
                    known_names.append(name)
                else:
                    log.warning(f"Could not find face in {name}/{filename}")
            except Exception as e:
                log.error(f"Error loading face from {fp}: {e}")

def compare_embeddings(embedding, tolerance=0.6):
    global known_embeddings, known_names
    if not known_embeddings:
        return "Unknown", 0.0
        
    # Compute L2 distance to all reference embeddings
    distances = np.linalg.norm(np.array(known_embeddings) - embedding, axis=1)
    min_idx = np.argmin(distances)
    min_dist = distances[min_idx]
    
    # Map L2 distance roughly to a confidence metric
    confidence = max(0.0, 1.0 - (min_dist / 2.0))
    
    if min_dist <= tolerance:
        return known_names[min_idx], confidence
    return "Unknown", confidence

async def wss_on_message(ws):
    global log, mtcnn, resnet
    message = await ws.recv()
    start_time = datetime.now()
    
    try:
        # Load and decode base64 input image
        image_bytes = base64.b64decode(message)
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img_width, img_height = img.size
        
        # 1. Detect faces using CPU (MPS workaround)
        # We downscale large images purely for the detection phase to speed it up significantly
        scale = min(320.0 / max(img_width, img_height), 1.0)
        if scale < 1.0:
            detect_img = img.resize((int(img_width * scale), int(img_height * scale)), Image.Resampling.BILINEAR)
        else:
            detect_img = img
            
        boxes, probs = mtcnn.detect(detect_img)
        
        mats = []
        if boxes is not None:
            # Scale boxes back to original image size
            if scale < 1.0:
                boxes = boxes / scale
                
            # 2. Extract face embeddings without re-detecting
            faces = mtcnn.extract(img, boxes, None)
            if faces is not None:
                if faces.dim() == 3:
                    faces = faces.unsqueeze(0)
                
                # Forward pass on M2 GPU with FP16
                embeddings = resnet(faces.to(device).half()).detach().cpu().numpy()
                
                for box, prob, embedding in zip(boxes, probs, embeddings):
                    # Find closest match in the database
                    name, confidence = compare_embeddings(embedding)
                    
                    m = {
                        'x': int(box[0]), 'y': int(box[1]),
                        'width': int(box[2] - box[0]), 'height': int(box[3] - box[1]),
                        'tag': name, 'confidence': float(confidence)
                    }
                    mats.append(m)
        
        end_time = datetime.now()
        et = (end_time - start_time).total_seconds()
        
        dt = {
            "details": {
                'plug': 'face_mps', 'name': 'face', 'reason': 'face',
                'matrices': mats, 'imgWidth': img_width, 'imgHeight': img_height,
                'time': et
            }
        }
        
        if len(mats) > 0:
            log.info(f"Found {len(mats)} face(s), took: {et:.4f} secs")
        else:
            log.info(f"No face detected, took: {et:.4f} secs")
            
        await ws.send(json.dumps(dt))
        
    except Exception as e:
        log.error(f"Error processing websocket message: {e}")
        await ws.send(json.dumps({"error": str(e)}))

async def start_server(port):
    async with websockets.serve(wss_on_message, "0.0.0.0", port):
        await asyncio.Future()  # run forever

def main():
    global log, known_faces_dir
    
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", action='store', type=int, default=4785,
                    help="server port number, 4785 is default")
    ap.add_argument("-d", "--dir", type=str, default="./known_faces/",
                    help="path to directory of known faces")
    args = vars(ap.parse_args())
    
    # Configure Logging
    logging.basicConfig(level=logging.INFO, datefmt="%H:%M:%S", format='%(asctime)s %(levelname)-5s %(message)s')
    log = logging.getLogger('mlface_mps')
    
    known_faces_dir = args['dir']
    init_models()
    
    # Start Websocket Server
    log.info(f"PyTorch MPS Websocket server starting on port {args['port']}...")
    asyncio.run(start_server(args['port']))

if __name__ == '__main__':
    sys.exit(main())
