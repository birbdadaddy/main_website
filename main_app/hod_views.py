import json
import requests
import os
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from django.db.models import Q
from django.conf import settings

from .forms import *
from .models import *


def bprint(var):
    for i in range(10):
        print('')
    print(var)
    for i in range(10):
        print('')

def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    subjects = Subject.objects.all()
    total_subject = subjects.count()
    total_course = Course.objects.all().count()
    total_classes = Class.objects.all().count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name[:7])
        attendance_list.append(attendance_count)

    # Total Subjects and students in Each Course
    classes_all = Course.objects.all()
    class_name_list = []
    subject_count_list = []
    student_count_list_in_class = []

    for class_obj in classes_all:
        students = Student.objects.filter(class_obj=class_obj).count()
        class_name_list.append(class_obj.name)
        student_count_list_in_class.append(students)
    
    subject_all = Class.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        student_count = Student.objects.filter(class_obj=subject).count()
        # student_count = Student.objects.filter(id=course.id).count()
        subject_list.append(f"{subject.year} {subject.type} {subject.name}")
        student_count_list_in_subject.append(student_count)

    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Student.objects.all()
    for student in students:
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leave = LeaveReportStudent.objects.filter(student_id=student.id, status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leave+absent)
        student_name_list.append(student.admin.first_name)

    context = {
        'page_title': "Administrative Dashboard",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_classes': total_classes,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list,
        'student_attendance_present_list': student_attendance_present_list,
        'student_attendance_leave_list': student_attendance_leave_list,
        "student_name_list": student_name_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "student_count_list_in_course": student_count_list_in_class,
        "course_name_list": class_name_list,

    }
    return render(request, 'hod_template/home_content.html', context)


def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Staff'}
    
    if request.method == 'POST':
        if form.is_valid():
            # Get form data
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            passport = request.FILES.get('profile_pic')
            
            # Save profile picture
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            
            # Create user instance
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, 
                    first_name=first_name, last_name=last_name, 
                    profile_pic=passport_url, gender=gender, address=address
                )
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
                return redirect(reverse('add_staff'))

            # Save selected classes
            class_objs = form.cleaned_data.get('class_obj')
            for class_obj in class_objs:
                user.staff.class_obj.add(class_obj)

            messages.success(request, "Successfully Added")
            return redirect(reverse('add_staff'))

        else:
            messages.error(request, "Please fulfill all requirements")

    return render(request, 'hod_template/add_staff_template.html', context)


def add_student(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Add Student'}
    if request.method == 'POST':
        if student_form.is_valid():
            first_name = student_form.cleaned_data.get('first_name')
            last_name = student_form.cleaned_data.get('last_name')
            address = student_form.cleaned_data.get('address')
            email = student_form.cleaned_data.get('email')
            massar = student_form.cleaned_data.get('massar')
            gender = student_form.cleaned_data.get('gender')
            password = student_form.cleaned_data.get('password')
            class_obj = student_form.cleaned_data.get('class_obj')
            session = student_form.cleaned_data.get('session')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.massar = massar
                user.gender = gender
                user.address = address
                user.student.session = session
                user.student.class_obj = class_obj
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_student'))
            except:
                messages.error(request, "An Error Occured While Adding Student")
        else:
            messages.error(request, "Could Not Add Student")
    return render(request, 'hod_template/add_student_template.html', context)

def add_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():

            year = form.cleaned_data['year']
            class_type = form.cleaned_data['type']
            class_name = form.cleaned_data['name']
            
            print('checking')
            # Check for duplicate class
            if Class.objects.filter(year=year, type=class_type, name=class_name).exists():
                print("ERROR")
                messages.error(request, "Class already exists.")
            else:
                Class.objects.create(year=year, type=class_type, name=class_name)
                messages.success(request, "Successfully Added")

            return redirect('add_class')

    else:
        form = ClassForm()

    context = {
        'form': form,
        'page_title': 'Add Class'
    }

    return render(request, 'hod_template/add_class_template.html', context)

def add_course(request):
    form = CourseForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course()
                course.name = name
                course.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_course'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_course_template.html', context)

