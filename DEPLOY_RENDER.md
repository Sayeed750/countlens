# Deploy CountLens on Render

This folder supports localhost and Render. It has not been deployed yet.

## Upload to GitHub

1. Extract the ZIP.
2. Create a GitHub repository named `countlens-web`.
3. Upload the CONTENTS of this folder to the repository root. Dockerfile, app.py,
   requirements.txt, render.yaml and the static folder must be at the top level.
4. Never upload your virtual environment or personal images.

## Deploy on Render

1. Sign in at https://dashboard.render.com/ and connect your GitHub account.
2. Choose New > Blueprint and select the repository.
3. Render reads render.yaml. Review the Free plan and create the service.
4. Wait for the Docker build and deployment to succeed.
5. Open the actual onrender.com URL shown by Render and share it with your teacher.

Alternative: New > Web Service, select the same repository, choose Docker,
use Dockerfile at the repository root, select Free, and set the health check to
/healthz. Leave Docker Command blank: the Dockerfile supplies the command.
Set YOLO_IMGSZ to 640 to use the deployment's reduced detection image size.

## What the deployment includes

- Flask serves the pages and /api/detect.
- Gunicorn listens on Render's PORT on 0.0.0.0.
- CPU-only PyTorch is installed before Ultralytics.
- The Docker build downloads yolo11n.pt once into the container image.
- One model worker serializes predictions. Concurrent detection requests receive
  a busy message; other page requests remain available.
- /healthz checks that the web server is alive; it does not run model inference.
- Photo edits happen in the browser. Object detection sends the photo to your
  Render service. The application does not save submitted photos to disk.

## Free-plan limits

The free service sleeps after 15 minutes without traffic, and opening it again
can take about a minute. It has 512 MB RAM. YOLO with PyTorch may exceed this:
free hosting is NOT a guarantee that inference will succeed. If logs show
out-of-memory or exit 137, use a larger instance or deploy detection separately.
Choose a paid plan only if you want its charges. The rest of the editor can
work while model inference is unavailable. Test detection before a presentation.

## Run locally as before

Run run_server.py with your existing Python environment. It still opens
http://localhost:8000 and uses the original 1280 detection size by default.
The Render Docker build does not run on your laptop unless you choose to use Docker.

## Files

app.py: Render Flask entrypoint.
run_server.py: localhost launcher and shared YOLO implementation.
Dockerfile: production dependencies and Gunicorn command.
requirements.txt: Python application dependencies.
render.yaml: Render service configuration.
static/: HTML, CSS and JavaScript interface.
