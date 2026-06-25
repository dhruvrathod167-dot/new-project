from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="profiles/", 
        blank=True, 
        null=True,
        default='profiles/default-avatar.png'
    )
    bio = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_full_name() or self.username
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username
    
    def get_profile_image_url(self):
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        return '/media/profiles/default-avatar.png'
    
    @property
    def full_name(self):
        return self.get_full_name()
    
    @property
    def is_admin(self):
        return self.is_superuser
    
    def get_role_display(self):
        if self.is_superuser:
            return 'Admin'
        elif self.is_staff:
            return 'Editor'
        return 'Member'


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Project(models.Model):
    CATEGORY_CHOICES = [
        ("residential", "Residential"),
        ("commercial", "Commercial"),
        ("cultural", "Cultural"),
        ("landscape", "Landscape"),
        ("interior", "Interior"),
        ("urban", "Urban"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("on_hold", "On Hold"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.TextField(max_length=500, blank=True)

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="residential")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    location = models.CharField(max_length=255, default="Unknown Location")
    country = models.CharField(max_length=100, default="Unknown Country")
    city = models.CharField(max_length=100, blank=True)

    year_completed = models.IntegerField(null=True, blank=True)

    featured_image = models.ImageField(upload_to="projects/", blank=True, null=True)

    area_sqft = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    architect = models.CharField(max_length=255, blank=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="projects")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="projects/images/")
    caption = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.title} - Image {self.order}"


class GalleryImage(models.Model):
    IMAGE_TYPES = [
        ("project", "Project"),
        ("architecture", "Architecture"),
        ("interior", "Interior"),
        ("landscape", "Landscape"),
        ("detail", "Detail"),
    ]

    image = models.ImageField(upload_to="gallery/")
    title = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES, default="architecture")
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Image {self.id}"


class Service(models.Model):
    SERVICE_TYPES = [
        ("interior", "Interior Design"),
        ("exterior", "Exterior Design"),
        ("planning", "Planning Services"),
        ("architecture", "Architectural Design"),
        ("landscape", "Landscape Architecture"),
        ("urban", "Urban Planning"),
        ("consulting", "Consulting"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default="architecture")
    icon_class = models.CharField(max_length=100, blank=True)
    icon_image = models.ImageField(upload_to="services/icons/", blank=True, null=True)
    features = models.JSONField(default=list, blank=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_custom_pricing = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ContactInquiry(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("read", "Read"),
        ("replied", "Replied"),
        ("resolved", "Resolved"),
    ]

    INQUIRY_TYPES = [
        ("general", "General Inquiry"),
        ("project", "Project Consultation"),
        ("career", "Career Opportunity"),
        ("press", "Press/Media"),
        ("partnership", "Partnership"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES, default="general")
    subject = models.CharField(max_length=255, default="General Inquiry")
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class JournalCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Journal Categories"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class JournalTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Journal(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=300, blank=True)
    content = models.TextField()
    
    featured_image = models.ImageField(upload_to='journal/featured/', blank=True, null=True)
    hero_image = models.ImageField(upload_to='journal/hero/', blank=True, null=True)
    
    categories = models.ManyToManyField(JournalCategory, related_name='articles', blank=True)
    tags = models.ManyToManyField(JournalTag, related_name='articles', blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_articles')
    author_name = models.CharField(max_length=100, blank=True)
    
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=200, blank=True)
    
    views = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)
    reading_time = models.PositiveIntegerField(default=5)

    class Meta:
        ordering = ['-published_date', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_date']),
            models.Index(fields=['featured']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.content:
            word_count = len(self.content.split())
            self.reading_time = max(1, round(word_count / 200))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class JournalImage(models.Model):
    article = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='journal/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.article.title} - Image {self.order + 1}"


class JournalComment(models.Model):
    article = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.name} on {self.article.title}"


class Award(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    organization = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='awards/', blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    link = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'order']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.organization} ({self.year})"


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    ROLE_CHOICES = [
        ('founder', 'Founder'),
        ('co_founder', 'Co-Founder'),
        ('principal', 'Principal Architect'),
        ('senior', 'Senior Architect'),
        ('associate', 'Associate Architect'),
        ('designer', 'Designer'),
        ('lead', 'Project Lead'),
        ('intern', 'Intern'),
        ('other', 'Other'),
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='other')
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='team/profiles/', blank=True, null=True)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    awards = models.TextField(blank=True, help_text='Awards and recognitions (comma or newline separated)')
    experience_years = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    email = models.EmailField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, default='')
    image = models.URLField(max_length=500, blank=True, default='')
    category = models.CharField(max_length=100, blank=True, default='uncategorized')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Founder(models.Model):
    ROLE_CHOICES = (
        ('founder', 'Founder'),
        ('co_founder', 'Co-Founder'),
        ('principal', 'Principal Architect'),
        ('director', 'Director'),
    )
    
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='founder')
    bio = models.TextField()
    profile_photo = models.ImageField(upload_to='founders/', null=True, blank=True)
    photo_alt_text = models.CharField(max_length=255, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order', 'name']


class FounderAward(models.Model):
    founder = models.ForeignKey(Founder, on_delete=models.CASCADE, related_name='awards')
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    is_experience = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.founder.name} - {self.title} ({self.year})"
    
    class Meta:
        ordering = ['order', 'year']