def add_subject(request):
    form = SubjectForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject()
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_subject'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_subject_template.html', context)

def add_time_table(request):
    form = TimeTableForm(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'page_title': 'Add Time Table'
    }
    if request.method == 'POST':
        if form.is_valid():
            class_obj = form.cleaned_data.get('class_obj')
            time_table = request.FILES['time_table']
            fs = FileSystemStorage()
            filename = fs.save(time_table.name, time_table)
            time_table_url = fs.url(filename)
            try:
                time_table = TimeTable.objects.create(class_obj=class_obj, time_table=time_table_url)
                time_table.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_time_table'))
            except:
                messages.error(request, "Could Not Add")
                return redirect(reverse('add_time_table'))
    
    return render(request, 'hod_template/add_time_table.html', context)

def manage_staff(request, search_query=False):
    if search_query != False:
        search_query = search_query.replace('-', ' ')
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': 'Manage Staff',
        'search_query': search_query
    }
    return render(request, "hod_template/manage_staff.html", context)

def manage_student(request, search_query=False):
    if search_query != False:
        search_query = search_query.replace('-', ' ')
    students = CustomUser.objects.filter(user_type=3)
    context = {
        'students': students,
        'page_title': 'Manage Students',
        'search_query': search_query
    }
    return render(request, "hod_template/manage_student.html", context)

def manage_class(request):
    year1 = Class.objects.filter(year=1)
    year2 = Class.objects.filter(year=2)
    year3 = Class.objects.filter(year=3)
    years = [year1, year2, year3]
    context = {
        'years': years,
        'page_title': 'Manage Classes'
    }
    return render(request, "hod_template/manage_class.html", context)

def manage_course(request):
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Manage Courses'
    }
    return render(request, "hod_template/manage_course.html", context)


def manage_subject(request):
    subjects = Subject.objects.all()
    context = {
        'subjects': subjects,
        'page_title': 'Manage Subjects'
    }
    return render(request, "hod_template/manage_subject.html", context)

def manage_time_table(request):
    classes = Class.objects.all()
    context = {
        'classes': classes,
        'page_title': 'Manage Time Tables'
    }
    return render(request, "hod_template/manage_time_tables.html", context)


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    user = CustomUser.objects.get(id=staff.admin.id)
    
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            # Extract form data
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            passport = request.FILES.get('profile_pic') or None
            class_obj = form.cleaned_data.get('class_obj')
            
            try:
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                staff.class_obj.set(class_obj)
                user.save()
                staff.save()
                
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, f"Could Not Update: {e}")
        else:
            messages.error(request, "Please fill the form properly")
    else:
        form = StaffForm(instance=staff, initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'address': user.address,
            'email': user.email,
            'gender': user.gender,
            'profile_pic': user.profile_pic,  
        })
    
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Edit Staff'
    }
    
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        'form': form,
        'student_id': student_id,
        'page_title': 'Edit Student'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            session = form.cleaned_data.get('session')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                student.session = session
                user.gender = gender
                user.address = address
                student.course = course
                user.save()
                student.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_student', args=[student_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "hod_template/edit_student_template.html", context)

def edit_class(request, class_id):
    instance = get_object_or_404(Class, id=class_id)
    form = ClassForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'class_id': class_id,
        'page_title': 'Edit Class'
    }
    if request.method == 'POST':
        if form.is_valid():
            class_year = form.cleaned_data.get('year')
            class_type = form.cleaned_data.get('type')
            class_name = form.cleaned_data.get('name')
            try:
                class_obj = Class.objects.get(id=class_id)

                class_obj.year = class_year
                class_obj.type = class_type
                class_obj.name = class_name
                class_obj.save()

                Student.objects.filter(class_obj=instance).update(class_obj=class_obj)
                TimeTable.objects.filter(class_obj=instance).update(class_obj=class_obj)
                Staff.objects.filter(class_obj=instance).update(class_obj=class_obj)

                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_class_template.html', context)

def edit_course(request, course_id):
    instance = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Edit Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course.objects.get(id=course_id)
                course.name = name
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)


