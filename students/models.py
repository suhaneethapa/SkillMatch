from django.db import models
from django.conf import settings


class StudentProfile(models.Model):
    """
    Extended profile for Student users.
    Linked 1-to-1 with the User model (one User = one StudentProfile).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    college = models.ForeignKey(
        'core.College',
        on_delete=models.PROTECT,
        help_text="College selected from admin-maintained list"
    )
    department = models.CharField(max_length=100)
    semester = models.PositiveSmallIntegerField()
    bio = models.TextField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    cv_file = models.FileField(upload_to='cvs/', blank=True)
    college_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.college.name}"


class StudentSkill(models.Model):
    """
    Junction table: which skills each student has.
    Many-to-many relationship between User and Skill.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_skills'
    )
    skill = models.ForeignKey(
        'core.Skill',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('student', 'skill')
        # Prevents duplicate entries: a student can't have "Python" twice


class Application(models.Model):
    """
    Represents a student applying to an internship.
    Stores the match score at application time (denormalized for performance).
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('offer_issued', 'Offer Issued'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    internship = models.ForeignKey(
        'companies.Internship',  # String reference because Internship hasn't been defined yet
        on_delete=models.CASCADE,
        related_name='applications'
    )
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    match_score = models.DecimalField(max_digits=5, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)
    offer_letter = models.FileField(upload_to='offer_letters/', blank=True)
    rejection_feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'internship')
        # Prevents duplicate applications: one student can only apply once per internship


class JournalEntry(models.Model):
    """
    Weekly progress journal for students in active internships.
    Only visible when Application.status = 'accepted'.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='journal_entries'
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='journal_entries'
    )
    week_number = models.PositiveSmallIntegerField()
    entry_date = models.DateField()
    hours_worked = models.PositiveSmallIntegerField()
    description = models.TextField()

    class Meta:
        unique_together = ('student', 'application', 'week_number')
        # One entry per week per internship