from django.urls import path
from apps.settings.views import SiteSettingsView

urlpatterns = [
    path('config/', SiteSettingsView.as_view(), name='site-settings'),
]