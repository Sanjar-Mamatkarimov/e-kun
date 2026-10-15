from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.users.serializers import CustomTokenObtainPairSerializer, UserSerializer


class LoginView(TokenObtainPairView):
  """Эндпоинт для входа (получение JWT токенов и роли)"""

  serializer_class = CustomTokenObtainPairSerializer


class CurrentUserView(APIView):
  """Эндпоинт для проверки текущего токена и получения данных вошедшего юзера"""

  permission_classes = [IsAuthenticated]

  def get(self, request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)