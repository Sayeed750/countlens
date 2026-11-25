"""Production WSGI entrypoint: gunicorn app:app."""
from pathlib import Path
import logging
import threading
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from run_server import detect_image

ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(ROOT / 'static'), static_url_path='/static')
app.config['MAX_CONTENT_LENGTH'] = 35_000_000
inference_slot = threading.Lock()


@app.get('/')
def home():
    return app.send_static_file('index.html')


@app.get('/app.js')
def javascript():
    return app.send_static_file('app.js')


@app.get('/chapter-algorithms.js')
def chapter_algorithms():
    return app.send_static_file('chapter-algorithms.js')


@app.get('/chapters.js')
def chapters_javascript():
    return app.send_static_file('chapters.js')


@app.get('/style.css')
def stylesheet():
    return app.send_static_file('style.css')


@app.get('/healthz')
def health():
    return jsonify(status='ok')


@app.post('/api/detect')
def detect():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error='Expected a JSON image request.'), 400
    if not inference_slot.acquire(blocking=False):
        return jsonify(error='Another detection is running. Please try again shortly.'), 429
    try:
        return jsonify(detect_image(payload))
    except (ValueError, TypeError) as error:
        return jsonify(error=str(error)), 400
    except ImportError:
        return jsonify(error='Detection dependencies are unavailable on the server.'), 503
    except Exception:
        logging.exception('Object detection failed')
        return jsonify(error='Detection failed. Try a smaller photo or check the server logs.'), 500
    finally:
        inference_slot.release()


@app.errorhandler(HTTPException)
def http_error(error):
    return jsonify(error=error.description), error.code
