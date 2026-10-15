from django.conf import settings
from django.db import models


class LessonSchedule(models.Model):
  """Расписание занятий учителя"""

  DAYS_OF_WEEK = [
      ('Monday', 'Понедельник'),
      ('Tuesday', 'Вторник'),
      ('Wednesday', 'Среда'),
      ('Thursday', 'Четверг'),
      ('Friday', 'Пятница'),
      ('Saturday', 'Суббота'),
      ('Sunday', 'Воскресенье'),
  ]

  teacher = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'teacher'},
      related_name='teacher_schedules',  # Уникальное имя
      verbose_name='Учитель',
  )
  student = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'student'},
      related_name='student_schedules',  # Уникальное имя
      verbose_name='Ученик',
  )
  subject = models.CharField(max_length=100, verbose_name='Предмет')
  day_of_week = models.CharField(
      max_length=20, choices=DAYS_OF_WEEK, verbose_name='День недели'
  )
  time = models.TimeField(verbose_name='Время')
  room = models.CharField(max_length=50, verbose_name='Кабинет')
  lesson_type = models.CharField(
      max_length=50, default='Индивидуальное', verbose_name='Тип занятия'
  )

  class Meta:
    verbose_name = 'Расписание занятий'
    verbose_name_plural = 'Расписание занятий'


class GradeJournal(models.Model):
  """Электронный журнал: посещаемость и текущие оценки"""

  teacher = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'teacher'},
      related_name='teacher_grades',  # Уникальное имя
      verbose_name='Учитель',
  )
  student = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'student'},
      related_name='student_grades',  # Уникальное имя
      verbose_name='Ученик',
  )
  subject = models.CharField(max_length=100, verbose_name='Предмет')
  date = models.DateField(verbose_name='Дата урока')
  attendance = models.CharField(
      max_length=10, blank=True, null=True, verbose_name='Посещаемость (Б/Н-Б)'
  )
  grade = models.PositiveIntegerField(
      blank=True, null=True, verbose_name='Оценка (1-5)'
  )
  comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')

  class Meta:
    verbose_name = 'Запись в журнале'
    verbose_name_plural = 'Журнал оценок'


class TermGrade(models.Model):
  """Итоги четверти / периода"""

  teacher = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'teacher'},
      related_name='teacher_term_grades',  # Уникальное имя
      verbose_name='Учитель',
  )
  student = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'student'},
      related_name='student_term_grades',  # Уникальное имя
      verbose_name='Ученик',
  )
  subject = models.CharField(max_length=100, verbose_name='Предмет')
  term = models.CharField(
      max_length=50, default='1 четверть', verbose_name='Четверть / Период'
  )
  academic_year = models.CharField(
      max_length=20, default='2026/2027', verbose_name='Учебный год'
  )
  final_grade = models.PositiveIntegerField(
      blank=True, null=True, verbose_name='Итоговая оценка учителя'
  )

  class Meta:
    verbose_name = 'Итог четверти'
    verbose_name_plural = 'Итоги четвертей'


class QuarterGrade(models.Model):
  """Итоговая (четвертная) оценка, которую подтверждает преподаватель.

  Хранит период четверти, чтобы фронтенд мог показать даты и год.
  """

  teacher = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'teacher'},
      related_name='teacher_quarter_grades',
      verbose_name='Учитель',
  )
  student = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'student'},
      related_name='student_quarter_grades',
      verbose_name='Ученик',
  )
  subject = models.CharField(max_length=100, verbose_name='Предмет')
  school_year = models.CharField(max_length=20, verbose_name='Учебный год')
  quarter = models.PositiveIntegerField(verbose_name='Четверть (1-4)')
  start_date = models.DateField(verbose_name='Начало четверти')
  end_date = models.DateField(verbose_name='Конец четверти')
  grade = models.PositiveIntegerField(verbose_name='Итоговая оценка (1-5)')

  class Meta:
    verbose_name = 'Четвертная оценка'
    verbose_name_plural = 'Четвертные оценки'
    unique_together = ('teacher', 'student', 'subject', 'school_year', 'quarter')

  def __str__(self):
    return (
        f'{self.student} — {self.subject} — {self.school_year}'
        f' {self.quarter} четв.: {self.grade}'
    )


class RepertoireItem(models.Model):
  """Репертуарный план ученика"""

  STATUS_CHOICES = [
      ('In progress', 'В работе'),
      ('Ready', 'Готово к зачету'),
      ('Passed', 'Сдано'),
  ]

  student = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'student'},
      related_name='student_repertoire',
      verbose_name='Ученик',
  )
  teacher = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'teacher'},
      related_name='teacher_repertoire',
      verbose_name='Преподаватель',
  )
  title = models.CharField(max_length=255, verbose_name='Название произведения')
  composer = models.CharField(max_length=255, verbose_name='Композитор')
  subject = models.CharField(max_length=100, verbose_name='Предмет')
  status = models.CharField(
      max_length=30,
      choices=STATUS_CHOICES,
      default='In progress',
      verbose_name='Статус',
  )

  class Meta:
    verbose_name = 'Произведение в репертуаре'
    verbose_name_plural = 'Репертуарный план'


class Homework(models.Model):
  """Домашние задания с возможностью прикрепления файлов"""

  teacher = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'teacher'},
      related_name='teacher_homeworks',
      verbose_name='Учитель',
  )
  student = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      limit_choices_to={'role': 'student'},
      related_name='student_homeworks',
      verbose_name='Ученик',
  )
  subject = models.CharField(max_length=100, verbose_name='Предмет')
  topic = models.CharField(max_length=255, verbose_name='Тема')
  description = models.TextField(blank=True, null=True, verbose_name='Описание')
  due_date = models.DateField(verbose_name='Срок сдачи')
  file = models.FileField(
      upload_to='homeworks/',
      blank=True,
      null=True,
      verbose_name='Файл (ноты/аудио)',
  )
  created_at = models.DateTimeField(
      auto_now_add=True, verbose_name='Дата отправки'
  )

  class Meta:
    verbose_name = 'Домашнее задание'
    verbose_name_plural = 'Домашние задания'