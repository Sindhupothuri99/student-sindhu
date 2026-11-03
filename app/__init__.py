from datetime import date, datetime
from functools import wraps
from flask import Flask, request, redirect, url_for, flash, render_template_string, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash
import os

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

class User(UserMixin, db.Model):
    id=db.Column(db.Integer, primary_key=True)
    full_name=db.Column(db.String(120), nullable=False)
    email=db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash=db.Column(db.String(255), nullable=False)
    role=db.Column(db.String(20), nullable=False, default="student")
    is_active=db.Column(db.Boolean, default=True, nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    def set_password(self,p): self.password_hash=generate_password_hash(p)
    def check_password(self,p): return check_password_hash(self.password_hash,p)

class Student(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),unique=True)
    roll_number=db.Column(db.String(40),unique=True,nullable=False); department=db.Column(db.String(100),nullable=False)
    year=db.Column(db.Integer,default=1); phone=db.Column(db.String(25))
    user=db.relationship("User",backref=db.backref("student_profile",uselist=False))
class Faculty(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),unique=True)
    employee_id=db.Column(db.String(40),unique=True,nullable=False); department=db.Column(db.String(100),nullable=False)
    phone=db.Column(db.String(25)); user=db.relationship("User",backref=db.backref("faculty_profile",uselist=False))
class Course(db.Model):
    id=db.Column(db.Integer,primary_key=True); code=db.Column(db.String(30),unique=True,nullable=False)
    title=db.Column(db.String(140),nullable=False); department=db.Column(db.String(100),nullable=False)
    faculty_id=db.Column(db.Integer,db.ForeignKey("faculty.id")); faculty=db.relationship("Faculty",backref="courses")
class Attendance(db.Model):
    id=db.Column(db.Integer,primary_key=True); student_id=db.Column(db.Integer,db.ForeignKey("student.id"),nullable=False)
    course_id=db.Column(db.Integer,db.ForeignKey("course.id"),nullable=False); attendance_date=db.Column(db.Date,default=date.today,nullable=False)
    status=db.Column(db.String(12),nullable=False); marked_by=db.Column(db.Integer,db.ForeignKey("user.id"))
    student=db.relationship("Student",backref="attendance_records"); course=db.relationship("Course",backref="attendance_records")
    __table_args__=(UniqueConstraint("student_id","course_id","attendance_date",name="uq_attendance_day"),)
class Assignment(db.Model):
    id=db.Column(db.Integer,primary_key=True); course_id=db.Column(db.Integer,db.ForeignKey("course.id"),nullable=False)
    title=db.Column(db.String(160),nullable=False); description=db.Column(db.Text); due_date=db.Column(db.Date,nullable=False)
    created_by=db.Column(db.Integer,db.ForeignKey("user.id")); created_at=db.Column(db.DateTime,default=datetime.utcnow)
    course=db.relationship("Course",backref="assignments")
class Submission(db.Model):
    id=db.Column(db.Integer,primary_key=True); assignment_id=db.Column(db.Integer,db.ForeignKey("assignment.id"),nullable=False)
    student_id=db.Column(db.Integer,db.ForeignKey("student.id"),nullable=False); answer_text=db.Column(db.Text,nullable=False)
    submitted_at=db.Column(db.DateTime,default=datetime.utcnow); grade=db.Column(db.String(10)); feedback=db.Column(db.Text)
    assignment=db.relationship("Assignment",backref="submissions"); student=db.relationship("Student",backref="submissions")
    __table_args__=(UniqueConstraint("assignment_id","student_id",name="uq_assignment_submission"),)
class Exam(db.Model):
    id=db.Column(db.Integer,primary_key=True); course_id=db.Column(db.Integer,db.ForeignKey("course.id"),nullable=False)
    title=db.Column(db.String(160),nullable=False); exam_date=db.Column(db.Date,nullable=False); max_marks=db.Column(db.Float,default=100)
    course=db.relationship("Course",backref="exams")
