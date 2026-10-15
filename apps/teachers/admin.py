from django.contrib import admin
from .models import (
    GradeJournal,
    Homework,
    LessonSchedule,
    RepertoireItem,
    TermGrade,
)

admin.site.register(LessonSchedule)
admin.site.register(GradeJournal)
admin.site.register(TermGrade)
admin.site.register(RepertoireItem)
admin.site.register(Homework)