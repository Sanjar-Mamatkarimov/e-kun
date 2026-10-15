from django.urls import path

from . import views

urlpatterns = [
    # --- Аутентификация ---
    path('auth/login/', views.login, name='api-login'),
    path('auth/refresh/', views.RefreshView.as_view(), name='api-refresh'),
    path('auth/me/', views.me, name='api-me'),

    # --- Директор ---
    path('director/stats/', views.director_stats, name='api-director-stats'),
    path(
        'director/student-statistics/',
        views.director_student_statistics,
        name='api-director-student-statistics',
    ),

    # --- Реестры (директор) ---
    path('teachers/', views.teachers, name='api-teachers'),
    path('teachers/<int:pk>/', views.teacher_detail, name='api-teacher-detail'),
    path('students/', views.students, name='api-students'),
    path('students/<int:pk>/', views.student_detail, name='api-student-detail'),

    # --- Мероприятия и справочники ---
    path('events/', views.events, name='api-events'),
    path('events/<int:pk>/', views.event_detail, name='api-event-detail'),
    path('subjects/', views.subjects, name='api-subjects'),

    # --- Преподаватель ---
    path('teacher/students/', views.teacher_students, name='api-teacher-students'),
    path(
        'teacher/student-statistics/',
        views.teacher_student_statistics,
        name='api-teacher-student-statistics',
    ),
    path('teacher/schedule/', views.teacher_schedule, name='api-teacher-schedule'),
    path(
        'teacher/schedule/<int:pk>/',
        views.teacher_schedule_detail,
        name='api-teacher-schedule-detail',
    ),
    path(
        'teacher/quarter-grades/',
        views.teacher_quarter_grades,
        name='api-teacher-quarter-grades',
    ),

    # --- Журнал / репертуар / домашние задания ---
    path('journal/', views.journal, name='api-journal'),
    path('journal/<int:pk>/', views.journal_detail, name='api-journal-detail'),
    path('repertoire/', views.repertoire, name='api-repertoire'),
    path('repertoire/<int:pk>/', views.repertoire_detail, name='api-repertoire-detail'),
    path('homework/', views.homework, name='api-homework'),
    path('homework/<int:pk>/', views.homework_detail, name='api-homework-detail'),

    # --- Ученик ---
    path('student/dashboard/', views.student_dashboard, name='api-student-dashboard'),
    path('student/grades/', views.student_grades, name='api-student-grades'),
    path(
        'student/quarter-grades/',
        views.student_quarter_grades,
        name='api-student-quarter-grades',
    ),
    path('student/repertoire/', views.student_repertoire, name='api-student-repertoire'),
    path('student/homework/', views.student_homework, name='api-student-homework'),
    path('student/schedule/', views.student_schedule, name='api-student-schedule'),
]
