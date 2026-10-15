"""Слой совместимости между Django REST-моделями и фронтендом.

Фронтенд (static/js/config.js и static/js/mock.js) описывает контракт API:
пути, имена полей и форматы данных. Этот модуль реализует ровно этот
контракт поверх существующих моделей, чтобы сайт заработал без переделки
фронтенда.
"""

import datetime
import os

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.director.models import EventAnnouncement
from apps.teachers.models import (
    GradeJournal,
    Homework,
    LessonSchedule,
    QuarterGrade,
    RepertoireItem,
)

User = get_user_model()

# --------------------------------------------------------------------------
# Константы-переводчики
# --------------------------------------------------------------------------
ROLE_TO_FRONT = {
    'director': 'DIRECTOR',
    'teacher': 'TEACHER',
    'student': 'STUDENT',
}

SUBJECTS = [
    'Специальность',
    'Сольфеджио',
    'Муз. литература',
    'Хор',
    'Оркестр',
    'Ансамбль',
    'Теория музыки',
]

# Понедельник -> Monday (модель LessonSchedule хранит английские ключи)
DAY_RU_TO_EN = {
    'Понедельник': 'Monday',
    'Вторник': 'Tuesday',
    'Среда': 'Wednesday',
    'Четверг': 'Thursday',
    'Пятница': 'Friday',
    'Суббота': 'Saturday',
    'Воскресенье': 'Sunday',
}
DAY_EN_TO_RU = {v: k for k, v in DAY_RU_TO_EN.items()}

# Статусы репертуара: фронт говорит по-русски, модель хранит английский ключ
STATUS_RU_TO_EN = {
    'В работе': 'In progress',
    'Готово к зачету': 'Ready',
    'Сдано': 'Passed',
}
STATUS_EN_TO_RU = {v: k for k, v in STATUS_RU_TO_EN.items()}


# --------------------------------------------------------------------------
# Помощники
# --------------------------------------------------------------------------
def role_of(user):
    return ROLE_TO_FRONT.get(user.role, str(user.role or '').upper())


def forbidden(message='Недостаточно прав'):
    return Response({'detail': message}, status=status.HTTP_403_FORBIDDEN)


def bad_request(message):
    return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)


def not_found(message='Не найдено'):
    return Response({'detail': message}, status=status.HTTP_404_NOT_FOUND)


def as_date(value, default=None):
    if not value:
        return default
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return default


def as_time(value, default=None):
    if not value:
        return default
    if isinstance(value, datetime.time):
        return value
    try:
        return datetime.time.fromisoformat(str(value)[:5])
    except (ValueError, TypeError):
        return default


def iso_date(value):
    return value.isoformat() if value else None


def hhmm(value):
    return value.strftime('%H:%M') if value else None


def user_public(user):
    data = {
        'id': user.id,
        'username': user.username,
        'role': role_of(user),
        'full_name': user.full_name or user.username,
    }
    if user.role == 'teacher':
        data['subject'] = user.subject or ''
    return data


def teacher_public(teacher):
    return {
        'id': teacher.id,
        'username': teacher.username,
        'login': teacher.username,
        'full_name': teacher.full_name or teacher.username,
        'subject': teacher.subject or '',
        'phone': teacher.phone or '',
        'students_count': teacher.students.count(),
    }


def student_public(student):
    return {
        'id': student.id,
        'username': student.username,
        'login': student.username,
        'full_name': student.full_name or student.username,
        'class_name': student.student_class or '',
        'subjects': student.subjects or [],
        'birth_date': iso_date(student.birth_date),
        'teacher_ids': list(student.teachers.values_list('id', flat=True)),
    }


def event_public(event):
    return {
        'id': event.id,
        'title': event.title,
        'place': event.location,
        'date': iso_date(event.date),
        'time': hhmm(event.time),
        'description': event.description or '',
    }


def journal_public(entry):
    return {
        'id': entry.id,
        'student_id': entry.student_id,
        'subject': entry.subject,
        'date': iso_date(entry.date),
        'attendance': entry.attendance or '',
        'grade': entry.grade,
        'comment': entry.comment or '',
    }


def repertoire_public(item):
    return {
        'id': item.id,
        'student_id': item.student_id,
        'student_name': item.student.full_name or item.student.username,
        'title': item.title,
        'composer': item.composer,
        'subject': item.subject,
        'status': STATUS_EN_TO_RU.get(item.status, item.status),
    }


