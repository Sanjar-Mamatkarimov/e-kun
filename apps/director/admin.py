from django.contrib import admin
from .models import EventAnnouncement


@admin.register(EventAnnouncement)
class EventAnnouncementAdmin(admin.ModelAdmin):
  list_display = ('title', 'date', 'time', 'location', 'created_by', 'created_at')
  list_filter = ('date', 'location', 'created_by')
  search_fields = ('title', 'description', 'location')
  date_hierarchy = 'date'