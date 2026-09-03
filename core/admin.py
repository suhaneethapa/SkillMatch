from django.contrib import admin
from .models import College, Category, Skill


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_verified", "created_at")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active", "is_custom")
    list_filter = ("category", "is_active")