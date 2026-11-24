"""CountLens localhost server with an optional Ultralytics YOLO endpoint."""
import base64
from collections import Counter
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
import webbrowser

ROOT = Path(__file__).resolve().parent
MODEL = None
MODEL_LOCK = threading.Lock()


def detect_image(payload):
    global MODEL
    import cv2
    import numpy as np
    from ultralytics import YOLO

    cutoff = float(payload.get('confidence', 0.55))
    if not 0.01 <= cutoff <= 1:
        raise ValueError('Confidence must be between 0.01 and 1.00.')
    encoded = payload.get('image', '')
    if not isinstance(encoded, str) or not encoded.startswith('data:image/png;base64,'):
        raise ValueError('Send a PNG image.')
    raw = base64.b64decode(encoded.split(',', 1)[1], validate=True)
    image = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError('Could not decode the image.')
    if image.shape[0] * image.shape[1] > 8_000_000:
        raise ValueError('Use an image with at most 8 million pixels.')
    with MODEL_LOCK:
        if MODEL is None:
            MODEL = YOLO(str(ROOT / 'yolo11n.pt'))
        result = MODEL.predict(source=image, conf=cutoff, imgsz=int(os.environ.get("YOLO_IMGSZ", "1280")), verbose=False)[0]
        marked = result.plot()
        counts = Counter()
        detections = []
        for box in result.boxes:
            label = result.names[int(box.cls.item())]
            counts[label] += 1
            detections.append({'label': label, 'confidence': float(box.conf.item())})
        success, png = cv2.imencode('.png', marked)
        if not success:
            raise RuntimeError('Could not encode the result.')
    return {'image': 'data:image/png;base64,' + base64.b64encode(png).decode(),
            'counts': dict(counts), 'total': sum(counts.values()), 'detections': detections}


class Handler(SimpleHTTPRequestHandler):
    def json_response(self, code, body):
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        if self.path != '/api/detect':
            self.json_response(404, {'error': 'Unknown endpoint.'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 35_000_000:
                self.json_response(413, {'error': 'Image request is too large or empty.'})
                return
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError('Expected an image request.')
            self.json_response(200, detect_image(payload))
        except ImportError:
            self.json_response(503, {'error': 'YOLO dependencies are missing. Install ultralytics using the same Python used to start this server, then restart.'})
        except (ValueError, TypeError) as error:
            self.json_response(400, {'error': str(error)})
        except Exception as error:
            self.json_response(500, {'error': 'Detection failed: ' + str(error)})


def main():
    handler = partial(Handler, directory=str(ROOT / 'static'))
    try:
        server = ThreadingHTTPServer(('127.0.0.1', 8000), handler)
    except OSError as error:
        print(f'Could not start CountLens on port 8000: {error}')
        print('Close the previous server, then try again.')
        return
    print('CountLens is running at http://localhost:8000')
    print('Keep this window open. Press Ctrl+C to stop.')
    webbrowser.open('http://localhost:8000')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nCountLens stopped.')
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
