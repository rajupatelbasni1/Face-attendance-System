# Face Attendance System (Django + InsightFace)

**Contents**
- Django app `face_app` with models and views
- Browser-based capture (HTML + JS) that posts an image to Django to register a face
- Streaming recognition endpoint that serves MJPEG frames with detected names
- `capture_insight.py` and `recognize_insight.py` scripts (standalone) using InsightFace
- Static CSS for a minimal nice UI

**Quick start (macOS / Linux)**
1. Create & activate a Python 3.10+ virtualenv:
   ```
   python3.10 -m venv env
   source env/bin/activate
   ```
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
3. Run Django migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Start Django server:
   ```
   python manage.py runserver
   ```
   - Visit `http://127.0.0.1:8000/capture/` to capture faces from browser.
   - Visit `http://127.0.0.1:8000/recognize/` to view live recognition stream.

**Notes**
- On macOS, the camera backend `cv2.CAP_AVFOUNDATION` is used in sample scripts; if it fails, change to `cv2.VideoCapture(0)`.
- InsightFace downloads models the first time; keep internet on for initial run.
- If you want to run capture/recognize scripts directly, activate the same env and run:
  ```
  python capture_insight.py
  python recognize_insight.py
  ```
# Face-attendance-System
# Face-attendance-System-DYP-DPGU
