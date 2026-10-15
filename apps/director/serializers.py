from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import EventAnnouncement

User = get_user_model()


class EventAnnouncementSerializer(serializers.ModelSerializer):

  class Meta:
    model = EventAnnouncement
    fields = [
        'id',
        'title',
        'description',
        'date',
        'time',
        'location',
        'created_at',
    ]


class TeacherSerializer(serializers.ModelSerializer):
  students_count = serializers.SerializerMethodField()

  class Meta:
    model = User
    fields = [
        'id',
        'username',
        'full_name',
        'subject',
        'phone',
        'students_count',
    ]

  def get_students_count(self, obj):
    return obj.students.count()


class TeacherCreateSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True)

  class Meta:
    model = User
    fields = ['username', 'password', 'full_name', 'subject', 'phone']


class StudentSerializer(serializers.ModelSerializer):
  teachers = serializers.SerializerMethodField()
  average_grade = serializers.SerializerMethodField()
  grades_count = serializers.SerializerMethodField()
  missed_classes = serializers.SerializerMethodField()
  teacher_ids = serializers.PrimaryKeyRelatedField(
      many=True,
      queryset=User.objects.filter(role='teacher'),
      write_only=True,
      source='teachers',
  )

  class Meta:
    model = User
    fields = [
        'id',
        'username',
        'full_name',
        'student_class',
        'birth_date',
        'subjects',
        'teachers',
        'teacher_ids',
        'average_grade',
        'grades_count',
        'missed_classes',
    ]

  def get_teachers(self, obj):
    return [{'id': t.id, 'full_name': t.full_name, 'subject': t.subject} for t in obj.teachers.all()]

  def get_average_grade(self, obj):
    return 4.8  # Заглушка, позже заменится реальными данными из журнала

  def get_grades_count(self, obj):
    return 4  # Заглушка количества оценок

  def get_missed_classes(self, obj):
    return 1  # Заглушка пропусков