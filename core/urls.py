"""URL configuration for core project.

Здесь собраны вместе:
  * админка Django;
  * единый REST API (/api/...), совместимый с контрактом фронтенда;
  * отдача HTML-страниц фронтенда (templates/) и статики (css/js/media).
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    # Единое API музыкальной школы
    path('api/', include('apps.api.urls')),
]

# --------------------------------------------------------------------------
# Страницы фронтенда
# --------------------------------------------------------------------------
FRONTEND_PAGES = {
    'index.html': 'index.html',
    'login.html': 'login.html',
    'director/dashboard.html': 'director/dashboard.html',
    'director/teachers.html': 'director/teachers.html',
    'director/students.html': 'director/students.html',
    'director/events.html': 'director/events.html',
    'teacher/dashboard.html': 'teacher/dashboard.html',
    'teacher/students.html': 'teacher/students.html',
    'teacher/journal.html': 'teacher/journal.html',
    'teacher/quarter-grades.html': 'teacher/quarter-grades.html',
    'teacher/schedule.html': 'teacher/schedule.html',
    'teacher/repertoire.html': 'teacher/repertoire.html',
    'teacher/homework.html': 'teacher/homework.html',
    'student/dashboard.html': 'student/dashboard.html',
    'student/diary.html': 'student/diary.html',
    'student/quarter-grades.html': 'student/quarter-grades.html',
    'student/repertoire.html': 'student/repertoire.html',
    'student/homework.html': 'student/homework.html',
    'student/schedule.html': 'student/schedule.html',
}

# Корень отдаёт страницу входа
urlpatterns.append(
    path('', TemplateView.as_view(template_name='login.html'), name='home')
)

for url_path, template_name in FRONTEND_PAGES.items():
    urlpatterns.append(
        path(
            url_path,
            TemplateView.as_view(template_name=template_name),
            name=url_path.replace('/', '-').replace('.html', ''),
        )
    )

# --------------------------------------------------------------------------
# Статика и медиа.
# Страницы ссылаются на css/... и js/... относительно корня, поэтому
# дополнительно отдаём эти папки по коротким путям (плюс стандартный /static/).
# --------------------------------------------------------------------------
urlpatterns += [
    re_path(r'^css/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'static' / 'css'}),
    re_path(r'^js/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'static' / 'js'}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
