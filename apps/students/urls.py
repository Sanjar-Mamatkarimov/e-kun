from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    StudentDashboardStatsView,
    StudentDiaryView,
    StudentHomeworksView,
    StudentRepertoireView,
    StudentScheduleView,
    StudentTermGradesView,
)

router = DefaultRouter()
router.register(
    'term-grades', StudentTermGradesView, basename='student-term-grades'
)
router.register(
    'repertoire', StudentRepertoireView, basename='student-repertoire'
)
router.register('homeworks', StudentHomeworksView, basename='student-homeworks')
router.register('schedule', StudentScheduleView, basename='student-schedule')

urlpatterns = [
    path(
        'dashboard/',
        StudentDashboardStatsView.as_view(),
        name='student-dashboard',
    ),
    path('diary/', StudentDiaryView.as_view(), name='student-diary'),
    path('', include(router.urls)),
]