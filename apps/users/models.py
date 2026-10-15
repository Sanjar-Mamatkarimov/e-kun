from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

  class Role(models.TextChoices):
    DIRECTOR = 'director', 'Директор'
    TEACHER = 'teacher', 'Учитель'
    STUDENT = 'student', 'Ученик'

  role = models.CharField(
      max_length=20,
      choices=Role.choices,
      default=Role.STUDENT,
      verbose_name='Роль',
  )
  full_name = models.CharField(
      max_length=255, blank=True, null=True, verbose_name='ФИО'
  )
  phone = models.CharField(
      max_length=50, blank=True, null=True, verbose_name='Телефон'
  )
  subject = models.CharField(
      max_length=100,
      blank=True,
      null=True,
      verbose_name='Предмет (для учителей)',
  )

  # Дополнительные поля для учеников
  student_class = models.CharField(
      max_length=50, blank=True, null=True, verbose_name='Класс (например, 3 класс)'
  )
  birth_date = models.DateField(
      blank=True, null=True, verbose_name='Дата рождения'
  )
  subjects = models.JSONField(
      default=list, blank=True, verbose_name='Предметы ученика'
  )

  # Связь преподавателей и учеников
  students = models.ManyToManyField(
      'self',
      symmetrical=False,
      blank=True,
      limit_choices_to={'role': 'student'},
      related_name='teachers',
      verbose_name='Ученики преподавателя',
  )

  def __str__(self):
    return (
        f'{self.full_name or self.username} ({self.get_role_display()})'
    )