def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Edit Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject.objects.get(id=subject_id)
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'hod_template/edit_subject_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Created")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Manage Sessions'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Edit Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Session Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def student_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStudent.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Student Feedback Messages'
        }
        return render(request, 'hod_template/student_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStudent, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def staff_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Staff Feedback Messages'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Staff'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_student_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Students'
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    subjects = Subject.objects.all()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'View Attendance'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify(request):
    notifications = Notification.objects.all()
    notifications = notifications[::-1]
    context = {
        'notifications': notifications,
        'page_title': "Send Notification",
    }
    return render(request, "hod_template/notification.html", context)

@csrf_exempt
def get_classes(request):
    year = request.POST.get('year')
    class_type = request.POST.get('class_type')
    try:
        filter_params = {}
        if year != "*":
            filter_params['year'] = year

        if class_type != "*":
            filter_params['type'] = class_type

        classes = Class.objects.filter(**filter_params)

        classes_data = []
        for class_obj in classes:
            data = {
                    "id": class_obj.id,
                    "name": class_obj.full_class_name(' ')
                    }
            classes_data.append(data)

        return JsonResponse(json.dumps(classes_data), content_type='application/json', safe=False)
    except Exception as e:
        return None

@csrf_exempt
def send_notification(request):
    user_type = request.POST.get('user_type')
    year = request.POST.get('year')
    class_type = request.POST.get('class_type')
    class_obj = request.POST.get('class_obj')
    message = request.POST.get('message')

    if user_type != "*":
        user_type = int(user_type)
    
    filter_params = {}
    if class_obj != "*":
        classes = Class.objects.filter(id=int(class_obj))
    else:
        if year != "*":
            filter_params['year'] = year

        if class_type != "*":
            filter_params['type'] = class_type

        classes = Class.objects.filter(**filter_params)
        filter_params = {}

    user_ids = []
    for class_obj in classes:
        staff_users = []
        student_users = []
        filter_params['class_obj'] = class_obj

        if user_type == 2:
            staff_users = Staff.objects.filter(**filter_params).values_list('admin_id', flat=True)
        elif user_type == 3:
            student_users = Student.objects.filter(**filter_params).values_list('admin_id', flat=True)
        else:
            staff_users = Staff.objects.filter(**filter_params).values_list('admin_id', flat=True)
            student_users = Student.objects.filter(**filter_params).values_list('admin_id', flat=True)

        user_ids += list(staff_users) + list(student_users)

    users = CustomUser.objects.filter(id__in=user_ids)

    try:
        for user in users:
            url = "https://fcm.googleapis.com/fcm/send"
            body = {
                'notification': {
                    'title': "Student Management System",
                    'body': message,
                    'click_action': reverse('staff_view_notification'),
                    'icon': static('dist/img/AdminLTELogo.png')
                },
                'to': user.fcm_token
            }
            headers = {'Authorization':
                    'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                    'Content-Type': 'application/json'}
            requests.post(url, data=json.dumps(body), headers=headers)

        notification = Notification.objects.create(message=message)
        notification.users.add(*users)

        messages.success(request, "Notification sent successfully!")
        return HttpResponse("True")
    except Exception as e:
        messages.error(request, "Error occurred while sending notification")
        return HttpResponse("False")


def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    staff = get_object_or_404(Staff, staff__id=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff'))


def delete_student(request, student_id):
    student = get_object_or_404(CustomUser, student__id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect(reverse('manage_student'))


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some students are assigned to this course already. Kindly change the affected student course and try again")
    return redirect(reverse('manage_course'))

def delete_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    try:
        class_obj.delete()
        messages.success(request, "Class deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some students are assigned to this class already.")
    return redirect(reverse('manage_class'))

def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect(reverse('manage_subject'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Session deleted successfully!")
    except Exception:
        messages.error(
            request, "There are students assigned to this session. Please move them to another session.")
    return redirect(reverse('manage_session'))

def delete_time_table(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    time_table = TimeTable.objects.filter(class_obj=class_obj)
    time_table.delete()
    messages.success(request, "Time table deleted successfully!")
    return redirect(reverse('manage_time_table'))