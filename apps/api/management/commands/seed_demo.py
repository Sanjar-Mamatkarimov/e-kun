"""Наполняет базу демонстрационными данными, совпадающими с mock.js.

После запуска можно войти тестовыми учётными записями:
    director / director  — Директор
    teacher  / teacher   — Преподаватель
    student  / student   — Ученик

Команда идемпотентна: повторный запуск не создаёт дубликаты.
"""

import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.director.models import EventAnnouncement
from apps.teachers.models import (
    GradeJournal,
    Homework,
    LessonSchedule,
    QuarterGrade,
    RepertoireItem,
)

User = get_user_model()


def make_user(username, password, role, full_name, **extra):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'role': role, 'full_name': full_name, **extra},
    )
    if created:
        user.role = role
        user.full_name = full_name
        for key, value in extra.items():
            setattr(user, key, value)
        user.set_password(password)
        user.save()
    return user


class Command(BaseCommand):
    help = 'Создаёт демонстрационные данные музыкальной школы.'

    @transaction.atomic
    def handle(self, *args, **options):
        # ---- Директор ----
        director = make_user(
            'director', 'director', 'director', 'Айгуль Смагулова'
        )

        # ---- Преподаватели ----
        teachers = [
            ('teacher', 'Дмитрий Ким', 'Специальность', '+7 701 111 22 33'),
            ('orlova', 'Марина Орлова', 'Сольфеджио', '+7 702 555 66 77'),
            ('volkov', 'Сергей Волков', 'Хор', '+7 705 888 99 00'),
            ('ahmetova', 'Гульнара Ахметова', 'Муз. литература', '+7 707 123 45 67'),
        ]
        teacher_objs = {}
        for login, full_name, subject, phone in teachers:
            teacher_objs[login] = make_user(
                login, login, 'teacher', full_name,
                subject=subject, phone=phone,
            )
        kim = teacher_objs['teacher']
        orlova = teacher_objs['orlova']
        volkov = teacher_objs['volkov']
        ahmetova = teacher_objs['ahmetova']

        # ---- Ученики ----
        students_data = [
            ('student', 'Алия Нурланова', '3 класс', '2013-04-12',
             ['Специальность', 'Сольфеджио', 'Хор'], [kim, orlova, volkov]),
            ('timur', 'Тимур Бекболатов', '3 класс', '2013-01-20',
             ['Специальность', 'Сольфеджио'], [kim]),
            ('sofia', 'София Ли', '4 класс', '2012-09-03',
             ['Специальность', 'Оркестр'], [kim]),
            ('daniyar', 'Данияр Сейтов', '2 класс', '2014-06-15',
             ['Специальность', 'Сольфеджио'], [orlova]),
            ('kamila', 'Камила Жумабай', '5 класс', '2011-11-28',
             ['Хор', 'Ансамбль'], [volkov]),
            ('amir', 'Амир Оспанов', '2 класс', '2014-03-08',
             ['Специальность', 'Хор'], [orlova]),
            ('eva', 'Ева Соколова', '6 класс', '2010-12-01',
             ['Муз. литература', 'Сольфеджио'], [ahmetova]),
        ]
        student_objs = {}
        for login, full_name, class_name, birth, subjects, teacher_list in students_data:
            student = make_user(
                login, login, 'student', full_name,
                student_class=class_name,
                birth_date=datetime.date.fromisoformat(birth),
                subjects=subjects,
            )
            student.teachers.set(teacher_list)
            student_objs[login] = student
        alia = student_objs['student']
        timur = student_objs['timur']
        sofia = student_objs['sofia']

        # ---- Мероприятия ----
        events = [
            ('Отчётный концерт «Зимняя сказка»', 'Большой зал филармонии',
             '2026-12-20', '18:00', 'Выступление старших классов и оркестра.'),
            ('Концерт ко Дню Независимости', 'Актовый зал школы',
             '2026-12-15', '15:30', 'Хор и ансамбль младших классов.'),
            ('Открытый урок сольфеджио', 'Кабинет №12',
             '2026-11-05', '14:00', 'Для родителей 2–3 классов.'),
        ]
        for title, place, date_str, time_str, description in events:
            EventAnnouncement.objects.get_or_create(
                title=title,
                defaults={
                    'location': place,
                    'date': datetime.date.fromisoformat(date_str),
                    'time': datetime.time.fromisoformat(time_str),
                    'description': description,
                    'created_by': director,
                },
            )

        # ---- Журнал ----
        journal_entries = [
            (kim, alia, 'Специальность', '2026-10-01', 'Б', 5, 'Отличная интонация.'),
            (kim, alia, 'Специальность', '2026-10-08', 'Б', 4, 'Сбивается в среднем разделе.'),
            (orlova, alia, 'Сольфеджио', '2026-10-02', 'Н/Б', None, 'Болеет.'),
            (orlova, alia, 'Сольфеджио', '2026-10-09', 'Б', 5, 'Диктант без ошибок.'),
            (volkov, alia, 'Хор', '2026-10-03', 'Б', 5, ''),
            (kim, timur, 'Специальность', '2026-10-01', 'Б', 3, 'Мало занимался дома.'),
            (kim, timur, 'Специальность', '2026-10-08', 'Б', 4, ''),
            (kim, sofia, 'Специальность', '2026-10-02', 'Б', 5, 'Готовится к конкурсу.'),
            (kim, sofia, 'Оркестр', '2026-10-04', 'Н/Б', None, 'Не предупредил.'),
        ]
        for teacher, student, subject, date_str, attendance, grade, comment in journal_entries:
            GradeJournal.objects.get_or_create(
                teacher=teacher,
                student=student,
                subject=subject,
                date=datetime.date.fromisoformat(date_str),
                defaults={
                    'attendance': attendance,
                    'grade': grade,
                    'comment': comment,
                },
            )

        # ---- Репертуар ----
        repertoire = [
            (kim, alia, 'Концерт ля минор, I ч.', 'А. Вивальди', 'Специальность', 'In progress'),
            (kim, alia, 'Этюд №12', 'К. Черни', 'Специальность', 'Ready'),
            (kim, alia, '«Сурок»', 'Л. Бетховен', 'Специальность', 'Passed'),
            (kim, timur, 'Гавот', 'Госсек', 'Специальность', 'In progress'),
            (kim, sofia, 'Рондо', 'В. Моцарт', 'Специальность', 'Ready'),
        ]
        for teacher, student, title, composer, subject, status in repertoire:
            RepertoireItem.objects.get_or_create(
                teacher=teacher,
                student=student,
                title=title,
                defaults={
                    'composer': composer,
                    'subject': subject,
                    'status': status,
                },
            )

        # ---- Домашние задания ----
        homework = [
            (kim, alia, 'Специальность', 'Вивальди — разобрать II часть',
             'Работа над штрихами, темп 60–70.', '2026-10-15'),
            (orlova, alia, 'Сольфеджио', 'Гамма фа мажор + интервалы',
             'Спеть и сыграть, выучить наизусть.', '2026-10-12'),
            (volkov, alia, 'Хор', 'Разучить партию сопрано',
             'Партия №2, страницы 3–4.', '2026-10-18'),
        ]
        for teacher, student, subject, title, description, due in homework:
            Homework.objects.get_or_create(
                teacher=teacher,
                student=student,
                topic=title,
                defaults={
                    'subject': subject,
                    'description': description,
                    'due_date': datetime.date.fromisoformat(due),
                },
            )

        # ---- Расписание ----
        schedule = [
            (kim, alia, 'Специальность', 'Monday', '15:00', 'Каб. 5', 'индивидуальное'),
            (orlova, alia, 'Сольфеджио', 'Tuesday', '16:30', 'Каб. 12', 'групповое'),
            (volkov, alia, 'Хор', 'Wednesday', '17:00', 'Актовый зал', 'групповое'),
            (kim, alia, 'Специальность', 'Thursday', '15:00', 'Каб. 5', 'индивидуальное'),
            (ahmetova, alia, 'Муз. литература', 'Friday', '14:00', 'Каб. 8', 'групповое'),
        ]
        for teacher, student, subject, day, time_str, room, kind in schedule:
            LessonSchedule.objects.get_or_create(
                teacher=teacher,
                student=student,
                subject=subject,
                day_of_week=day,
                time=datetime.time.fromisoformat(time_str),
                defaults={'room': room, 'lesson_type': kind},
            )

        # ---- Четвертные оценки ----
        if not QuarterGrade.objects.exists():
            QuarterGrade.objects.create(
                teacher=kim,
                student=alia,
                subject='Специальность',
                school_year='2026/2027',
                quarter=1,
                start_date=datetime.date(2026, 9, 1),
                end_date=datetime.date(2026, 11, 30),
                grade=5,
            )

        self.stdout.write(self.style.SUCCESS(
            'Демо-данные готовы. Вход: director/director, teacher/teacher, student/student'
        ))
