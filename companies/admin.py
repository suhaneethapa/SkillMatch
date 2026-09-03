from django.contrib import admin
from .models import CompanyProfile, Internship, InternshipSkill, InternshipCollege, InternshipDepartment


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'contact_person', 'industry', 'suspended')
    list_filter = ('industry', 'suspended')
    search_fields = ('organization_name', 'contact_person')


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'status', 'total_positions', 'deadline')
    list_filter = ('status', 'location_type', 'category')
    search_fields = ('title', 'company__organization_name')


admin.site.register([InternshipSkill, InternshipCollege, InternshipDepartment])