def homework_public(item):
    file_name = os.path.basename(item.file.name) if item.file else None
    file_url = item.file.url if item.file else None
    return {
        'id': item.id,
        'student_id': item.student_id,
        'student_name': item.student.full_name or item.student.username,
        'subject': item.subject,
        'title': item.topic,
        'description': item.description or '',
        'due_date': iso_date(item.due_date),
        'created_at': iso_date(item.created_at),
        'file_name': file_name,
        'file_url': file_url,
        'teacher': item.teacher.full_name or item.teacher.username,
    }


def schedule_public(lesson):
    return {
        'id': lesson.id,
        'student_id': lesson.student_id,
        'student_name': lesson.student.full_name or lesson.student.username,
        'teacher_id': lesson.teacher_id,
        'teacher': lesson.teacher.full_name or lesson.teacher.username,
        'subject': lesson.subject,
        'day': DAY_EN_TO_RU.get(lesson.day_of_week, lesson.day_of_week),
        'time': hhmm(lesson.time),
        'room': lesson.room or '',
        'kind': lesson.lesson_type or 'индивидуальное',
    }


def quarter_public(item):
    return {
        'id': item.id,
        'student_id': item.student_id,
        'student_name': item.student.full_name or item.student.username,
        'teacher_id': item.teacher_id,
        'subject': item.subject,
        'school_year': item.school_year,
        'quarter': item.quarter,
        'start_date': iso_date(item.start_date),
        'end_date': iso_date(item.end_date),
        'grade': item.grade,
    }


def student_statistics(student):
    records = GradeJournal.objects.filter(student=student)
    grades = [r.grade for r in records if r.grade is not None]
    return {
        'student_id': student.id,
        'full_name': student.full_name or student.username,
        'class_name': student.student_class or '',
        'average': round(sum(grades) / len(grades), 1) if grades else None,
        'grades_count': len(grades),
        'absences': sum(1 for r in records if r.attendance == 'Н/Б'),
        'lessons_count': records.count(),
    }


