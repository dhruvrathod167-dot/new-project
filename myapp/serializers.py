from rest_framework import serializers
from .models import (
    Project, ProjectImage, GalleryImage, Service, ContactInquiry, User,
    Journal, JournalCategory, JournalTag, JournalImage, JournalComment,
    Award, TeamMember, Tag
)


# ============================================================
# USER SERIALIZER
# ============================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'bio', 'profile_image']


# ============================================================
# PROJECT SERIALIZERS
# ============================================================

class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'caption', 'alt_text', 'is_featured', 'order']


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'slug', 'short_description', 'category', 
                  'location', 'country', 'year_completed', 'featured_image', 'created_at']


class ProjectDetailSerializer(serializers.ModelSerializer):
    images = ProjectImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'title', 'slug', 'description', 'short_description', 
                  'category', 'status', 'location', 'country', 'city',
                  'year_completed', 'featured_image', 'images',
                  'area_sqft', 'architect', 'created_at', 'updated_at']


# ============================================================
# GALLERY SERIALIZER
# ============================================================

class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = ['id', 'image', 'title', 'caption', 'alt_text', 'image_type', 
                  'tags', 'is_featured', 'is_published', 'order', 'created_at']


# ============================================================
# SERVICE SERIALIZERS
# ============================================================

class ServiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'title', 'slug', 'short_description', 'service_type', 
                  'icon_class', 'starting_price', 'order']


class ServiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'title', 'slug', 'description', 'short_description', 
                  'service_type', 'icon_class', 'icon_image', 'features', 
                  'starting_price', 'is_custom_pricing', 'created_at', 'updated_at']


# ============================================================
# CONTACT SERIALIZER
# ============================================================

class ContactInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInquiry
        fields = ['id', 'name', 'email', 'phone', 'inquiry_type', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


# ============================================================
# ========== JOURNAL SERIALIZERS ==============================
# ============================================================

class JournalCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalCategory
        fields = ['id', 'name', 'slug', 'description']


class JournalTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalTag
        fields = ['id', 'name', 'slug']


class JournalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalImage
        fields = ['id', 'image', 'caption', 'alt_text', 'order']


class JournalCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalComment
        fields = ['id', 'name', 'comment', 'created_at']


class JournalSerializer(serializers.ModelSerializer):
    """Full Journal Serializer with all fields"""
    # ✅ FIXED: featured_image and hero_image instead of image
    image = serializers.SerializerMethodField()
    categories = JournalCategorySerializer(many=True, read_only=True)
    tags = JournalTagSerializer(many=True, read_only=True)
    images = JournalImageSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Journal
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content',
            'image', 'featured_image', 'hero_image',
            'categories', 'tags',
            'status', 'published_date', 'created_at', 'updated_at',
            'author', 'author_name', 
            'meta_title', 'meta_description',
            'views', 'featured', 'pinned', 'reading_time',
            'images', 'comments'
        ]

    def get_image(self, obj):
        """Return featured_image URL or hero_image URL"""
        request = self.context.get('request')
        
        # Try featured_image first
        if obj.featured_image and hasattr(obj.featured_image, 'url'):
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        
        # Then try hero_image
        elif obj.hero_image and hasattr(obj.hero_image, 'url'):
            if request:
                return request.build_absolute_uri(obj.hero_image.url)
            return obj.hero_image.url
        
        return None

    def get_comments(self, obj):
        """Return approved comments"""
        comments = obj.comments.filter(is_approved=True)
        return JournalCommentSerializer(comments, many=True).data


class JournalListSerializer(serializers.ModelSerializer):
    """Lightweight Journal Serializer for listing"""
    image = serializers.SerializerMethodField()
    categories = serializers.StringRelatedField(many=True)
    tags = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = Journal
        fields = [
            'id', 'title', 'slug', 'excerpt', 'image',
            'categories', 'tags', 'published_date', 'reading_time',
            'views', 'featured'
        ]

    def get_image(self, obj):
        """Return featured_image URL or hero_image URL"""
        if obj.featured_image and hasattr(obj.featured_image, 'url'):
            return obj.featured_image.url
        elif obj.hero_image and hasattr(obj.hero_image, 'url'):
            return obj.hero_image.url
        return None


# ============================================================
# ========== AWARD SERIALIZER =================================
# ============================================================

class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = ['id', 'title', 'slug', 'organization', 'year', 
                  'description', 'image', 'location', 'link', 'featured', 'order']


# ============================================================
# ========== TEAM MEMBER SERIALIZER ===========================
# ============================================================

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'slug', 'role', 'bio', 'photo', 
                  'email', 'linkedin_url', 'instagram_url', 'order', 'is_active']


# ============================================================
# ========== TAG SERIALIZER ===================================
# ============================================================

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']