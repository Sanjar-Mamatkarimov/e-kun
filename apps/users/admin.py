from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
  model = User
  list_display = (
      'username',
      'full_name',
      'role',
      'subject',
      'student_class',
      'phone',
      'is_staff',
  )
  list_filter = ('role', 'subject', 'student_class', 'is_staff')
  fieldsets = UserAdmin.fieldsets + (
      (
          'Данные музыкальной школы',
          {
              'fields': (
                  'role',
                  'full_name',
                  'phone',
                  'subject',
                  'student_class',
                  'birth_date',
                  'subjects',
                  'students',
              )
          },
      ),
  )
  filter_horizontal = (
      'students',
      'groups',
      'user_permissions',
  )