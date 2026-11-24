COUNTLENS WEB — LOCALHOST VERSION

Start from Command Prompt in this folder:
"C:\Users\Sayeed\spyder-cv2\Scripts\python.exe" run_server.py

Open http://localhost:8000 and keep the terminal open.
After updating files, stop the old server with Ctrl+C, restart and press Ctrl+F5.

OBJECT DETECTION
One-time dependency installation (Command Prompt):
"C:\Users\Sayeed\spyder-cv2\Scripts\python.exe" -m pip install ultralytics

Your existing Spyder environment may already have this installed.
Copy your existing yolo11n.pt beside run_server.py to reuse it.
Otherwise the first detection downloads the model (internet required).
Other tools work without YOLO dependencies.
The pretrained model supports a fixed set of classes; it may miss or mislabel objects.