# --------------------------------------------------------------------------
# Аутентификация
# --------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is None or not user.is_active:
        return Response(
            {'detail': 'Неверный логин или пароль.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': user_public(user),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(user_public(request.user))


class RefreshView(TokenRefreshView):
    """POST /api/auth/refresh/ -> {access} (совместимо с фронтендом)."""


# --------------------------------------------------------------------------
# Директор
# --------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def director_stats(request):
    if request.user.role != 'director':
        return forbidden('Доступ запрещен.')

    records = GradeJournal.objects.all()
    grades = [r.grade for r in records if r.grade is not None]
    total = records.count()
    attended = sum(1 for r in records if r.attendance == 'Б')
    events = EventAnnouncement.objects.order_by('date', 'time')[:3]

    return Response({
        'teachers': User.objects.filter(role='teacher').count(),
        'students': User.objects.filter(role='student').count(),
        'events': EventAnnouncement.objects.count(),
        'average': round(sum(grades) / len(grades), 1) if grades else None,
        'grades_count': len(grades),
        'absences': sum(1 for r in records if r.attendance == 'Н/Б'),
        'lessons_count': total,
        'attendance_rate': round(attended / total * 100) if total else None,
        'upcoming_events': [event_public(e) for e in events],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def director_student_statistics(request):
    if request.user.role != 'director':
        return forbidden('Доступ запрещен.')
    students = User.objects.filter(role='student')
    return Response([student_statistics(s) for s in students])


# --------------------------------------------------------------------------
# Управление преподавателями и учениками (директор)
# --------------------------------------------------------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def teachers(request):
    if request.method == 'GET':
        queryset = User.objects.filter(role='teacher')
        return Response([teacher_public(t) for t in queryset])

    if request.user.role != 'director':
        return forbidden('Преподавателей создаёт только директор.')

    full_name = str(request.data.get('full_name') or '').strip()
    login_name = str(request.data.get('login') or '').strip()
    password = str(request.data.get('password') or '')
    if not full_name or not login_name or not password:
        return bad_request('Укажите ФИО, логин и пароль преподавателя.')
    if User.objects.filter(username=login_name).exists():
        return bad_request('Такой логин уже занят.')

    teacher = User(
        username=login_name,
        role='teacher',
        full_name=full_name,
        subject=str(request.data.get('subject') or ''),
        phone=str(request.data.get('phone') or ''),
    )
    try:
        validate_password(password, teacher)
    except ValidationError as exc:
        return bad_request(' '.join(exc.messages))
    teacher.set_password(password)
    teacher.save()
    return Response(teacher_public(teacher), status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def teacher_detail(request, pk):
    try:
        teacher = User.objects.get(pk=pk, role='teacher')
    except User.DoesNotExist:
        return not_found('Преподаватель не найден.')

    if request.method == 'GET':
        return Response(teacher_public(teacher))

    if request.user.role != 'director':
        return forbidden('Удалять преподавателей может только директор.')
    teacher.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def _apply_teacher_ids(student, teacher_ids):
    teachers_qs = User.objects.filter(id__in=teacher_ids, role='teacher')
    student.teachers.set(teachers_qs)


def _read_teacher_ids(data):
    raw = data.get('teacher_ids', None)
    if raw is None:
        single = data.get('teacher_id', None)
        raw = [single] if single not in (None, '') else []
    if not isinstance(raw, (list, tuple)):
        raw = [raw]
    result = []
    for value in raw:
        try:
            number = int(value)
        except (TypeError, ValueError):
            continue
        if number > 0:
            result.append(number)
    return list(dict.fromkeys(result))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def students(request):
    if request.method == 'GET':
        queryset = User.objects.filter(role='student')
        class_name = request.query_params.get('class')
        if class_name:
            queryset = queryset.filter(student_class=class_name)
        return Response([student_public(s) for s in queryset])

    if request.user.role != 'director':
        return forbidden('Учеников создаёт только директор.')

    full_name = str(request.data.get('full_name') or '').strip()
    login_name = str(request.data.get('login') or '').strip()
    password = str(request.data.get('password') or '')
    subjects = request.data.get('subjects') or []
    if not isinstance(subjects, (list, tuple)):
        subjects = [subjects]
    subjects = [str(s).strip() for s in subjects if str(s).strip()]

    if not full_name or not login_name or not password:
        return bad_request('Укажите ФИО, логин и пароль ученика.')
    if not subjects:
        return bad_request('Выберите хотя бы один предмет.')
    if User.objects.filter(username=login_name).exists():
        return bad_request('Такой логин уже занят.')

    student = User(
        username=login_name,
        role='student',
        full_name=full_name,
        student_class=str(request.data.get('class_name') or ''),
        birth_date=as_date(request.data.get('birth_date')),
        subjects=subjects,
    )
    try:
        validate_password(password, student)
    except ValidationError as exc:
        return bad_request(' '.join(exc.messages))
    student.set_password(password)
    student.save()
    _apply_teacher_ids(student, _read_teacher_ids(request.data))
    return Response(student_public(student), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def student_detail(request, pk):
    try:
        student = User.objects.get(pk=pk, role='student')
    except User.DoesNotExist:
        return not_found('Ученик не найден.')

    user = request.user
    is_director = user.role == 'director'
    is_owner = user.role == 'teacher' and student.teachers.filter(id=user.id).exists()

    if request.method == 'GET':
        if not (is_director or is_owner or user.id == student.id):
            return forbidden()
        return Response(student_public(student))

    if request.method == 'DELETE':
        if not is_director:
            return forbidden('Удалять учеников может только директор.')
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PATCH
    if not (is_director or is_owner):
        return forbidden()

    data = request.data
    if 'full_name' in data:
        full_name = str(data.get('full_name') or '').strip()
        if not full_name:
            return bad_request('Укажите ФИО ученика.')
        student.full_name = full_name
    if 'class_name' in data:
        student.student_class = str(data.get('class_name') or '').strip()
    if 'birth_date' in data:
        student.birth_date = as_date(data.get('birth_date'))
    if 'subjects' in data:
        subjects = data.get('subjects') or []
        if not isinstance(subjects, (list, tuple)):
            subjects = [subjects]
        subjects = [str(s).strip() for s in subjects if str(s).strip()]
        if not subjects:
            return bad_request('Выберите хотя бы один предмет.')
        student.subjects = subjects

    if is_director:
        if 'teacher_ids' in data or 'teacher_id' in data:
            _apply_teacher_ids(student, _read_teacher_ids(data))
        if 'login' in data and str(data.get('login') or '').strip():
            new_login = str(data.get('login')).strip()
            if User.objects.filter(username=new_login).exclude(pk=student.pk).exists():
                return bad_request('Такой логин уже занят.')
            student.username = new_login
        new_password = data.get('password')
        if new_password:
            student.set_password(str(new_password))

    student.save()
    return Response(student_public(student))


# --------------------------------------------------------------------------
# Мероприятия и предметы
# --------------------------------------------------------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def events(request):
    if request.method == 'GET':
        queryset = EventAnnouncement.objects.order_by('date', 'time')
        return Response([event_public(e) for e in queryset])

    if request.user.role != 'director':
        return forbidden('Анонсы создаёт только директор.')
    data = request.data
    event_date = as_date(data.get('date'))
    event_time = as_time(data.get('time'))
    title = str(data.get('title') or '').strip()
    place = str(data.get('place') or data.get('location') or '').strip()
    if not title or not place or not event_date or not event_time:
        return bad_request('Заполните название, место, дату и время.')
    event = EventAnnouncement.objects.create(
        title=title,
        location=place,
        date=event_date,
        time=event_time,
        description=str(data.get('description') or ''),
        created_by=request.user,
    )
    return Response(event_public(event), status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def event_detail(request, pk):
    try:
        event = EventAnnouncement.objects.get(pk=pk)
    except EventAnnouncement.DoesNotExist:
        return not_found('Анонс не найден.')
    if request.method == 'GET':
        return Response(event_public(event))
    if request.user.role != 'director':
        return forbidden('Удалять анонсы может только директор.')
    event.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subjects(request):
    return Response([{'id': i + 1, 'name': name} for i, name in enumerate(SUBJECTS)])


# --------------------------------------------------------------------------
# Преподаватель (свои данные)
# --------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_students(request):
    if request.user.role != 'teacher':
        return forbidden()
    return Response([student_public(s) for s in request.user.students.all()])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_student_statistics(request):
    if request.user.role != 'teacher':
        return forbidden()
    return Response([student_statistics(s) for s in request.user.students.all()])


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def teacher_schedule(request):
    if request.user.role != 'teacher':
        return forbidden()
    if request.method == 'GET':
        order = {name: i for i, name in enumerate(DAY_EN_TO_RU)}
        lessons = list(LessonSchedule.objects.filter(teacher=request.user))
        lessons.sort(key=lambda l: (order.get(l.day_of_week, 99), l.time))
        return Response([schedule_public(l) for l in lessons])

    student_id = request.data.get('student_id')
    student = User.objects.filter(
        id=student_id, role='student', teachers__id=request.user.id
    ).first()
    if not student:
        return bad_request('Выберите своего ученика.')
    day_ru = str(request.data.get('day') or '')
    day_en = DAY_RU_TO_EN.get(day_ru)
    lesson_time = as_time(request.data.get('time'))
    subject_name = str(request.data.get('subject') or '').strip()
    if not day_en or not lesson_time or not subject_name:
        return bad_request('Укажите день, время и предмет.')
    lesson = LessonSchedule.objects.create(
        teacher=request.user,
        student=student,
        subject=subject_name,
        day_of_week=day_en,
        time=lesson_time,
        room=str(request.data.get('room') or '') or '—',
        lesson_type=str(request.data.get('kind') or 'индивидуальное'),
    )
    return Response(schedule_public(lesson), status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def teacher_schedule_detail(request, pk):
    if request.user.role != 'teacher':
        return forbidden()
    lesson = LessonSchedule.objects.filter(pk=pk, teacher=request.user).first()
    if not lesson:
        return not_found('Занятие не найдено.')
    lesson.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def teacher_quarter_grades(request):
    if request.user.role != 'teacher':
        return forbidden()

    if request.method == 'GET':
        queryset = QuarterGrade.objects.filter(teacher=request.user)
        student_id = request.query_params.get('student')
        subject_name = request.query_params.get('subject')
        school_year = request.query_params.get('school_year')
        quarter = request.query_params.get('quarter')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_name:
            queryset = queryset.filter(subject=subject_name)
        if school_year:
            queryset = queryset.filter(school_year=school_year)
        if quarter:
            queryset = queryset.filter(quarter=quarter)
        return Response([quarter_public(q) for q in queryset])

    data = request.data
    student_id = data.get('student_id')
    student = User.objects.filter(
        id=student_id, role='student', teachers__id=request.user.id
    ).first()
    if not student:
        return forbidden('Ученик не найден или не закреплён за вами.')

    subject_name = str(data.get('subject') or '').strip()
    if request.user.subject and subject_name != request.user.subject:
        return forbidden('Оценки ставятся только по вашему предмету.')

    school_year = str(data.get('school_year') or '').strip()
    try:
        quarter_num = int(data.get('quarter'))
    except (TypeError, ValueError):
        quarter_num = 0
    start_date = as_date(data.get('start_date'))
    end_date = as_date(data.get('end_date'))
    try:
        grade_value = int(data.get('grade'))
    except (TypeError, ValueError):
        grade_value = 0

    if not school_year or quarter_num not in (1, 2, 3, 4):
        return bad_request('Укажите учебный год и четверть.')
    if not start_date or not end_date or start_date > end_date:
        return bad_request('Укажите корректные даты четверти.')
    if grade_value < 1 or grade_value > 5:
        return bad_request('Оценка должна быть от 1 до 5.')

    item, _created = QuarterGrade.objects.update_or_create(
        teacher=request.user,
        student=student,
        subject=subject_name,
        school_year=school_year,
        quarter=quarter_num,
        defaults={
            'start_date': start_date,
            'end_date': end_date,
            'grade': grade_value,
        },
    )
    return Response(quarter_public(item), status=status.HTTP_201_CREATED)


# --------------------------------------------------------------------------
# Журнал
# --------------------------------------------------------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def journal(request):
    if request.user.role != 'teacher':
        return forbidden()

    if request.method == 'GET':
        queryset = GradeJournal.objects.filter(teacher=request.user)
        student_id = request.query_params.get('student')
        subject_name = request.query_params.get('subject')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_name:
            queryset = queryset.filter(subject=subject_name)
        queryset = queryset.order_by('-date')
        return Response([journal_public(e) for e in queryset])

    data = request.data
    student_id = data.get('student_id')
    student = User.objects.filter(
        id=student_id, role='student', teachers__id=request.user.id
    ).first()
    if not student:
        return forbidden('Это не ваш ученик.')

    subject_name = str(data.get('subject') or '').strip()
    if request.user.subject and subject_name != request.user.subject:
        return forbidden('Журнал ведётся только по вашему предмету.')

    lesson_date = as_date(data.get('date'))
    if not lesson_date:
        return bad_request('Укажите дату занятия.')

    grade_raw = data.get('grade')
    try:
        grade_value = int(grade_raw) if grade_raw not in (None, '') else None
    except (TypeError, ValueError):
        grade_value = None

    entry, _created = GradeJournal.objects.update_or_create(
        teacher=request.user,
        student=student,
        subject=subject_name,
        date=lesson_date,
        defaults={
            'attendance': str(data.get('attendance') or 'Б'),
            'grade': grade_value,
            'comment': str(data.get('comment') or ''),
        },
    )
    return Response(journal_public(entry), status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def journal_detail(request, pk):
    if request.user.role != 'teacher':
        return forbidden()
    entry = GradeJournal.objects.filter(pk=pk, teacher=request.user).first()
    if not entry:
        return not_found('Запись не найдена.')
    entry.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------
# Репертуар
# --------------------------------------------------------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def repertoire(request):
    if request.method == 'GET':
        if request.user.role == 'teacher':
            queryset = RepertoireItem.objects.filter(teacher=request.user)
        elif request.user.role == 'student':
            queryset = RepertoireItem.objects.filter(student=request.user)
        else:
            queryset = RepertoireItem.objects.all()
        student_id = request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return Response([repertoire_public(r) for r in queryset])

    if request.user.role != 'teacher':
        return forbidden()
    data = request.data
    student_id = data.get('student_id')
    student = User.objects.filter(
        id=student_id, role='student', teachers__id=request.user.id
    ).first()
    if not student:
        return forbidden('Это не ваш ученик.')
    if not str(data.get('title') or '').strip():
        return bad_request('Укажите название произведения.')

    status_ru = str(data.get('status') or 'В работе')
    item = RepertoireItem.objects.create(
        teacher=request.user,
        student=student,
        title=str(data.get('title')).strip(),
        composer=str(data.get('composer') or ''),
        subject=str(data.get('subject') or 'Специальность'),
        status=STATUS_RU_TO_EN.get(status_ru, 'In progress'),
    )
    return Response(repertoire_public(item), status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def repertoire_detail(request, pk):
    if request.user.role != 'teacher':
        return forbidden()
    item = RepertoireItem.objects.filter(pk=pk, teacher=request.user).first()
    if not item:
        return not_found('Произведение не найдено.')

    if request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    data = request.data
    if 'title' in data:
        item.title = str(data.get('title') or '').strip()
    if 'composer' in data:
        item.composer = str(data.get('composer') or '')
    if 'subject' in data:
        item.subject = str(data.get('subject') or '')
    if 'status' in data:
        status_ru = str(data.get('status') or '')
        item.status = STATUS_RU_TO_EN.get(status_ru, item.status)
    item.save()
    return Response(repertoire_public(item))


# --------------------------------------------------------------------------
# Домашние задания
# --------------------------------------------------------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def homework(request):
    if request.method == 'GET':
        if request.user.role == 'teacher':
            queryset = Homework.objects.filter(teacher=request.user)
        elif request.user.role == 'student':
            queryset = Homework.objects.filter(student=request.user)
        else:
            queryset = Homework.objects.all()
        student_id = request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        queryset = queryset.order_by('-created_at')
        return Response([homework_public(h) for h in queryset])

    if request.user.role != 'teacher':
        return forbidden()
    data = request.data
    student_id = data.get('student_id')
    student = User.objects.filter(
        id=student_id, role='student', teachers__id=request.user.id
    ).first()
    if not student:
        return forbidden('Это не ваш ученик.')
    title = str(data.get('title') or '').strip()
    if not title:
        return bad_request('Укажите тему задания.')
    subject_name = str(data.get('subject') or 'Специальность')
    due_date = as_date(data.get('due_date'), default=datetime.date.today())

    item = Homework.objects.create(
        teacher=request.user,
        student=student,
        subject=subject_name,
        topic=title,
        description=str(data.get('description') or ''),
        due_date=due_date,
    )
    upload = request.FILES.get('file')
    if upload:
        item.file = upload
        item.save(update_fields=['file'])
    return Response(homework_public(item), status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def homework_detail(request, pk):
    if request.user.role != 'teacher':
        return forbidden()
    item = Homework.objects.filter(pk=pk, teacher=request.user).first()
    if not item:
        return not_found('Задание не найдено.')
    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------
# Ученик (свои данные)
# --------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    if request.user.role != 'student':
        return forbidden()
    student = request.user
    records = list(GradeJournal.objects.filter(student=student).order_by('-date'))
    grades = [r.grade for r in records if r.grade is not None]
    events = EventAnnouncement.objects.order_by('date', 'time')[:4]

    by_subject = {}
    for record in records:
        bucket = by_subject.setdefault(
            record.subject, {'subject': record.subject, 'grades': [], 'absences': 0}
        )
        if record.grade is not None:
            bucket['grades'].append(record.grade)
        if record.attendance == 'Н/Б':
            bucket['absences'] += 1

    return Response({
        'full_name': student.full_name or student.username,
        'class_name': student.student_class or '',
        'average': round(sum(grades) / len(grades), 1) if grades else None,
        'grades_count': len(grades),
        'absences': sum(1 for r in records if r.attendance == 'Н/Б'),
        'homework_pending': Homework.objects.filter(student=student).count(),
        'recent': [journal_public(r) for r in records[:5]],
        'events': [event_public(e) for e in events],
        'by_subject': list(by_subject.values()),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_grades(request):
    if request.user.role != 'student':
        return forbidden()
    records = GradeJournal.objects.filter(student=request.user).order_by('-date')
    grouped = {}
    for record in records:
        grouped.setdefault(record.subject, []).append(journal_public(record))
    return Response([
        {'subject': subject, 'records': items}
        for subject, items in grouped.items()
    ])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_quarter_grades(request):
    if request.user.role != 'student':
        return forbidden()
    queryset = QuarterGrade.objects.filter(student=request.user)
    return Response([quarter_public(q) for q in queryset])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_repertoire(request):
    if request.user.role != 'student':
        return forbidden()
    queryset = RepertoireItem.objects.filter(student=request.user)
    return Response([repertoire_public(r) for r in queryset])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_homework(request):
    if request.user.role != 'student':
        return forbidden()
    queryset = Homework.objects.filter(student=request.user).order_by('-created_at')
    return Response([homework_public(h) for h in queryset])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_schedule(request):
    if request.user.role != 'student':
        return forbidden()
    order = {name: i for i, name in enumerate(DAY_EN_TO_RU)}
    lessons = list(LessonSchedule.objects.filter(student=request.user))
    lessons.sort(key=lambda l: (order.get(l.day_of_week, 99), l.time))
    return Response([schedule_public(l) for l in lessons])
