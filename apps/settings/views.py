from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.settings.models import SiteSettings
from .serializers import SiteSettingsSerializer

class SiteSettingsView(APIView):
  permission_classes = [AllowAny]

  def get(self, request):
    settings_obj, created = SiteSettings.objects.get_or_create(
        pk=1,
        defaults={
            'school_name': 'Э-Күндүлүк',
            'school_subtitle': 'Электронный дневник музыкальной школы',
            'footer_text': (
                '© 2026 Музыкальная школа. Все права защищены.'
            ),
        },
    )
    serializer = SiteSettingsSerializer(
        settings_obj, context={'request': request}
    )
    return Response(serializer.data)