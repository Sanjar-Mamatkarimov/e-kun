from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.users.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
  """Добавляет роль и ФИО пользователя в JSON-ответ при логине"""

  @classmethod
  def get_token(cls, user):
    token = super().get_token(user)
    token['role'] = user.role
    token['username'] = user.username
    return token

  def validate(self, attrs):
    data = super().validate(attrs)
    data['role'] = self.user.role
    data['username'] = self.user.username
    data['full_name'] = self.user.full_name or self.user.username
    return data


class UserSerializer(serializers.ModelSerializer):
  """Сериализатор для отображения данных пользователя"""

  role_display = serializers.CharField(
      source='get_role_display', read_only=True
  )

  class Meta:
    model = User
    fields = ['id', 'username', 'full_name', 'role', 'role_display']