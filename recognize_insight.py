import os, django, json, time
import cv2, numpy as np
import insightface
from numpy.linalg import norm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "face_attendance.settings")
django.setup()

from face_app.models import Student

app = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0)

def cosine_sim(a,b):
    return np.dot(a,b)/(norm(a)*norm(b)+1e-10)

students = Student.objects.exclude(embedding__isnull=True).exclude(embedding__exact='')
known_emb = [np.array(json.loads(s.embedding),dtype=np.float32) for s in students]
known_names = [s.name for s in students]
print('Loaded:', known_names)

cap = cv2.VideoCapture(2, cv2.CAP_AVFOUNDATION)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    small = cv2.resize(frame,(0,0),fx=0.6,fy=0.6)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    faces = app.get(rgb)
    for face in faces:
        x1,y1,x2,y2 = face.bbox.astype(int)
        # scale to full frame
        x1 = int(x1/0.6); y1=int(y1/0.6); x2=int(x2/0.6); y2=int(y2/0.6)
        emb = face.embedding.astype(np.float32)
        name='Unknown'
        if len(known_emb)>0:
            sims=[cosine_sim(emb,k) for k in known_emb]
            idx=int(np.argmax(sims))
            if sims[idx]>0.5:
                name=known_names[idx]
        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
        cv2.putText(frame,name,(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)
    cv2.imshow('Recognize',frame)
    if cv2.waitKey(1)&0xFF==ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
