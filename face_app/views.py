import base64, json, cv2, numpy as np
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt

import insightface
from numpy.linalg import norm
import os
from collections import defaultdict
from .models import Student
from calendar import monthrange
# login student
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
# from .forms import UserForm
from .models import UserData
from .models import Student, Attendance

# initialize model (loads once)

import matplotlib.pyplot as plt
import io, base64

from .models import Faculty, Attendance, Subject
# def login_page(request):
#     return render(request, 'face_app/login2.html')

from .models import Student, Faculty
from django.utils.timezone import now
from .models import Faculty, TimeTable, Subject, Attendance
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.contrib import messages



from datetime import date, timedelta

from numpy.linalg import norm

def login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")
        dept_name = request.POST.get("department")

        user = authenticate(request, username=username, password=password)

        if user is None:
            error = "❌ Invalid username or password"
            return render(request, "face_app/login.html", {"error": error})

        # =====================
        # FACULTY LOGIN CHECK
        # =====================
        if role == "faculty":
            try:
                faculty = Faculty.objects.get(user=user)
            except Faculty.DoesNotExist:
                error = "❌ You are not registered as Faculty"
                return render(request, "face_app/login.html", {"error": error})

            if not dept_name:
                error = "❌ Department selection required for Faculty"
                return render(request, "face_app/login.html", {"error": error})

            if faculty.department.name != dept_name:
                error = f"❌ You belong to {faculty.department.name} department, not {dept_name}"
                return render(request, "face_app/login.html", {"error": error})

            login(request, user)
            return redirect("faculty_dashboard")

        # =====================
        # STUDENT LOGIN CHECK
        # =====================
        elif role == "student":
            try:
                student = Student.objects.get(user=user)
            except Student.DoesNotExist:
                error = "❌ You are not registered as Student"
                return render(request, "face_app/login.html", {"error": error})

            login(request, user)
            return redirect("student_dashboard")

        # =====================
        # ADMIN LOGIN
        # =====================
        elif role == "admin":
            if not user.is_superuser:
                error = "❌ You are not Admin"
                return render(request, "face_app/login.html", {"error": error})

            login(request, user)
            return redirect("/admin/")

        else:
            error = "❌ Invalid role selected"

    return render(request, "face_app/login.html")
# {"error": error}
###########################
def student_monthly_report(request):
    student = Student.objects.get(user=request.user)

    records = Attendance.objects.filter(student=student)

    attendance_data = {
        str(a.date): a.status
        for a in records
    }

    return render(request, 'face_app/student_monthly_report.html', {
        'attendance_data': attendance_data
    })


def capture_page(request):
    students = Student.objects.all()   # ya faculty.department ke students
    return render(request, 'face_app/capture2.html', {
        'students': students
    })

@login_required
def student_dashboard(request):
    student = Student.objects.get(user=request.user)

    today = date.today()

    # ---------------- SUMMARY ----------------
    total_days = Attendance.objects.filter(student=student).count()
    present_days = Attendance.objects.filter(student=student, status='Present').count()
    absent_days = total_days - present_days

    attendance_percent = int((present_days / total_days) * 100) if total_days > 0 else 0

    # ---------------- LAST 7 DAYS ----------------
    week_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        is_present = Attendance.objects.filter(
            student=student,
            date=d,
            status='Present'
        ).exists()
        week_data.append(1 if is_present else 0)

    # ---------------- LAST 28 DAYS ----------------
    month_data = []
    for i in range(27, -1, -1):
        d = today - timedelta(days=i)
        total = Attendance.objects.filter(student=student, date=d).count()
        present = Attendance.objects.filter(student=student, date=d, status='Present').count()
        percent = int((present / total) * 100) if total > 0 else 0
        month_data.append(percent)

    context = {
        'attendance_percent': attendance_percent,
        'present_days': present_days,
        'absent_days': absent_days,
        'week_data': json.dumps(week_data),
        'month_data': json.dumps(month_data),
    }

    return render(request, 'face_app/student_dashboard.html', context)

@login_required
def view_attendance(request):
    student = Student.objects.get(user=request.user)
    records = Attendance.objects.filter(student=student).order_by('-date')
    return render(request, 'face_app/view_attendance.html', {'records': records})


@login_required
def monthly_report(request):
    student = Student.objects.get(user=request.user)
    records = Attendance.objects.filter(student=student)
    return render(request, 'face_app/monthly_report.html', {'records': records})


@login_required
def performance(request):
    student = Student.objects.get(user=request.user)
    return render(request, 'face_app/performance.html')


@login_required
def student_profile(request):
    student = Student.objects.get(user=request.user)
    return render(request, 'face_app/profile.html', {'student': student})

