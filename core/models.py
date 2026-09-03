from django.db import models


class College(models.Model):
    """
    Master list of partner colleges.
    Admin pre-populates this; students select from dropdown at registration.
    """
    name = models.CharField(max_length=255, unique=True)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Skill categories: Programming Languages, Frameworks, Design, etc.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    """
    Master list of skills.
    Admin manages this. Students select from it. Companies require it in listings.
    """
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="skills")
    is_active = models.BooleanField(default=True)
    is_custom = models.BooleanField(default=False)
    submitted_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name