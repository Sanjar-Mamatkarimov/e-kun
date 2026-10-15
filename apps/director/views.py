from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import EventAnnouncement
from .serializers import (
    EventAnnouncementSerializer,
    StudentSerializer,
    TeacherCreateSerializer,
    TeacherSerializer,
)

User = get_user_model()


class DirectorDashboardStatsView(APIView):
  """Статистика для Дашборда директора"""

  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    if request.user.role != 'director':
      return Response({'detail': 'Доступ запрещен.'}, status=403)

    return Response({
        'teachers_count': User.objects.filter(role='teacher').count(),
        'students_count': User.objects.filter(role='student').count(),
        'events_count': EventAnnouncement.objects.count(),
        'average_grade': 4.4,
        'attendance_percentage': 78,
    })


class EventAnnouncementViewSet(viewsets.ModelViewSet):
  """Управление концертами и анонсами"""

  queryset = EventAnnouncement.objects.all()
  serializer_class = EventAnnouncementSerializer
  permission_classes = [permissions.IsAuthenticated]

  def perform_create(self, serializer):
    serializer.save(created_by=self.request.user)


class TeacherManagementViewSet(viewsets.ModelViewSet):
  """Управление преподавателями"""

  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return User.objects.filter(role='teacher').prefetch_related('students')

  def get_serializer_class(self):
    if self.action in ['create', 'update', 'partial_update']:
      return TeacherCreateSerializer
    return TeacherSerializer

  def perform_create(self, serializer):
    password = serializer.validated_data.pop('password', 'defaultpassword123')
    user = serializer.save(role='teacher')
    user.set_password(password)
    user.save()

  @action(detail=True, methods=['post'], url_path='assign-students')
  def assign_students(self, request, pk=None):
    teacher = self.get_object()
    student_ids = request.data.get('student_ids', [])
    students = User.objects.filter(id__in=student_ids, role='student')
    teacher.students.set(students)
    return Response({'status': 'Ученики привязаны.'}, status=status.HTTP_200_OK)


class StudentManagementViewSet(viewsets.ModelViewSet):
  """Управление реестром учеников"""

  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    queryset = User.objects.filter(role='student').prefetch_related('teachers')
    # Фильтрация по классу, если передана в query-параметрах
    student_class = self.request.query_params.get('class')
    if student_class:
      queryset = queryset.filter(student_class=student_class)
    return queryset

  serializer_class = StudentSerializer

  def perform_create(self, serializer):
    # Автогенерация логина и временного пароля для ученика, если они не указаны
    username = f'student_{User.objects.filter(role="student").count() + 1}'
    password = 'studentpassword123'
    user = serializer.save(role='student', username=username)
    user.set_password(password)
    user.save()