class Result(db.Model):
    id=db.Column(db.Integer,primary_key=True); exam_id=db.Column(db.Integer,db.ForeignKey("exam.id"),nullable=False)
    student_id=db.Column(db.Integer,db.ForeignKey("student.id"),nullable=False); marks=db.Column(db.Float,nullable=False)
    remarks=db.Column(db.String(255)); exam=db.relationship("Exam",backref="results"); student=db.relationship("Student",backref="results")
    __table_args__=(UniqueConstraint("exam_id","student_id",name="uq_exam_result"),)
class Notice(db.Model):
    id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(160),nullable=False); body=db.Column(db.Text,nullable=False)
    audience=db.Column(db.String(20),default="all"); author_id=db.Column(db.Integer,db.ForeignKey("user.id"))
    created_at=db.Column(db.DateTime,default=datetime.utcnow); author=db.relationship("User")

@login_manager.user_loader
def load_user(uid): return db.session.get(User,int(uid))

def roles(*allowed):
    def deco(fn):
        @wraps(fn)
        @login_required
        def wrapped(*a,**kw):
            if current_user.role not in allowed: abort(403)
            return fn(*a,**kw)
        return wrapped
    return deco

BASE = """
<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{{ title }} · EduPrime</title><link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css' rel='stylesheet'>
<style>body{background:#f4f7fc;color:#182942}.navbar{background:#142b4a}.card{border:0;border-radius:15px;box-shadow:0 5px 22px #142b4a0c}.stat{padding:22px;background:white;border-radius:15px}.stat b{font-size:2rem;color:#2858d7}.quick a{display:block;padding:15px;border:1px solid #e5ebf4;border-radius:12px;text-decoration:none;color:#142b4a;margin:6px 0}.table th{font-size:.78rem;color:#718096;text-transform:uppercase}.btn{border-radius:9px}.login{max-width:440px;margin:8vh auto}</style></head><body>
{% if current_user.is_authenticated %}<nav class='navbar navbar-expand-lg navbar-dark'><div class='container-fluid'><a class='navbar-brand fw-bold' href='/dashboard'>EduPrime</a><button class='navbar-toggler' data-bs-toggle='collapse' data-bs-target='#nav'><span class='navbar-toggler-icon'></span></button><div class='collapse navbar-collapse' id='nav'><ul class='navbar-nav me-auto'>
<li class='nav-item'><a class='nav-link' href='/dashboard'>Dashboard</a></li>
{% if current_user.role=='admin' %}<li class='nav-item'><a class='nav-link' href='/users'>Users</a></li><li class='nav-item'><a class='nav-link' href='/students'>Students</a></li><li class='nav-item'><a class='nav-link' href='/faculty'>Faculty</a></li><li class='nav-item'><a class='nav-link' href='/courses'>Courses</a></li>{% elif current_user.role=='faculty' %}<li class='nav-item'><a class='nav-link' href='/students'>Students</a></li>{% endif %}
<li class='nav-item'><a class='nav-link' href='/attendance'>Attendance</a></li><li class='nav-item'><a class='nav-link' href='/assignments'>Assignments</a></li><li class='nav-item'><a class='nav-link' href='/exams'>Exams & Results</a></li><li class='nav-item'><a class='nav-link' href='/notices'>Notices</a></li></ul><span class='navbar-text me-3'>{{ current_user.full_name }} · {{ current_user.role|title }}</span><form method='post' action='/logout'><input type='hidden' name='csrf_token' value='{{ csrf_token() }}'><button class='btn btn-outline-light btn-sm'>Sign out</button></form></div></div></nav>{% endif %}
<main class='container py-4'>{% with msgs=get_flashed_messages(with_categories=true) %}{% for cat,msg in msgs %}<div class='alert alert-{{cat}} alert-dismissible fade show'>{{msg}}<button class='btn-close' data-bs-dismiss='alert'></button></div>{% endfor %}{% endwith %}{{ body|safe }}</main><footer class='text-center text-secondary small py-4'>EduPrime · Student Management System</footer><script src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js'></script></body></html>
"""
def page(title,body,**ctx):
    return render_template_string(BASE,title=title,body=render_template_string(body,**ctx),**ctx)

