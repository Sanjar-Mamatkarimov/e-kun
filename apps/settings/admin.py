from django.contrib import admin
from apps.settings.models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
  list_display = (
      'school_name',
      'school_subtitle',
      'logo',
      'footer_text',
      'is_registration_open',
  )

  def has_add_permission(self, request):
    if self.model.objects.exists():
      return False
    return super().has_add_permission(request)