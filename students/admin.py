from django.contrib import admin
from .models import StudentProfile, StudentSkill, Application, JournalEntry


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'college', 'department', 'semester', 'college_verified')
    list_filter = ('college', 'department', 'college_verified')
    search_fields = ('user__email', 'department')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'internship', 'status', 'match_score', 'applied_at')
    list_filter = ('status',)
    search_fields = ('student__email', 'internship__title')


admin.site.register([StudentSkill, JournalEntry])