@login_required
def profile(request):
    student = Student.objects.get(user=request.user)

    total = Attendance.objects.filter(student=student).count()
    present = Attendance.objects.filter(student=student, status='Present').count()
    absent = total - present
    percent = int((present / total) * 100) if total > 0 else 0

    return render(request, 'face_app/profile.html', {
        'student': student,
        'attendance_percent': percent,
        'present_days': present,
        'absent_days': absent
    })


def logout_view(request):
    logout(request)
    return redirect('login')
########################### faculty dashboard
@login_required
def faculty_dashboard(request):
    faculty = Faculty.objects.get(user=request.user)

    students_qs = Student.objects.filter(department=faculty.department)

    # 👇 JS ke liye clean data
    students = [
        {
            'id': s.id,
            'name': s.name,
            'roll_no': s.roll_no
        }
        for s in students_qs
    ]

    attendance_data = defaultdict(dict)

    # ⚠️ DAY-WISE attendance (no subject)
    for a in Attendance.objects.filter(student__department=faculty.department):
        attendance_data[a.student.id][str(a.date)] = a.status

    today = date.today()

    context = {
        'faculty': faculty,
        'students': students,
        'attendance_data': dict(attendance_data),
        'total_students': students_qs.count(),
        'today_present': Attendance.objects.filter(date=today, status='Present').count(),
        'today_absent': Attendance.objects.filter(date=today, status='Absent').count(),
    }

    return render(request, 'face_app/faculty_dashboard.html', context)
@login_required

def add_student(request):
    faculty = Faculty.objects.get(user=request.user)

    if request.method == 'POST':
        # form data
        name = request.POST['name']
        email = request.POST['email']
        contact = request.POST['contact']
        roll_no = request.POST['roll_no']
        username = request.POST['username']
        password = request.POST['password']
        profile_picture = request.FILES.get('profile')

        # ❌ username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Username already exists. Try another.")
            return redirect('add_student')

        # ❌ email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "❌ Email already exists.")
            return redirect('add_student')

        # 🔐 CREATE USER (LOGIN ACCOUNT)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # 🎓 CREATE STUDENT
        Student.objects.create(
            user=user,
            faculty=faculty,
            department=faculty.department,
            name=name,
            email=email,
            contact_no=contact,
            roll_no=roll_no,
            profile_picture=profile_picture   # ✅ CORRECT FIELD
        )

        messages.success(request, "✅ Student added successfully")
        return redirect('faculty_dashboard')

    return render(request, 'face_app/add_student.html', {
        'department': faculty.department
    })

@login_required

def edit_student_attendance(request):
    students = Student.objects.all()
    selected_student = None
    attendance = []

    if 'student_id' in request.GET:
        selected_student = Student.objects.get(id=request.GET['student_id'])
        attendance = Attendance.objects.filter(
            student=selected_student
        ).order_by('-date')

    if request.method == 'POST':
        student_id = request.POST['student_id']
        att_date = request.POST['date']
        status = request.POST['status']

        student = Student.objects.get(id=student_id)

        Attendance.objects.update_or_create(
            student=student,
            date=att_date,
            defaults={
                'status': status,
                'auto_marked': False
            }
        )

        return redirect(f"/faculty/edit-attendance/?student_id={student_id}")

    return render(request, 'face_app/edit_attendance.html', {
        'students': students,
        'selected_student': selected_student,
        'attendance': attendance
    })

@login_required
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    return redirect('faculty_dashboard')


@login_required
def student_attendance(request, id):
    student = get_object_or_404(Student, id=id)

    today = date.today()
    total_days = monthrange(today.year, today.month)[1]

    records = Attendance.objects.filter(
        student=student,
        date__month=today.month
    )

    present = records.filter(status='Present').count()
    absent = total_days - present

    return render(request, 'face_app/student_attendance.html', {
        'student': student,
        'present': present,
        'absent': absent
    })


@login_required
def register_face(request, id):
    student = get_object_or_404(Student, id=id)

    # 🔥 Here you will integrate InsightFace / camera logic later
    student.face_registered = True
    student.save()

    return redirect('faculty_dashboard')
###################################################
app = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0)

def cosine_sim(a,b):
    return np.dot(a,b)/(norm(a)*norm(b)+1e-10)

# def capture_page(request):
#     return render(request, 'face_app/capture.html')

# @csrf_exempt
# def capture_face(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)

#         # required: name + image
#         student_name = data.get('name', '').strip()
#         img_b64 = data.get('image', '').split(',')[-1]

#         if not student_name:
#             return JsonResponse({'message': 'Student name required'}, status=400)

#         if not img_b64:
#             return JsonResponse({'message': 'No image data'}, status=400)

#         # decode image
#         img_bytes = base64.b64decode(img_b64)
#         arr = np.frombuffer(img_bytes, np.uint8)
#         frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

#         # detect face
#         faces = app.get(frame)
#         if not faces:
#             return JsonResponse({'message':'No face detected'}, status=200)

