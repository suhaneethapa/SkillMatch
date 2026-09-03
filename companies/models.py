from django.db import models
from django.conf import settings


class CompanyProfile(models.Model):
    """
    Extended profile for Company users.
    Linked 1-to-1 with the User model.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_profile'
    )
    organization_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    industry = models.CharField(max_length=100)
    description = models.TextField()
    website_url = models.URLField(blank=True)
    hq_location = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', blank=True)
    suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.organization_name


class Internship(models.Model):
    """
    A job posting created by a company.
    Includes skill requirements, targeting rules, and position limits.
    """
    LOCATION_CHOICES = [
        ('remote', 'Remote'),
        ('onsite', 'Onsite'),
        ('hybrid', 'Hybrid'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
    ]

    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='internships'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        'core.Category',
        on_delete=models.PROTECT
    )
    location_type = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    stipend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deadline = models.DateField()
    total_positions = models.PositiveIntegerField()
    expected_duration = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining_positions(self):
        """Computed property: how many spots are still open."""
        accepted = self.applications.filter(status='accepted').count()
        return max(0, self.total_positions - accepted)

    def __str__(self):
        return self.title


class InternshipSkill(models.Model):
    """
    Junction table: which skills an internship requires or prefers.
    is_required=True means the skill is required (weight 2.0 in matching).
    is_required=False means preferred (weight 1.0 in matching).
    """
    internship = models.ForeignKey(
        Internship,
        on_delete=models.CASCADE,
        related_name='internship_skills'
    )
    skill = models.ForeignKey(
        'core.Skill',
        on_delete=models.CASCADE
    )
    is_required = models.BooleanField(default=True)

    class Meta:
        unique_together = ('internship', 'skill')


class InternshipCollege(models.Model):
    """
    Junction table: which colleges an internship targets.
    If empty, the internship is open to all colleges.
    """
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    college = models.ForeignKey('core.College', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('internship', 'college')


class InternshipDepartment(models.Model):
    """
    Junction table: which departments an internship targets.
    If empty, the internship is open to all departments.
    """
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)

    class Meta:
        unique_together = ('internship', 'department')