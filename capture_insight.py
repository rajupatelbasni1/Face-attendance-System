import os, django, json
import cv2, numpy as np
import insightface

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "face_attendance.settings")
django.setup()

from face_app.models import Student

print("Loading InsightFace...")
app = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0)

def main():
    name = input("Enter student name: ").strip() or None
    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print('Press c to capture, q to quit')
    saved_emb = None
    saved_crop = None
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        cv2.imshow('Capture', frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('c'):
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = app.get(rgb)
            if not faces:
                print('No face detected, try again')
                continue
            emb = faces[0].embedding.astype(float).tolist()
            x1,y1,x2,y2 = faces[0].bbox.astype(int)
            h,w = frame.shape[:2]
            x1,y1 = max(0,x1), max(0,y1)
            x2,y2 = min(w,x2), min(h,y2)
            crop = frame[y1:y2, x1:x2].copy()
            saved_emb = emb
            saved_crop = crop
            print('Face captured')
            break
        elif k == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    if saved_emb is None:
        print('No face saved')
        return
    s = Student.objects.create(name=name or f'Student_{Student.objects.count()+1}', embedding=json.dumps(saved_emb))
    os.makedirs('media/faces', exist_ok=True)
    fname = f'face_{s.id}.jpg'
    cv2.imwrite(os.path.join('media','faces',fname), saved_crop)
    s.face_image = f'faces/{fname}'
    s.save()
    print('Saved', s.id)

if __name__ == '__main__':
    main()
