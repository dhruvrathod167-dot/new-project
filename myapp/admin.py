from django.contrib import admin
from .models import (
    User, Project, ProjectImage, GalleryImage,
    Service, ContactInquiry, Award, Tag, 
    Journal, JournalCategory, JournalTag, JournalImage, JournalComment,
    TeamMember, Newsletter, Product
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_verified']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'is_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    fieldsets = (
        ('Personal Info', {
            'fields': ('username', 'first_name', 'last_name', 'email', 'phone', 'bio', 'profile_image')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'status', 'location', 'year_completed', 'created_at']
    list_filter = ['category', 'status', 'country']
    search_fields = ['title', 'description', 'location']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']
    filter_horizontal = ['tags']


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'caption', 'is_featured', 'order', 'created_at']
    list_filter = ['is_featured', 'project']
    search_fields = ['caption', 'alt_text']
    ordering = ['project', 'order']


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'image_type', 'is_featured', 'is_published', 'order', 'created_at']
    list_filter = ['image_type', 'is_featured', 'is_published']
    search_fields = ['title', 'caption', 'alt_text', 'tags']
    ordering = ['order', '-created_at']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'service_type', 'is_published', 'order', 'created_at']
    list_filter = ['service_type', 'is_published']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', 'title']


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'inquiry_type', 'status', 'subject', 'created_at']
    list_filter = ['status', 'inquiry_type']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'user_agent']
    ordering = ['-created_at']


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'organization', 'year', 'featured', 'order']
    list_filter = ['year', 'featured']
    search_fields = ['title', 'organization', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-year', 'order']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


# ============================================================
# ========== JOURNAL ADMIN (FULL FEATURED) ===================
# ============================================================

@admin.register(JournalCategory)
class JournalCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'order', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(JournalTag)
class JournalTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


class JournalImageInline(admin.TabularInline):
    model = JournalImage
    extra = 1
    fields = ['image', 'caption', 'alt_text', 'order']
    ordering = ['order']


class JournalCommentInline(admin.TabularInline):
    model = JournalComment
    extra = 0
    fields = ['name', 'email', 'comment', 'is_approved', 'created_at']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'published_date', 'views', 'featured', 'reading_time', 'created_at']
    list_filter = ['status', 'categories', 'tags', 'featured', 'pinned']
    search_fields = ['title', 'excerpt', 'content', 'author_name']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-published_date', '-created_at']
    readonly_fields = ['views', 'created_at', 'updated_at']
    filter_horizontal = ['categories', 'tags']
    inlines = [JournalImageInline, JournalCommentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Media', {
            'fields': ('featured_image', 'hero_image'),
            'classes': ('wide',)
        }),
        ('Categories & Tags', {
            'fields': ('categories', 'tags')
        }),
        ('Author', {
            'fields': ('author', 'author_name')
        }),
        ('Status & Dates', {
            'fields': ('status', 'published_date')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Engagement', {
            'fields': ('views', 'featured', 'pinned', 'reading_time')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JournalComment)
class JournalCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'article', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'article']
    search_fields = ['name', 'email', 'comment']
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"


@admin.register(JournalImage)
class JournalImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'article', 'caption', 'order', 'created_at']
    list_filter = ['article']
    search_fields = ['caption', 'alt_text']
    ordering = ['article', 'order']


# ============================================================
# ========== TEAM MEMBER ADMIN ===============================
# ============================================================

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'role', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'role']
    search_fields = ['name', 'role', 'bio']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'role', 'bio')
        }),
        ('Photos', {                          # ← AA MISSING HATU
            'fields': ('profile_photo', 'photo'),
        }),
        ('Contact & Social', {
            'fields': ('email', 'linkedin_url', 'instagram_url')
        }),
        ('Details', {
            'fields': ('experience_years', 'awards', 'order', 'is_active')
        }),
    )


# ============================================================
# ========== NEWSLETTER ADMIN ================================
# ============================================================

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['email']
    ordering = ['-created_at']


# ============================================================
# ========== PRODUCT ADMIN ===================================
# ============================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'price', 'created_at']
    list_filter = ['category']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    
    
from .models import Founder, FounderAward

class FounderAwardInline(admin.TabularInline):
    model = FounderAward
    extra = 1
    fields = ['title', 'year', 'is_experience', 'order']

@admin.register(Founder)
class FounderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'role', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']
    inlines = [FounderAwardInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'role', 'bio')
        }),
        ('Photo', {
            'fields': ('profile_photo', 'photo_alt_text'),
        }),
        ('Social', {
            'fields': ('linkedin_url', 'instagram_url')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )


# ============================================================
# ========== SITE CONFIGURATION ==============================
# ============================================================

admin.site.site_header = "ARCHAUS Admin Panel"
admin.site.site_title = "ARCHAUS"
admin.site.index_title = "Welcome to ARCHAUS Architecture Studio Admin"