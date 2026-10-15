from apps.director.models import EventAnnouncement
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import GradeJournal, Homework, LessonSchedule, RepertoireItem, TermGrade
from .serializers import (
    GradeJournalSerializer,
    HomeworkSerializer,
    LessonScheduleSerializer,
    RepertoireItemSerializer,
    TermGradeSerializer,
)


class TeacherDashboardStatsView(APIView):
  """Статистика для главной страницы учителя[cite: 17]"""

  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    teacher = request.user
    if teacher.role != 'teacher':
      return Response({'detail': 'Доступ запрещен.'}, status=403)

    my_students_count = teacher.students.count()
    events_count = EventAnnouncement.objects.count()
    schedules_count = LessonSchedule.objects.filter(teacher=teacher).count()

    return Response({
        'my_students_count': my_students_count,
        'events_count': events_count,
        'average_grade': 4.4,
        'schedules_count': schedules_count,
    })


class TeacherStudentsViewSet(viewsets.ReadOnlyModelViewSet):
  """Просмотр закрепленных за учителем учеников[cite: 18]"""

  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return self.request.user.students.all()


class LessonScheduleViewSet(viewsets.ModelViewSet):
  """Управление расписанием занятий[cite: 21]"""

  serializer_class = LessonScheduleSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return LessonSchedule.objects.filter(teacher=self.request.user)

  def perform_create(self, serializer):
    serializer.save(teacher=self.request.user)


class GradeJournalViewSet(viewsets.ModelViewSet):
  """Ведение журнала оценок и посещаемости[cite: 19]"""

  serializer_class = GradeJournalSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return GradeJournal.objects.filter(teacher=self.request.user)

  def perform_create(self, serializer):
    serializer.save(teacher=self.request.user)


class TermGradeViewSet(viewsets.ModelViewSet):
  """Итоги четверти[cite: 20]"""

  serializer_class = TermGradeSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return TermGrade.objects.filter(teacher=self.request.user)

  def perform_create(self, serializer):
    serializer.save(teacher=self.request.user)


class RepertoireItemViewSet(viewsets.ModelViewSet):
  """Репертуарный план учеников[cite: 22, 23]"""

  serializer_class = RepertoireItemSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return RepertoireItem.objects.filter(teacher=self.request.user)

  def perform_create(self, serializer):
    serializer.save(teacher=self.request.user)


class HomeworkViewSet(viewsets.ModelViewSet):
  """Домашние задания[cite: 24]"""

  serializer_class = HomeworkSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return Homework.objects.filter(teacher=self.request.user)

  def perform_create(self, serializer):
    serializer.save(teacher=self.request.user)