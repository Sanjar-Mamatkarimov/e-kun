from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    GradeJournalViewSet,
    HomeworkViewSet,
    LessonScheduleViewSet,
    RepertoireItemViewSet,
    TeacherDashboardStatsView,
    TeacherStudentsViewSet,
    TermGradeViewSet,
)

router = DefaultRouter()
router.register(
    'my-students',
    TeacherStudentsViewSet,
    basename='teacher-my-students',
)
router.register('schedules', LessonScheduleViewSet, basename='teacher-schedule')
router.register('journal', GradeJournalViewSet, basename='teacher-journal')
router.register('term-grades', TermGradeViewSet, basename='teacher-term-grades')
router.register(
    'repertoire', RepertoireItemViewSet, basename='teacher-repertoire'
)
router.register('homeworks', HomeworkViewSet, basename='teacher-homeworks')

urlpatterns = [
    path('dashboard/stats/', TeacherDashboardStatsView.as_view(), name='teacher-dashboard-stats'),
    path('', include(router.urls)),
]