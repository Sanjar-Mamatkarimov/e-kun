from django.core import exceptions
from django.db import models


class SiteSettings(models.Model):
  school_name = models.CharField(
      max_length=255,
      default='Э-Күндүлүк',
      verbose_name='Название системы / школы',
  )
  school_subtitle = models.CharField(
      max_length=255,
      default='Электронный дневник музыкальной школы',
      verbose_name='Подзаголовок',
  )
  logo = models.ImageField(
      upload_to='logos/',
      blank=True,
      null=True,
      verbose_name='Логотип школы (иконка)',
  )
  footer_text = models.CharField(
      max_length=255,
      default='© 2026 Музыкальная школа. Все права защищены.',
      verbose_name='Текст в футере (подвале)',
  )
  is_registration_open = models.BooleanField(
      default=False, verbose_name='Открыта ли регистрация'
  )

  def save(self, *args, **kwargs):
    if not self.pk and SiteSettings.objects.exists():
      raise exceptions.ValidationError(
          'Настройки сайта уже существуют. Вы можете отредактировать'
          ' существующие.'
      )
    super().save(*args, **kwargs)

  def __str__(self):
    return f'Настройки платформы: {self.school_name}'