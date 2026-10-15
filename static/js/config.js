/* =========================================================================
 * config.js — Глобальная конфигурация фронтенда
 * =======================================================================*/
window.App = window.App || {};

App.CONFIG = {
  /* -----------------------------------------------------------------
   * Адрес Django REST API.
   *  - '' (пусто)         — тот же origin, что и фронтенд (рекомендуется:
   *                         отдавайте фронт через Django/nginx рядом с /api/).
   *  - 'http://localhost:8000' — если бэкенд запущен отдельно (runserver).
   * ----------------------------------------------------------------- */
  API_BASE: '',

  /* -----------------------------------------------------------------
   * DEMO_MODE:
   *  - true  — все запросы обслуживаются встроенными мок-данными.
   *            Фронт полностью работает без бэкенда (для демонстрации).
   *  - false — реальные запросы к API_BASE (Django REST + JWT).
   * ----------------------------------------------------------------- */
  DEMO_MODE: false,

  /* Ключи localStorage */
  STORAGE: {
    ACCESS: 'ek_access',
    REFRESH: 'ek_refresh',
    USER: 'ek_user',
  },

  /* Пути эндпоинтов Django REST (можно менять под свой urls.py).
   * Часть путей относительная — api.buildUrl() сам добавит /api/ если нужно.
   */
  ENDPOINTS: {
    // --- Auth (djangorestframework-simplejwt) ---
    login: '/api/auth/login/',          // POST {username, password} -> {access, refresh, user}
    refresh: '/api/auth/refresh/',      // POST {refresh} -> {access}
    me: '/api/auth/me/',                // GET  current user {id, username, role, full_name, subject?} (subject — предмет учителя)

    // --- Director (создаёт учётные записи учителей и учеников) ---
    stats: '/api/director/stats/',      // GET {teachers, students, events}
    directorStudentStats: '/api/director/student-statistics/', // GET school-wide per-student performance
    teachers: '/api/teachers/',         // GET / POST (создание только директором: full_name, subject, phone, login, password)
    teacher: (id) => `/api/teachers/${id}/`, // DELETE (только директор)
    students: '/api/students/',         // GET (?class=) / POST (только директор: + teacher_ids[] — ученика можно закрепить за несколькими преподавателями)
    student: (id) => `/api/students/${id}/`, // GET / PATCH (директор: + teacher_ids[]) / DELETE (только директор)
    events: '/api/events/',             // GET / POST
    event: (id) => `/api/events/${id}/`,

    // --- Teacher ---
    myStudents: '/api/teacher/students/',   // GET (ученики, закреплённые директором)
    teacherStudentStats: '/api/teacher/student-statistics/', // GET per-student performance for assigned students
    teacherSchedule: '/api/teacher/schedule/', // GET / POST lessons assigned to students
    teacherScheduleItem: (id) => `/api/teacher/schedule/${id}/`, // DELETE
    subjects: '/api/subjects/',             // GET список предметов
    journal: '/api/journal/',               // GET (?subject=&student=) / POST (учитель — только свои ученики и свой предмет)
    journalItem: (id) => `/api/journal/${id}/`,
    quarterGrades: '/api/teacher/quarter-grades/', // GET / POST (учитель — только свои ученики и свой предмет)
    repertoire: '/api/repertoire/',         // GET (?student=) / POST / PATCH
    repertoireItem: (id) => `/api/repertoire/${id}/`,
    homework: '/api/homework/',             // GET / POST (multipart, файл)
    homeworkItem: (id) => `/api/homework/${id}/`,

    // --- Student ---
    studentQuarterGrades: '/api/student/quarter-grades/', // GET saved grades for current student
  },

  SUBJECTS: [
    'Специальность',
    'Сольфеджио',
    'Муз. литература',
    'Хор',
    'Оркестр',
    'Ансамбль',
    'Теория музыки',
  ],
};
