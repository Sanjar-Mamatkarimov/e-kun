from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import GradeJournal, Homework, LessonSchedule, RepertoireItem, TermGrade

User = get_user_model()


class TeacherStatsSerializer(serializers.Serializer):
  """Статистика для главной страницы учителя"""

  my_students_count = serializers.IntegerField()
  events_count = serializers.IntegerField()
  average_grade = serializers.FloatField()
  schedules_count = serializers.IntegerField()


class LessonScheduleSerializer(serializers.ModelSerializer):
  student_name = serializers.CharField(
      source='student.full_name', read_only=True
  )

  class Meta:
    model = LessonSchedule
    fields = [
        'id',
        'student',
        'student_name',
        'subject',
        'day_of_week',
        'time',
        'room',
        'lesson_type',
    ]


class GradeJournalSerializer(serializers.ModelSerializer):

  class Meta:
    model = GradeJournal
    fields = [
        'id',
        'teacher',
        'student',
        'subject',
        'date',
        'attendance',
        'grade',
        'comment',
    ]
    read_only_fields = ['teacher']


class TermGradeSerializer(serializers.ModelSerializer):
  student_name = serializers.CharField(
      source='student.full_name', read_only=True
  )

  class Meta:
    model = TermGrade
    fields = [
        'id',
        'student',
        'student_name',
        'subject',
        'term',
        'academic_year',
        'final_grade',
    ]
    read_only_fields = ['teacher']


class RepertoireItemSerializer(serializers.ModelSerializer):
  student_name = serializers.CharField(
      source='student.full_name', read_only=True
  )

  class Meta:
    model = RepertoireItem
    fields = [
        'id',
        'student',
        'student_name',
        'teacher',
        'title',
        'composer',
        'subject',
        'status',
    ]
    read_only_fields = ['teacher']


class HomeworkSerializer(serializers.ModelSerializer):
  student_name = serializers.CharField(
      source='student.full_name', read_only=True
  )

  class Meta:
    model = Homework
    fields = [
        'id',
        'student',
        'student_name',
        'subject',
        'topic',
        'description',
        'due_date',
        'file',
        'created_at',
    ]
    read_only_fields = ['teacher', 'created_at']