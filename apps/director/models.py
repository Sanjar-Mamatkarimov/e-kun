from django.conf import settings
from django.db import models


class EventAnnouncement(models.Model):
  title = models.CharField(max_length=255, verbose_name='Название мероприятия')
  description = models.TextField(
      blank=True, null=True, verbose_name='Описание / Программа'
  )
  date = models.DateField(verbose_name='Дата проведения')
  time = models.TimeField(verbose_name='Время проведения')
  location = models.CharField(
      max_length=255, verbose_name='Место проведения (зал/кабинет)'
  )
  created_by = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'director'},
      verbose_name='Создал (Директор)',
  )
  created_at = models.DateTimeField(
      auto_now_add=True, verbose_name='Дата создания'
  )

  class Meta:
    verbose_name = 'Концерт / Анонс'
    verbose_name_plural = 'Концерты и анонсы'
    ordering = ['date', 'time']

  def __str__(self):
    return f'{self.title} ({self.date})'