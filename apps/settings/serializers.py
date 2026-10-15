from rest_framework import serializers
from apps.settings.models import SiteSettings

class SiteSettingsSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(read_only=True)

    class Meta:
        model = SiteSettings
        fields = ['school_name', 'school_subtitle', 'logo', 'footer_text', 'is_registration_open']
    