#         # get embedding
#         emb = faces[0].embedding.astype(float).tolist()

#         # save student with REAL NAME
#         s = Student.objects.create(
#             name=student_name,       # <—— REAL NAME
#             embedding=json.dumps(emb)
#         )        

#         # crop & save face image
#         x1,y1,x2,y2 = faces[0].bbox.astype(int)
#         h,w = frame.shape[:2]
#         x1, y1 = max(0,x1), max(0,y1)
#         x2, y2 = min(w,x2), min(h,y2)

#         crop = frame[y1:y2, x1:x2]

#         faces_dir = 'media/faces'
#         import os
#         os.makedirs(faces_dir, exist_ok=True)

#         fname = f'face_{s.id}.jpg'
#         cv2.imwrite(os.path.join(faces_dir, fname), crop)

#         s.face_image = f'faces/{fname}'
#         s.save()

#         return JsonResponse({'message':'Face saved', 'id': s.id})

#     return JsonResponse({'message':'Invalid method'}, status=405)

@csrf_exempt
def capture_face(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request'}, status=405)

    try:
        data = json.loads(request.body)

        student_id = data.get('student_id')
        img_b64 = data.get('image', '').split(',')[-1]

        if not student_id:
            return JsonResponse({'message': 'Student not selected'}, status=400)

        if not img_b64:
            return JsonResponse({'message': 'Image not received'}, status=400)

        # get student
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return JsonResponse({'message': 'Student not found'}, status=404)

        # decode image
        img_bytes = base64.b64decode(img_b64)
        arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        # detect face
        faces = app.get(frame)
        if not faces:
            return JsonResponse({'message': '❌ No face detected'}, status=200)

        face = faces[0]
        embedding = face.embedding.astype(float).tolist()

        # save embedding
        student.face_embedding = json.dumps(embedding)
        student.face_registered = True

        # crop face
        x1, y1, x2, y2 = face.bbox.astype(int)
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        crop = frame[y1:y2, x1:x2]

        os.makedirs("media/students/faces", exist_ok=True)
        face_path = f"students/faces/student_{student.id}.jpg"
        cv2.imwrite("media/" + face_path, crop)

        student.profile_picture = face_path
        student.save()

        return JsonResponse({'message': '✅ Face registered successfully'})

    except Exception as e:
        return JsonResponse({'message': f'❌ Error: {str(e)}'}, status=500)


def gen_frames():
    # 🔹 Load saved face embeddings
    students = Student.objects.filter(face_registered=True).exclude(face_embedding__isnull=True)

    known_embeddings = []
    known_names = []






def gen_frames():
    print("🎥 gen_frames started")

    try:
        # 🔹 Load registered students
        students = Student.objects.filter(face_registered=True)
        print("👥 Students loaded:", students.count())

        known_embeddings = []
        known_students = []

        for s in students:
            if s.face_embedding:
                known_embeddings.append(
                    np.array(json.loads(s.face_embedding), dtype=np.float32)
                )
                known_students.append(s)

        # 🎥 Camera (Mac compatible)
        cap = cv2.VideoCapture(2, cv2.CAP_AVFOUNDATION)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        recognized_today = set()  # avoid repeat attendance

        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Frame not read")
                continue

            faces = app.get(frame)
            print("🙂 Faces detected:", len(faces))

            for face in faces:
                emb = face.embedding.astype(np.float32)

                student_obj = None
                name = "Unknown"

                # 🔍 Face matching
                if known_embeddings:
                    sims = [
                        np.dot(emb, ke) / (norm(emb) * norm(ke) + 1e-10)
                        for ke in known_embeddings
                    ]
                    idx = int(np.argmax(sims))

                    if sims[idx] > 0.45:
                        student_obj = known_students[idx]
                        name = student_obj.name

                # ===============================
                # ✅ AUTO ATTENDANCE (DAY WISE)
                # ===============================
                if student_obj:
                    today = date.today()

                    if student_obj.id not in recognized_today:
                        attendance, created = Attendance.objects.get_or_create(
                            student=student_obj,
                            date=today,
                            defaults={
                                'status': 'Present',
                                'marked_by_face': True,
                                'auto_marked': True
                            }
                        )

                        if created:
                            print(f"✅ Attendance marked for {student_obj.name}")
                        else:
                            print(f"ℹ️ Attendance already marked for {student_obj.name}")

                        recognized_today.add(student_obj.id)

                # 🟩 Draw face box
                x1, y1, x2, y2 = face.bbox.astype(int)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                cv2.putText(
                    frame,
                    name,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

            # 🎞️ Stream frame
            _, jpeg = cv2.imencode('.jpg', frame)
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                jpeg.tobytes() +
                b'\r\n'
            )

    except Exception as e:
        print("🔥 gen_frames ERROR:", e)


def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def recognize_page(request):
    return render(request, 'face_app/recognize.html')


# login student 
