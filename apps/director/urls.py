from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    DirectorDashboardStatsView,
    EventAnnouncementViewSet,
    StudentManagementViewSet,
    TeacherManagementViewSet,
)

router = DefaultRouter()
router.register(
    'events', EventAnnouncementViewSet, basename='event-announcement'
)
router.register('teachers', TeacherManagementViewSet, basename='teacher-manage')
router.register('students', StudentManagementViewSet, basename='student-manage')

urlpatterns = [
    path(
        'dashboard/stats/',
        DirectorDashboardStatsView.as_view(),
        name='dashboard-stats',
    ),
    path('', include(router.urls)),
]