def create_app(test_config=None):
    app=Flask(__name__)
    app.config.update(SECRET_KEY=os.getenv("SECRET_KEY","dev-only-change-this-secret"),SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL","sqlite:///eduprime.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE","0")=="1",WTF_CSRF_TIME_LIMIT=3600)
    if test_config: app.config.update(test_config)
    db.init_app(app); login_manager.init_app(app); csrf.init_app(app); login_manager.login_view="login"
    @app.get("/health")
    def health(): return {"status":"ok","application":"EduPrime"}
    @app.route("/")
    def index(): return redirect(url_for("dashboard") if current_user.is_authenticated else url_for("login"))
    @app.route("/login",methods=["GET","POST"])
    def login():
        if current_user.is_authenticated: return redirect(url_for("dashboard"))
        if request.method=="POST":
            u=User.query.filter_by(email=request.form.get("email","").strip().lower(),is_active=True).first()
            if u and u.check_password(request.form.get("password","")):
                login_user(u,remember=request.form.get("remember")=="on"); return redirect(url_for("dashboard"))
            flash("Invalid email or password.","danger")
        return page("Sign in","""<div class='login card p-4 p-md-5'><h2 class='fw-bold'>Welcome to EduPrime</h2><p class='text-secondary'>Sign in to your academic workspace.</p><form method='post'><input type='hidden' name='csrf_token' value='{{csrf_token()}}'><label class='form-label'>Email</label><input class='form-control mb-3' type='email' name='email' required><label class='form-label'>Password</label><input class='form-control mb-3' type='password' name='password' required><button class='btn btn-primary btn-lg w-100'>Sign in</button></form></div>""")
    @app.post("/logout")
    @login_required
    def logout(): logout_user(); flash("Signed out successfully.","info"); return redirect(url_for("login"))
    @app.get("/dashboard")
    @login_required
    def dashboard():
        stats=[("Students",Student.query.count()),("Faculty",Faculty.query.count()),("Courses",Course.query.count()),("Assignments",Assignment.query.count())]
        notices=Notice.query.filter(Notice.audience.in_(["all",current_user.role])).order_by(Notice.created_at.desc()).limit(5).all()
        return page("Dashboard","""<h1 class='h3 fw-bold'>Welcome, {{current_user.full_name}}</h1><p class='text-secondary'>Your academic workspace at a glance.</p><div class='row g-3 my-3'>{% for label,value in stats %}<div class='col-6 col-xl-3'><div class='stat'><div class='text-secondary'>{{label}}</div><b>{{value}}</b></div></div>{% endfor %}</div><div class='row g-3'><div class='col-lg-7'><div class='card p-4'><h5>Quick access</h5><div class='quick'><a href='/attendance'>Attendance · Daily records</a><a href='/assignments'>Assignments · Publish and submit</a><a href='/exams'>Exams & Results · Schedules and grades</a><a href='/notices'>Notices · Announcements</a></div></div></div><div class='col-lg-5'><div class='card p-4'><h5>Latest notices</h5>{% for n in notices %}<p class='border-bottom pb-2'><b>{{n.title}}</b><br><small class='text-secondary'>{{n.body}}</small></p>{% else %}<p class='text-secondary'>No notices published.</p>{% endfor %}</div></div></div>""",stats=stats,notices=notices)
    @app.route("/users",methods=["GET","POST"])
    @roles("admin")
    def users():
        if request.method=="POST":
            name=request.form.get("full_name","").strip(); email=request.form.get("email","").strip().lower(); pw=request.form.get("password",""); role=request.form.get("role","")
            if not name or not email or len(pw)<10 or role not in ("admin","faculty","student"): flash("Enter valid details; password must be at least 10 characters.","danger")
            elif User.query.filter_by(email=email).first(): flash("Email already exists.","danger")
            else:
                u=User(full_name=name,email=email,role=role); u.set_password(pw); db.session.add(u); db.session.commit(); flash("Account created.","success"); return redirect("/users")
        return page("Users","""<h1 class='h3 mb-3'>User accounts</h1><div class='card p-3 mb-4'><form method='post' class='row g-2'><input type='hidden' name='csrf_token' value='{{csrf_token()}}'><div class='col-md-3'><input class='form-control' name='full_name' placeholder='Full name' required></div><div class='col-md-3'><input class='form-control' type='email' name='email' placeholder='Email' required></div><div class='col-md-2'><input class='form-control' type='password' name='password' minlength='10' placeholder='Password (10+)' required></div><div class='col-md-2'><select class='form-select' name='role'><option>student</option><option>faculty</option><option>admin</option></select></div><div class='col-md-2'><button class='btn btn-primary w-100'>Create account</button></div></form></div><div class='card table-responsive'><table class='table mb-0'><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th></th></tr>{% for u in users %}<tr><td>{{u.full_name}}</td><td>{{u.email}}</td><td>{{u.role}}</td><td>{{'Active' if u.is_active else 'Disabled'}}</td><td>{% if u.id!=current_user.id %}<form method='post' action='/users/{{u.id}}/toggle'><input type='hidden' name='csrf_token' value='{{csrf_token()}}'><button class='btn btn-sm btn-outline-secondary'>Toggle</button></form>{% endif %}</td></tr>{% endfor %}</table></div>""",users=User.query.order_by(User.created_at.desc()).all())
    @app.post("/users/<int:uid>/toggle")
    @roles("admin")
    def toggle_user(uid):
        u=db.get_or_404(User,uid)
        if u.id!=current_user.id: u.is_active=not u.is_active; db.session.commit()
        return redirect("/users")
    @app.route("/students",methods=["GET","POST"])
    @roles("admin","faculty")
    def students():
        if request.method=="POST":
            if current_user.role!="admin": abort(403)
            try:
                u=db.get_or_404(User,int(request.form["user_id"]))
                if u.role!="student" or u.student_profile: raise ValueError()
                db.session.add(Student(user_id=u.id,roll_number=request.form["roll_number"].strip(),department=request.form["department"].strip(),year=int(request.form["year"]),phone=request.form.get("phone","")))
                db.session.commit(); flash("Student profile added.","success")
            except Exception: db.session.rollback(); flash("Could not create profile; check account and unique roll number.","danger")
            return redirect("/students")
        return page("Students","""<h1 class='h3 mb-3'>Student directory</h1>{% if current_user.role=='admin' %}<div class='card p-3 mb-4'><form method='post' class='row g-2'><input type='hidden' name='csrf_token' value='{{csrf_token()}}'><div class='col-md-3'><select class='form-select' name='user_id' required><option value=''>Student account</option>{% for u in available if not u.student_profile %}<option value='{{u.id}}'>{{u.full_name}} · {{u.email}}</option>{% endfor %}</select></div><div class='col-md-2'><input class='form-control' name='roll_number' placeholder='Roll number' required></div><div class='col-md-3'><input class='form-control' name='department' placeholder='Department' required></div><div class='col-md-1'><input class='form-control' type='number' name='year' min='1' max='8' value='1'></div><div class='col-md-2'><input class='form-control' name='phone' placeholder='Phone'></div><div class='col-md-1'><button class='btn btn-primary'>Add</button></div></form></div>{% endif %}<div class='card table-responsive'><table class='table mb-0'><tr><th>Roll no.</th><th>Name</th><th>Email</th><th>Department</th><th>Year</th></tr>{% for s in students %}<tr><td>{{s.roll_number}}</td><td>{{s.user.full_name}}</td><td>{{s.user.email}}</td><td>{{s.department}}</td><td>{{s.year}}</td></tr>{% else %}<tr><td colspan='5'>No students yet.</td></tr>{% endfor %}</table></div>""",students=Student.query.all(),available=User.query.filter_by(role="student").all())
    @app.route("/faculty",methods=["GET","POST"])
    @roles("admin")
    def faculty():
        if request.method=="POST":
            try:
                u=db.get_or_404(User,int(request.form["user_id"]))
                if u.role!="faculty" or u.faculty_profile: raise ValueError()
                db.session.add(Faculty(user_id=u.id,employee_id=request.form["employee_id"],department=request.form["department"],phone=request.form.get("phone",""))); db.session.commit(); flash("Faculty profile added.","success")
            except Exception: db.session.rollback(); flash("Could not add profile; check employee ID.","danger")
            return redirect("/faculty")
        return page("Faculty","""<h1 class='h3 mb-3'>Faculty directory</h1><div class='card p-3 mb-4'><form method='post' class='row g-2'><input type='hidden' name='csrf_token' value='{{csrf_token()}}'><div class='col-md-3'><select class='form-select' name='user_id' required><option value=''>Faculty account</option>{% for u in available if not u.faculty_profile %}<option value='{{u.id}}'>{{u.full_name}}</option>{% endfor %}</select></div><div class='col-md-2'><input class='form-control' name='employee_id' placeholder='Employee ID' required></div><div class='col-md-4'><input class='form-control' name='department' placeholder='Department' required></div><div class='col-md-2'><input class='form-control' name='phone' placeholder='Phone'></div><div class='col-md-1'><button class='btn btn-primary'>Add</button></div></form></div><div class='card table-responsive'><table class='table mb-0'><tr><th>ID</th><th>Name</th><th>Email</th><th>Department</th></tr>{% for f in faculty %}<tr><td>{{f.employee_id}}</td><td>{{f.user.full_name}}</td><td>{{f.user.email}}</td><td>{{f.department}}</td></tr>{% endfor %}</table></div>""",faculty=Faculty.query.all(),available=User.query.filter_by(role="faculty").all())
    @app.route("/courses",methods=["GET","POST"])
    @roles("admin")
    def courses():
        if request.method=="POST":
            try:
                fid=request.form.get("faculty_id") or None
                db.session.add(Course(code=request.form["code"].upper(),title=request.form["title"],department=request.form["department"],faculty_id=int(fid) if fid else None)); db.session.commit(); flash("Course created.","success")
            except Exception: db.session.rollback(); flash("Course code must be unique and fields valid.","danger")
            return redirect("/courses")
        return page("Courses","""<h1 class='h3 mb-3'>Course catalogue</h1><div class='card p-3 mb-4'><form method='post' class='row g-2'><input type='hidden' name='csrf_token' value='{{csrf_token()}}'><div class='col-md-2'><input class='form-control' name='code' placeholder='Code' required></div><div class='col-md-3'><input class='form-control' name='title' placeholder='Course title' required></div><div class='col-md-3'><input class='form-control' name='department' placeholder='Department' required></div><div class='col-md-3'><select class='form-select' name='faculty_id'><option value=''>Faculty (optional)</option>{% for f in faculty %}<option value='{{f.id}}'>{{f.user.full_name}}</option>{% endfor %}</select></div><div class='col-md-1'><button class='btn btn-primary'>Add</button></div></form></div><div class='card table-responsive'><table class='table mb-0'><tr><th>Code</th><th>Course</th><th>Department</th><th>Faculty</th></tr>{% for c in courses %}<tr><td>{{c.code}}</td><td>{{c.title}}</td><td>{{c.department}}</td><td>{{c.faculty.user.full_name if c.faculty else 'Unassigned'}}</td></tr>{% endfor %}</table></div>""",courses=Course.query.all(),faculty=Faculty.query.all())
    def assigned_course_ids():
        f=Faculty.query.filter_by(user_id=current_user.id).first()
        return [c.id for c in f.courses] if f else []
    @app.route("/attendance",methods=["GET","POST"])
    @roles("admin","faculty","student")
    def attendance():
        profile=Student.query.filter_by(user_id=current_user.id).first() if current_user.role=="student" else None
        if request.method=="POST":
            try:
                sid=int(request.form["student_id"]); cid=int(request.form["course_id"]); day=date.fromisoformat(request.form["attendance_date"]); status=request.form["status"]
                if status not in ("Present","Absent","Late") or (current_user.role=="faculty" and cid not in assigned_course_ids()): abort(403)
                r=Attendance.query.filter_by(student_id=sid,course_id=cid,attendance_date=day).first()
                if r: r.status=status
                else: db.session.add(Attendance(student_id=sid,course_id=cid,attendance_date=day,status=status,marked_by=current_user.id))
                db.session.commit(); flash("Attendance saved.","success")
            except (ValueError,KeyError): db.session.rollback(); flash("Invalid attendance details.","danger")
            return redirect("/attendance")
        q=Attendance.query.filter_by(student_id=profile.id) if profile else Attendance.query
        records=q.order_by(Attendance.attendance_date.desc()).limit(150).all()
        courses=Course.query.filter(Course.id.in_(assigned_course_ids())).all() if current_user.role=="faculty" else Course.query.all()
        return page("Attendance","""<h1 class='h3 mb-3'>Attendance</h1>{% if current_user.role!='student' %}<div class='card p-3 mb-4'><form method='post' class='row g-2'><input type='hidden' name='csrf_token' value='{{csrf_token()}}'><div class='col-md-3'><select class='form-select' name='student_id' required><option value=''>Student</option>{% for s in students %}<option value='{{s.id}}'>{{s.roll_number}} · {{s.user.full_name}}</option>{% endfor %}</select></div><div class='col-md-3'><select class='form-select' name='course_id' required><option value=''>Course</option>{% for c in courses %}<option value='{{c.id}}'>{{c.code}}</option>{% endfor %}</select></div><div class='col-md-2'><input class='form-control' type='date' name='attendance_date' value='{{today}}' required></div><div class='col-md-2'><select class='form-select' name='status'><option>Present</option><option>Absent</option><option>Late</option></select></div><div class='col-md-2'><button class='btn btn-primary w-100'>Save</button></div></form></div>{% endif %}<div class='card table-responsive'><table class='table mb-0'><tr><th>Date</th><th>Student</th><th>Course</th><th>Status</th></tr>{% for r in records %}<tr><td>{{r.attendance_date}}</td><td>{{r.student.user.full_name}}</td><td>{{r.course.code}}</td><td>{{r.status}}</td></tr>{% else %}<tr><td colspan='4'>No records.</td></tr>{% endfor %}</table></div>""",records=records,students=Student.query.all(),courses=courses,today=date.today().isoformat())
    @app.route("/assignments",methods=["GET","POST"])
    @login_required
    def assignments():
        if request.method=="POST":
            if current_user.role not in ("admin","faculty"): abort(403)
            try:
                cid=int(request.form["course_id"])
                if current_user.role=="faculty" and cid not in assigned_course_ids(): abort(403)
                db.session.add(Assignment(course_id=cid,title=request.form["title"],description=request.form.get("description",""),due_date=date.fromisoformat(request.form["due_date"]),created_by=current_user.id)); db.session.commit(); flash("Assignment published.","success")
            except (ValueError,KeyError): db.session.rollback(); flash("Invalid assignment details.","danger")
            return redirect("/assignments")
        q=Assignment.query
        if current_user.role=="faculty": q=q.filter(Assignment.course_id.in_(assigned_course_ids()))
        profile=Student.query.filter_by(user_id=current_user.id).first() if current_user.role=="student" else None
        return page("Assignments","""<h1 class='h3 mb-3'>Assignments</h1>{% if current_user.role in ['admin','faculty'] %}<div class='card p-3 mb-4'><form method='post' class='row g-2'><input type='hidden' name='csrf_token' value='{{csrf_token()}}'><div class='col-md-3'><select class='form-select' name='course_id' required><option value=''>Course</option>{% for c in courses %}<option value='{{c.id}}'>{{c.code}}</option>{% endfor %}</select></div><div class='col-md-3'><input class='form-control' name='title' placeholder='Title' required></div><div class='col-md-2'><input class='form-control' type='date' name='due_date' required></div><div class='col-md-3'><input class='form-control' name='description' placeholder='Instructions'></div><div class='col-md-1'><button class='btn btn-primary'>Publish</button></div></form></div>{% endif %}<div class='row g-3'>{% for a in assignments %}<div class='col-md-6'><div class='card p-3 h-100'><div class='d-flex justify-content-between'><span class='badge bg-light text-dark'>{{a.course.code}}</span><small>Due {{a.due_date}}</small></div><h5 class='mt-2'>{{a.title}}</h5><p>{{a.description}}</p>{% if current_user.role=='student' %}<form method='post' action='/assignments/{{a.id}}/submit'><input type='hidden' name='csrf_token' value='{{csrf_token()}}'><textarea class='form-control mb-2' name='answer_text' placeholder='Your submission' required></textarea><button class='btn btn-primary btn-sm' {% if a.due_date<today %}disabled{% endif %}>Submit / update</button></form>{% endif %}</div></div>{% else %}<p>No assignments.</p>{% endfor %}</div>""",assignments=q.order_by(Assignment.due_date).all(),courses=Course.query.filter(Course.id.in_(assigned_course_ids())).all() if current_user.role=="faculty" else Course.query.all(),today=date.today())
    @app.post("/assignments/<int:aid>/submit")
    @roles("student")
    def submit_assignment(aid):
        s=Student.query.filter_by(user_id=current_user.id).first(); a=db.get_or_404(Assignment,aid); answer=request.form.get("answer_text","").strip()
        if not s: flash("Ask the administrator to create your student profile.","warning")
        elif not answer or date.today()>a.due_date: flash("Submission is empty or past the due date.","danger")
        else:
            sub=Submission.query.filter_by(assignment_id=aid,student_id=s.id).first()
            if sub: sub.answer_text=answer; sub.submitted_at=datetime.utcnow()
            else: db.session.add(Submission(assignment_id=aid,student_id=s.id,answer_text=answer))
            db.session.commit(); flash("Assignment submitted.","success")
        return redirect("/assignments")
    @app.route("/exams",methods=["GET","POST"])
    @roles("admin","faculty","student")
    def exams():
        if request.method=="POST":
            if current_user.role not in ("admin","faculty"): abort(403)
            try:
                cid=int(request.form["course_id"])
                if current_user.role=="faculty" and cid not in assigned_course_ids(): abort(403)
                db.session.add(Exam(course_id=cid,title=request.form["title"],exam_date=date.fromisoformat(request.form["exam_date"]),max_marks=float(request.form["max_marks"]))); db.session.commit(); flash("Exam scheduled.","success")
            except (ValueError,KeyError): db.session.rollback(); flash("Invalid exam details.","danger")
            return redirect("/exams")
        s=Student.query.filter_by(user_id=current_user.id).first() if current_user.role=="student" else None
        exams=Exam.query.join(Result).filter(Result.student_id==s.id).all() if s else Exam.query.order_by(Exam.exam_date).all()
        results=Result.query.filter_by(student_id=s.id).all() if s else Result.query.order_by(Result.id.desc()).limit(100).all()
        return page("Exams & Results","""<h1 class='h3 mb-3'>Examinations & results</h1>{% if current_user.role in ['admin','faculty'] %}<div class='card p-3 mb-4'><form method='post' class='row g-2'><input type='hidden' name='csrf_token' value='{{csrf_token()}}'><div class='col-md-4'><select class='form-select' name='course_id' required><option value=''>Course</option>{% for c in courses %}<option value='{{c.id}}'>{{c.code}}</option>{% endfor %}</select></div><div class='col-md-3'><input class='form-control' name='title' placeholder='Exam title' required></div><div class='col-md-2'><input class='form-control' type='date' name='exam_date' required></div><div class='col-md-2'><input class='form-control' type='number' min='1' name='max_marks' value='100'></div><div class='col-md-1'><button class='btn btn-primary'>Add</button></div></form></div>{% endif %}<div class='card p-3 mb-4'><h5>Exam schedule</h5><table class='table'><tr><th>Exam</th><th>Course</th><th>Date</th><th>Max</th></tr>{% for e in exams %}<tr><td>{{e.title}}</td><td>{{e.course.code}}</td><td>{{e.exam_date}}</td><td>{{e.max_marks}}</td></tr>{% else %}<tr><td colspan='4'>No exams available.</td></tr>{% endfor %}</table></div>{% if current_user.role in ['admin','faculty'] %}<div class='card p-3 mb-4'><h5>Enter result</h5>{% for e in exams %}<form method='post' action='/exams/{{e.id}}/results' class='row g-2 border-bottom py-2'><input type='hidden' name='csrf_token' value='{{csrf_token()}}'><div class='col-md-3'>{{e.title}}</div><div class='col-md-4'><select class='form-select' name='student_id' required><option value=''>Student</option>{% for s in students %}<option value='{{s.id}}'>{{s.roll_number}} · {{s.user.full_name}}</option>{% endfor %}</select></div><div class='col-md-2'><input class='form-control' type='number' name='marks' min='0' max='{{e.max_marks}}' step='.5' placeholder='Marks' required></div><div class='col-md-2'><input class='form-control' name='remarks' placeholder='Remarks'></div><div class='col-md-1'><button class='btn btn-primary btn-sm'>Save</button></div></form>{% endfor %}</div>{% endif %}<div class='card p-3'><h5>Results</h5><table class='table'><tr><th>Student</th><th>Exam</th><th>Course</th><th>Marks</th></tr>{% for r in results %}<tr><td>{{r.student.user.full_name}}</td><td>{{r.exam.title}}</td><td>{{r.exam.course.code}}</td><td>{{r.marks}} / {{r.exam.max_marks}}</td></tr>{% else %}<tr><td colspan='4'>No results.</td></tr>{% endfor %}</table></div>""",exams=exams,results=results,courses=Course.query.filter(Course.id.in_(assigned_course_ids())).all() if current_user.role=="faculty" else Course.query.all(),students=Student.query.all())
    @app.post("/exams/<int:eid>/results")
    @roles("admin","faculty")
    def enter_result(eid):
        e=db.get_or_404(Exam,eid)
        if current_user.role=="faculty" and e.course_id not in assigned_course_ids(): abort(403)
        try:
            sid=int(request.form["student_id"]); marks=float(request.form["marks"])
            if marks<0 or marks>e.max_marks: raise ValueError()
            r=Result.query.filter_by(exam_id=eid,student_id=sid).first()
            if r: r.marks=marks; r.remarks=request.form.get("remarks","")
            else: db.session.add(Result(exam_id=eid,student_id=sid,marks=marks,remarks=request.form.get("remarks","")))
            db.session.commit(); flash("Result saved.","success")
        except (ValueError,KeyError): db.session.rollback(); flash("Marks must be within the exam maximum.","danger")
        return redirect("/exams")
    @app.route("/notices",methods=["GET","POST"])
    @login_required
    def notices():
        if request.method=="POST":
            if current_user.role not in ("admin","faculty"): abort(403)
            title=request.form.get("title","").strip(); body=request.form.get("body","").strip(); audience=request.form.get("audience","all")
            if title and body and audience in ("all","student","faculty"):
                db.session.add(Notice(title=title,body=body,audience=audience,author_id=current_user.id)); db.session.commit(); flash("Notice published.","success")
            return redirect("/notices")
        q=Notice.query
        if current_user.role!="admin": q=q.filter(Notice.audience.in_(["all",current_user.role]))
        return page("Notices","""<h1 class='h3 mb-3'>Institution notices</h1>{% if current_user.role in ['admin','faculty'] %}<div class='card p-3 mb-4'><form method='post'><input type='hidden' name='csrf_token' value='{{csrf_token()}}'><div class='row g-2'><div class='col-md-5'><input class='form-control' name='title' placeholder='Title' required></div><div class='col-md-3'><select class='form-select' name='audience'><option value='all'>Everyone</option><option value='student'>Students</option><option value='faculty'>Faculty</option></select></div><div class='col-12'><textarea class='form-control' name='body' placeholder='Announcement' required></textarea></div><div class='col-12'><button class='btn btn-primary'>Publish</button></div></div></form></div>{% endif %}<div class='row g-3'>{% for n in notices %}<div class='col-md-6'><div class='card p-3'><small class='text-secondary'>{{n.audience|title}} · {{n.created_at.strftime('%d %b %Y')}}</small><h5 class='mt-2'>{{n.title}}</h5><p>{{n.body}}</p></div></div>{% else %}<p>No notices.</p>{% endfor %}</div>""",notices=q.order_by(Notice.created_at.desc()).all())
    @app.errorhandler(403)
    def forbidden(e): return page("Access denied","<div class='text-center py-5'><h1>403</h1><p>You do not have permission to access this page.</p></div>"),403
    @app.errorhandler(404)
    def missing(e): return page("Not found","<div class='text-center py-5'><h1>404</h1><p>Page not found.</p></div>"),404
    return app
