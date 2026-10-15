from apps.director.models import EventAnnouncement
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.teachers.models import (
    GradeJournal,
    Homework,
    LessonSchedule,
    RepertoireItem,
    TermGrade,
)
from apps.teachers.serializers import (
    GradeJournalSerializer,
    HomeworkSerializer,
    LessonScheduleSerializer,
    RepertoireItemSerializer,
    TermGradeSerializer,
)


class StudentDashboardStatsView(APIView):
  """Статистика и афиша для главной страницы ученика[cite: 25]"""

  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    student = request.user
    if student.role != 'student':
      return Response({'detail': 'Доступ запрещен.'}, status=403)

    # Подсчет оценок и пропусков ученика
    journals = GradeJournal.objects.filter(student=student)
    grades_count = journals.exclude(grade__isnull=True).count()
    missed_count = journals.filter(attendance='Н/Б').count()
    homeworks_count = Homework.objects.filter(student=student).count()

    events = EventAnnouncement.objects.all()[:3]
    events_data = [
        {
            'id': e.id,
            'title': e.title,
            'date': e.date,
            'time': e.time,
            'location': e.location,
            'description': e.description,
        }
        for e in events
    ]

    return Response({
        'full_name': student.full_name or student.username,
        'average_grade': 4.8,  # Динамический или расчетный средний балл[cite: 25]
        'grades_count': grades_count,
        'missed_count': missed_count,
        'homeworks_count': homeworks_count,
        'upcoming_events': events_data,
    })


class StudentDiaryView(APIView):
  """Электронный дневник ученика (оценки и посещаемость по предметам)[cite: 25, 26]"""

  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    student = request.user
    if student.role != 'student':
      return Response({'detail': 'Доступ запрещен.'}, status=403)

    journals = GradeJournal.objects.filter(student=student).order_by('-date')
    serializer = GradeJournalSerializer(journals, many=True)
    return Response(serializer.data)


class StudentTermGradesView(viewsets.ReadOnlyModelViewSet):
  """Просмотр четвертных оценок ученика[cite: 27]"""

  serializer_class = TermGradeSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return TermGrade.objects.filter(student=self.request.user)


class StudentRepertoireView(viewsets.ReadOnlyModelViewSet):
  """Просмотр своего репертуарного плана[cite: 28]"""

  serializer_class = RepertoireItemSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return RepertoireItem.objects.filter(student=self.request.user)


class StudentHomeworksView(viewsets.ReadOnlyModelViewSet):
  """Просмотр домашних заданий и скачивание файлов[cite: 29]"""

  serializer_class = HomeworkSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return Homework.objects.filter(student=self.request.user)


class StudentScheduleView(viewsets.ReadOnlyModelViewSet):
  """Просмотр личного расписания занятий[cite: 30]"""

  serializer_class = LessonScheduleSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return LessonSchedule.objects.filter(student=self.request.user)