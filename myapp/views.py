from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods, require_POST
from django.utils import timezone
from functools import wraps
import json
import re
import logging
from django.db import models

from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view

from .models import (
    User, Project, ProjectImage, GalleryImage, Service, 
    ContactInquiry, TeamMember, Award, Tag, Product,
    Journal, JournalCategory, JournalTag, JournalComment,
    Newsletter
)
from .serializers import (
    ProjectListSerializer, ProjectDetailSerializer,
    GalleryImageSerializer, ServiceListSerializer, 
    ServiceDetailSerializer, ContactInquirySerializer,
    JournalSerializer, JournalListSerializer
)

# Setup logger
logger = logging.getLogger(__name__)


# ============================================================
# GET CLIENT IP
# ============================================================

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


# ============================================================
# VALIDATION HELPERS (SECURITY FIXES)
# ============================================================

def validate_email_strict(email):
    """
    Strict email validation with multiple checks
    """
    if not email or not email.strip():
        return False, "Email is required"
    
    email = email.strip().lower()
    
    # Basic format check
    if '@' not in email:
        return False, "Invalid email format - missing @ symbol"
    
    # Split and validate parts
    parts = email.split('@')
    if len(parts) != 2:
        return False, "Invalid email format"
    
    local, domain = parts
    
    if not local or not domain:
        return False, "Invalid email format - missing local or domain part"
    
    if '.' not in domain:
        return False, "Invalid email format - domain must contain a dot"
    
    # Check for common disposable email domains (optional)
    disposable_domains = [
        'tempmail.com', 'throwaway.com', 'guerrillamail.com',
        'mailinator.com', '10minutemail.com', 'temp-mail.org'
    ]
    if domain.lower() in disposable_domains:
        return False, "Please use a permanent email address"
    
    return True, email


def validate_password_strength(password):
    """
    Comprehensive password strength validation
    """
    errors = []
    
    if not password:
        errors.append("Password is required")
        return errors
    
    if len(password) < 12:
        errors.append("Password must be at least 12 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    # Check for common passwords
    common_passwords = ['password123', 'admin123', '12345678', 'qwerty123']
    if password.lower() in common_passwords:
        errors.append("Password is too common - choose a more unique password")
    
    return errors


def validate_message_length(message, max_length=5000):
    """
    Validate message length
    """
    if not message:
        return False, "Message cannot be empty"
    
    if len(message) > max_length:
        return False, f"Message too long. Maximum {max_length} characters allowed (current: {len(message)})"
    
    return True, None


def validate_image_file(uploaded_file, max_size_mb=5):
    """
    Validate uploaded profile image: type and size
    """
    if uploaded_file.size > max_size_mb * 1024 * 1024:
        return False, f"Image size must be under {max_size_mb}MB."

    valid_content_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    if uploaded_file.content_type not in valid_content_types:
        return False, "Please upload a valid image file (JPEG, PNG, WEBP, or GIF)."

    return True, None


# ============================================================
# AUTH DECORATORS
# ============================================================

def admin_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/auth/login/')
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "Admin access required.")
            return redirect('/auth/dashboard/')
        return view_func(request, *args, **kwargs)
    return wrapper


def editor_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/auth/login/')
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Editor access required.")
            return redirect('/auth/login/')
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================
# PUBLIC PAGES
# ============================================================

def home(request):
    """Home page"""
    try:
        featured_projects = Project.objects.filter(status='completed').order_by('-year_completed')[:6]
        featured_awards = Award.objects.filter(featured=True)[:3]
        featured_articles = Journal.objects.filter(status='published', featured=True)[:3]
        services = Service.objects.filter(is_published=True)[:6]
        
        context = {
            'featured_projects': featured_projects,
            'featured_awards': featured_awards,
            'featured_articles': featured_articles,
            'services': services,
        }
        return render(request, 'index.html', context)
    except Exception as e:
        logger.error(f"Home page error: {str(e)}")
        return render(request, 'index.html', {'error': 'Unable to load content'})


def philosophy(request):
    try:
        return render(request, 'philosophy.html')
    except Exception as e:
        logger.error(f"Philosophy page error: {str(e)}")
        return render(request, 'philosophy.html', {'error': 'Unable to load page'})


def services_page(request):
    """Display all services"""
    try:
        services = Service.objects.filter(is_published=True).order_by('order')
        return render(request, 'services.html', {'services': services})
    except Exception as e:
        logger.error(f"Services page error: {str(e)}")
        return render(request, 'services.html', {'services': [], 'error': 'Unable to load services'})


def service_detail(request, slug):
    try:
        service = get_object_or_404(Service, slug=slug, is_published=True)
        return render(request, 'service_detail.html', {'service': service})
    except Http404:
        return render(request, '404.html', {'error': 'Service not found'}, status=404)
    except Exception as e:
        logger.error(f"Service detail error: {str(e)}")
        return render(request, 'service_detail.html', {'error': 'Unable to load service'})


def awards_page(request):
    """Awards listing page"""
    try:
        awards = Award.objects.all().order_by('-year')
        featured_awards = awards.filter(featured=True)
        
        context = {
            'awards': awards,
            'featured_awards': featured_awards,
        }
        return render(request, 'awards.html', context)
    except Exception as e:
        logger.error(f"Awards page error: {str(e)}")
        return render(request, 'awards.html', {'awards': [], 'error': 'Unable to load awards'})


def journal_page(request):
    """Journal listing page"""
    try:
        articles = Journal.objects.filter(status='published').order_by('-published_date')
        featured = articles.filter(featured=True)[:3]
        categories = JournalCategory.objects.all()
        
        # Search
        q = request.GET.get('q')
        if q:
            articles = articles.filter(
                models.Q(title__icontains=q) | 
                models.Q(excerpt__icontains=q) | 
                models.Q(content__icontains=q)
            )
        
        # Category filter
        category_slug = request.GET.get('category')
        if category_slug:
            category = get_object_or_404(JournalCategory, slug=category_slug)
            articles = articles.filter(categories=category)
        
        context = {
            'articles': articles,
            'featured': featured,
            'categories': categories,
        }
        return render(request, 'journal.html', context)
    except Exception as e:
        logger.error(f"Journal page error: {str(e)}")
        return render(request, 'journal.html', {'articles': [], 'error': 'Unable to load articles'})


def journal_detail(request, slug):
    """Single journal article detail"""
    try:
        article = get_object_or_404(Journal, slug=slug, status='published')
        
        # Increment views
        article.views += 1
        article.save(update_fields=['views'])
        
        # Related articles
        related = Journal.objects.filter(
            models.Q(categories__in=article.categories.all()) |
            models.Q(tags__in=article.tags.all())
        ).exclude(id=article.id).distinct()[:3]
        
        context = {
            'article': article,
            'related': related,
        }
        return render(request, 'journal_detail.html', context)
    except Http404:
        return render(request, '404.html', {'error': 'Article not found'}, status=404)
    except Exception as e:
        logger.error(f"Journal detail error: {str(e)}")
        return render(request, 'journal_detail.html', {'error': 'Unable to load article'})


def gallery(request):
    try:
        images = GalleryImage.objects.filter(is_published=True).order_by('order')
        return render(request, 'gallery.html', {'images': images})
    except Exception as e:
        logger.error(f"Gallery error: {str(e)}")
        return render(request, 'gallery.html', {'images': [], 'error': 'Unable to load gallery'})


def studio(request):
    try:
        from .models import Founder
        
        founders = Founder.objects.filter(is_active=True).order_by('order')
        architects = TeamMember.objects.filter(
            is_active=True
        ).exclude(
            role__in=['founder', 'co_founder']
        ).order_by('order')
        team_members = TeamMember.objects.filter(is_active=True).order_by('order')
        
        return render(request, 'studio.html', {
            'team_members': team_members,
            'founders': founders,
            'architects': architects,
        })
    except Exception as e:
        logger.error(f"Studio error: {str(e)}")
        return render(request, 'studio.html', {'error': 'Unable to load team'})


def contact_page(request):
    """Contact page"""
    try:
        return render(request, 'contact.html')
    except Exception as e:
        logger.error(f"Contact page error: {str(e)}")
        return render(request, 'contact.html', {'error': 'Unable to load page'})


# ============================================================
# PROJECTS - ✅ SECURE VERSION
# ============================================================

def projects_list(request):
    """List all completed projects - SECURE"""
    try:
        # ✅ Only show completed projects
        projects = Project.objects.filter(status='completed').order_by('-year_completed')
        
        # ✅ Only show tags from completed projects
        tags = Tag.objects.filter(projects__status='completed').distinct()   # ← 's' add kari (projects, nahi project)
        
        # ✅ Only completed projects for dropdown
        all_projects = Project.objects.filter(status='completed').order_by('title')
        
        return render(request, 'projects.html', {
            'projects': projects,
            'tags': tags,
            'all_projects': all_projects,
        })
    except Exception as e:
        logger.error(f"Projects list error: {str(e)}")
        return render(request, 'projects.html', {
            'projects': [], 
            'error': 'Unable to load projects'
        }, status=500)


def project_detail(request, slug):
    try:
        # Use 'status' instead of 'is_active'
        project = Project.objects.get(slug=slug, status='published')  # or 'active'
        
        # Or if you want to show all projects regardless of status:
        # project = Project.objects.get(slug=slug)
        
        # Get related projects
        related = Project.objects.filter(
            category=project.category,
            status='published'  # Use correct field
        ).exclude(id=project.id)[:3]
        
        all_projects = Project.objects.filter(status='published')  # Use correct field
        
        context = {
            'project': project,
            'related': related,
            'all_projects': all_projects,
        }
        
        return render(request, 'myapp/project_detail.html', context)
        
    except Project.DoesNotExist:
        raise Http404("Project not found")

# ============================================================
# 🔒 AUTH VIEWS (WITH SECURITY FIXES)
# ============================================================

@csrf_protect
def register_view(request):
    if request.user.is_authenticated:
        return redirect('/auth/dashboard/')
    
    if request.method == 'POST':
        try:
            full_name = request.POST.get('full_name', '').strip()
            email = request.POST.get('email', '').strip().lower()
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            if not full_name:
                messages.error(request, 'Full name is required.')
                return render(request, 'auth/register.html')
            
            if not email or '@' not in email:
                messages.error(request, 'Valid email address is required.')
                return render(request, 'auth/register.html')
            
            from .models import User
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered. Please login.')
                return redirect('/auth/login/')
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'auth/register.html')
            
            password_errors = []
            if len(password) < 12:
                password_errors.append("Password must be at least 12 characters long")
            if not re.search(r'[A-Z]', password):
                password_errors.append("Password must contain at least one uppercase letter")
            if not re.search(r'[a-z]', password):
                password_errors.append("Password must contain at least one lowercase letter")
            if not re.search(r'\d', password):
                password_errors.append("Password must contain at least one number")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                password_errors.append("Password must contain at least one special character")
            
            if password_errors:
                for error in password_errors:
                    messages.error(request, error)
                return render(request, 'auth/register.html')
            
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=full_name.split()[0] if ' ' in full_name else full_name,
                last_name=full_name.split()[-1] if ' ' in full_name else ''
            )
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome to ARCHAUS, {full_name}!')
                return redirect('/auth/dashboard/')
            else:
                messages.success(request, 'Registration successful! Please login.')
                return redirect('/auth/login/')
                
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            messages.error(request, 'Registration failed. Please try again.')
            return render(request, 'auth/register.html')
    
    return render(request, 'auth/register.html')


@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/auth/dashboard/')
    
    if request.method == 'POST':
        try:
            email = request.POST.get('email', '').strip().lower()
            password = request.POST.get('password', '')
            
            if not email or not password:
                messages.error(request, 'Email and password are required.')
                return render(request, 'auth/login.html')
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('/auth/dashboard/')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            messages.error(request, 'Login failed. Please try again.')
    
    return render(request, 'auth/login.html')


# ============================================================
# 🔒 LOGOUT VIEW (POST only - CSRF protected)
# ============================================================

@require_POST
@csrf_protect
def logout_view(request):
    """Logout user - requires POST method to prevent CSRF attacks"""
    try:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        messages.error(request, 'Logout failed. Please try again.')
    return redirect('/auth/login/')


# ============================================================
# DASHBOARD VIEW
# ============================================================

@login_required(login_url='/auth/login/')
def dashboard_view(request):
    try:
        recent_projects = Project.objects.filter(status='completed').order_by('-updated_at')[:5]
        context = {
            "user": request.user,
            "all_users": User.objects.all() if request.user.is_superuser else None,
            "recent_projects": recent_projects,
            "stats": {
                "active_projects": Project.objects.filter(status='completed').count(),
                "total_users": User.objects.filter(is_active=True).count(),
            }
        }
        return render(request, 'auth/dashboard.html', context)
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return render(request, 'auth/dashboard.html', {'error': 'Unable to load dashboard'})


# ============================================================
# USER MANAGEMENT (ADMIN ONLY)
# ============================================================

@admin_required
def user_list_view(request):
    try:
        users = User.objects.all().order_by("-is_superuser", "username")
        return render(request, 'auth/user_list.html', {"users": users})
    except Exception as e:
        logger.error(f"User list error: {str(e)}")
        messages.error(request, 'Unable to load users')
        return redirect('/auth/dashboard/')


@admin_required
def user_create_view(request):
    if request.method == "POST":
        try:
            email = request.POST.get("email", "").strip().lower()
            full_name = request.POST.get("full_name", "").strip()
            is_admin = request.POST.get("is_admin") == "on"
            password = request.POST.get("password", "")
            
            is_valid, email_result = validate_email_strict(email)
            if not is_valid:
                messages.error(request, email_result)
                return render(request, 'auth/user_form.html')
            email = email_result
            
            if is_admin:
                password_errors = validate_password_strength(password)
                if password_errors:
                    for error in password_errors:
                        messages.error(request, error)
                    return render(request, 'auth/user_form.html')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, "User with this email already exists.")
            else:
                User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=full_name.split()[0] if ' ' in full_name else full_name,
                    last_name=full_name.split()[-1] if ' ' in full_name else '',
                    is_staff=is_admin,
                    is_superuser=is_admin,
                )
                messages.success(request, f"User {full_name} created.")
                return redirect('/auth/users/')
        except Exception as e:
            logger.error(f"User create error: {str(e)}")
            messages.error(request, 'Failed to create user. Please try again.')
    
    return render(request, 'auth/user_form.html')


@admin_required
@require_POST
def user_toggle_active(request, pk):
    try:
        user = User.objects.get(pk=pk)
        if user == request.user:
            return JsonResponse({
                'success': False,
                'message': 'Cannot deactivate yourself.'
            }, status=400)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({
            'success': True,
            'active': user.is_active, 
            'name': user.get_full_name() or user.username
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found.'
        }, status=404)
    except Exception as e:
        logger.error(f"User toggle active error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to update user status.'
        }, status=500)


# ============================================================
# PROFILE VIEW
# ============================================================

@login_required(login_url='/auth/login/')
def profile_view(request):
    if request.method == "POST":
        try:
            user = request.user

            # ---- FULL NAME ----
            full_name = request.POST.get("full_name", "").strip()
            if full_name:
                parts = full_name.split()
                user.first_name = parts[0]
                user.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

            # ---- PHONE ----
            phone = request.POST.get("phone", "").strip()
            user.phone = phone

            # ---- BIO ----
            bio = request.POST.get("bio", "").strip()
            user.bio = bio

            # ---- PROFILE IMAGE ----
            if 'profile_image' in request.FILES:
                uploaded_file = request.FILES['profile_image']
                is_valid_image, image_error = validate_image_file(uploaded_file)
                if not is_valid_image:
                    messages.error(request, image_error)
                    return render(request, 'auth/profile.html')
                user.profile_image = uploaded_file

            # ---- PASSWORD CHANGE ----
            new_password = request.POST.get("new_password", "")
            if new_password:
                current = request.POST.get("current_password", "")
                if not user.check_password(current):
                    messages.error(request, "Current password is incorrect.")
                    return render(request, 'auth/profile.html')
                
                password_errors = validate_password_strength(new_password)
                if password_errors:
                    for error in password_errors:
                        messages.error(request, error)
                    return render(request, 'auth/profile.html')
                
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password updated. Please log in again.")
                logout(request)
                return redirect('/auth/login/')
            
            user.save()
            messages.success(request, "Profile updated.")
            return redirect('/auth/profile/')
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            messages.error(request, 'Failed to update profile. Please try again.')
    
    return render(request, 'auth/profile.html')


# ============================================================
# API LOGIN (AJAX) - ✅ FIXED
# ============================================================

@require_http_methods(["POST"])
def api_login(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        is_valid, _ = validate_email_strict(email)
        if not is_valid:
            return JsonResponse({
                'success': False,
                'message': 'Invalid email format'
            }, status=401)
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'redirect_url': '/auth/dashboard/',
                'message': 'Login successful'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid email or password.'
            }, status=401)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"API login error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred during login. Please try again.'
        }, status=500)


# ============================================================
# PRODUCTS API - ✅ FIXED
# ============================================================

def products_page(request):
    try:
        return render(request, 'products.html')
    except Exception as e:
        logger.error(f"Products page error: {str(e)}")
        return render(request, 'products.html', {'error': 'Unable to load page'})


def get_products(request):
    if request.method == 'GET':
        try:
            products = Product.objects.all().order_by('-id')
            data = [
                {
                    'id': p.id,
                    'title': p.title,
                    'price': float(p.price),
                    'description': p.description,
                    'image': p.image,
                    'category': p.category
                }
                for p in products
            ]
            return JsonResponse({
                'success': True,
                'data': data
            })
        except Exception as e:
            logger.error(f"Get products error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Unable to fetch products. Please try again.'
            }, status=500)
    return JsonResponse({
        'success': False,
        'message': 'Method not allowed'
    }, status=405)


@staff_member_required
def add_product(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        
        title = data.get('title', '').strip()
        price = data.get('price', 0)
        description = data.get('description', '').strip()
        image = data.get('image', 'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=480&q=70')
        category = data.get('category', 'uncategorized').strip()
        
        if not title:
            return JsonResponse({
                'success': False,
                'message': 'Title is required'
            }, status=400)
        if not price or float(price) <= 0:
            return JsonResponse({
                'success': False,
                'message': 'Valid price is required'
            }, status=400)
        
        product = Product.objects.create(
            title=title,
            price=float(price),
            description=description,
            image=image,
            category=category
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Product added successfully!',
            'data': {
                'id': product.id,
                'title': product.title,
                'price': float(product.price),
                'description': product.description,
                'image': product.image,
                'category': product.category
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Add product error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Unable to add product. Please try again.'
        }, status=500)


@staff_member_required
def product_detail_api(request, product_id):
    if request.method == 'GET':
        try:
            product = Product.objects.get(id=product_id)
            data = {
                'id': product.id,
                'title': product.title,
                'price': float(product.price),
                'description': product.description,
                'image': product.image,
                'category': product.category
            }
            return JsonResponse({'success': True, 'data': data})
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Get product detail error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Unable to fetch product details'
            }, status=500)
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            product = Product.objects.get(id=product_id)
            
            product.title = data.get('title', product.title)
            product.price = float(data.get('price', product.price))
            product.description = data.get('description', product.description)
            product.image = data.get('image', product.image)
            product.category = data.get('category', product.category)
            product.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Product updated successfully!',
                'data': {
                    'id': product.id,
                    'title': product.title,
                    'price': float(product.price),
                    'description': product.description,
                    'image': product.image,
                    'category': product.category
                }
            })
            
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Update product error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Unable to update product'
            }, status=500)
    
    elif request.method == 'DELETE':
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return JsonResponse({
                'success': True,
                'message': 'Product deleted successfully!'
            })
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Delete product error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Unable to delete product'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Method not allowed. Use GET, PUT, or DELETE'
    }, status=405)


# ============================================================
# CONTACT INQUIRY - ✅ FIXED
# ============================================================

def contact_submit(request):
    if request.method == 'GET':
        return JsonResponse({
            'status': 'active',
            'message': 'Contact API is ready!',
            'endpoint': '/api/contact/',
            'method': 'POST (for form submission)',
            'fields': {
                'required': ['name', 'email', 'message'],
                'optional': ['phone', 'location', 'project_type', 'budget']
            }
        }, status=200)
    
    if request.method == 'POST':
        try:
            if request.content_type and 'application/json' in request.content_type:
                data = json.loads(request.body)
                name = data.get('name', '').strip()
                email = data.get('email', '').strip()
                phone = data.get('phone', '').strip()
                location = data.get('location', '').strip()
                project_type = data.get('project_type', '').strip()
                budget = data.get('budget', '').strip()
                message = data.get('message', '').strip()
            else:
                name = request.POST.get('name', '').strip()
                email = request.POST.get('email', '').strip()
                phone = request.POST.get('phone', '').strip()
                location = request.POST.get('location', '').strip()
                project_type = request.POST.get('project_type', '').strip()
                budget = request.POST.get('budget', '').strip()
                message = request.POST.get('message', '').strip()
            
            if not name:
                return JsonResponse({
                    'success': False,
                    'message': 'Name is required.'
                }, status=400)
            
            is_valid, email_result = validate_email_strict(email)
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'message': email_result
                }, status=400)
            email = email_result
            
            is_valid_message, msg_error = validate_message_length(message, max_length=5000)
            if not is_valid_message:
                return JsonResponse({
                    'success': False,
                    'message': msg_error
                }, status=400)
            
            inquiry = ContactInquiry.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=f"Project: {project_type} - Budget: {budget}",
                message=f"Location: {location}\n\n{message}",
                inquiry_type='project',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Your enquiry has been sent successfully!',
                'inquiry_id': inquiry.id
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data.'
            }, status=400)
        except Exception as e:
            logger.error(f"Contact submit error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Unable to send your enquiry. Please try again.'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Method not allowed.'
    }, status=405)


# ============================================================
# NEWSLETTER - ✅ FIXED
# ============================================================

def newsletter_subscribe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            
            is_valid, email_result = validate_email_strict(email)
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'message': email_result
                }, status=400)
            email = email_result
            
            newsletter, created = Newsletter.objects.get_or_create(email=email)
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for subscribing!'
                }, status=201)
            else:
                if newsletter.is_active:
                    return JsonResponse({
                        'success': False,
                        'message': 'This email is already subscribed.'
                    }, status=400)
                else:
                    newsletter.is_active = True
                    newsletter.save()
                    return JsonResponse({
                        'success': True,
                        'message': 'Your subscription has been reactivated.'
                    }, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Newsletter subscribe error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Unable to process subscription. Please try again.'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Only POST method allowed'
    }, status=405)


# ============================================================
# API VIEWS (Django REST Framework)
# ============================================================

class ProjectViewSet(viewsets.ModelViewSet):
    """Secure Project ViewSet - Only shows completed projects to non-staff"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """✅ Only show completed projects unless user is staff"""
        if self.request.user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(status='completed')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """✅ Secure single project retrieval"""
        try:
            project = self.get_object()
            
            # ✅ Double-check status for non-staff
            if not request.user.is_staff and project.status != 'completed':
                return Response({
                    'success': False,
                    'message': 'Project not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(project)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Http404:
            return Response({
                'success': False,
                'message': 'Project not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Project retrieve error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Unable to load project'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def handle_exception(self, exc):
        """✅ Prevent error leaks"""
        from rest_framework.exceptions import APIException
        if isinstance(exc, APIException):
            return super().handle_exception(exc)
        logger.error(f"Project viewset error: {str(exc)}")
        return Response({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GalleryViewSet(viewsets.ModelViewSet):
    queryset = GalleryImage.objects.filter(is_published=True)
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAuthenticated]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.filter(is_published=True)
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'  
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ServiceListSerializer
        return ServiceDetailSerializer


class ContactViewSet(viewsets.ModelViewSet):
    queryset = ContactInquiry.objects.all()
    serializer_class = ContactInquirySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']


# ============================================================
# GENERIC API VIEWS
# ============================================================

class ProjectListView(generics.ListAPIView):
    """✅ Only shows completed projects"""
    queryset = Project.objects.filter(status='completed').order_by('-created_at')
    serializer_class = ProjectListSerializer


class ProjectDetailView(generics.RetrieveAPIView):
    """✅ Secure project detail - only completed projects"""
    queryset = Project.objects.filter(status='completed')
    serializer_class = ProjectDetailSerializer
    lookup_field = 'slug'


class GalleryListView(generics.ListAPIView):
    queryset = GalleryImage.objects.filter(is_published=True).order_by('order')
    serializer_class = GalleryImageSerializer


class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.filter(is_published=True).order_by('order')
    serializer_class = ServiceListSerializer


class ServiceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceDetailSerializer
    lookup_field = 'slug'


class ContactInquiryCreateView(generics.CreateAPIView):
    queryset = ContactInquiry.objects.all()
    serializer_class = ContactInquirySerializer


# ============================================================
# JOURNAL API VIEWS - ✅ FIXED
# ============================================================

@api_view(['GET'])
def journal_api_list(request):
    try:
        articles = Journal.objects.filter(status='published').order_by('-published_date')
        
        category_slug = request.GET.get('category')
        if category_slug:
            category = get_object_or_404(JournalCategory, slug=category_slug)
            articles = articles.filter(categories=category)
        
        q = request.GET.get('q')
        if q:
            articles = articles.filter(
                models.Q(title__icontains=q) | 
                models.Q(excerpt__icontains=q) | 
                models.Q(content__icontains=q)
            )
        
        serializer = JournalListSerializer(articles, many=True, context={'request': request})
        return Response({
            'success': True,
            'count': articles.count(),
            'articles': serializer.data
        })
    except Exception as e:
        logger.error(f"Journal API list error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Unable to fetch articles'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def journal_api_detail(request, slug):
    try:
        article = get_object_or_404(Journal, slug=slug, status='published')
        article.views += 1
        article.save(update_fields=['views'])
        serializer = JournalSerializer(article, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Http404:
        return Response({
            'success': False,
            'message': 'Article not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Journal API detail error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Unable to load article'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def journal_api_comment(request, slug):
    try:
        article = get_object_or_404(Journal, slug=slug, status='published')
        
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        comment_text = request.data.get('comment', '').strip()
        
        if not name or not comment_text:
            return Response({
                'success': False,
                'message': 'Name and comment are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if email:
            is_valid, _ = validate_email_strict(email)
            if not is_valid:
                return Response({
                    'success': False,
                    'message': 'Invalid email format'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(comment_text) > 5000:
            return Response({
                'success': False,
                'message': 'Comment too long. Maximum 5000 characters allowed.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        comment = JournalComment.objects.create(
            article=article,
            name=name,
            email=email,
            comment=comment_text,
            is_approved=False
        )
        
        return Response({
            'success': True,
            'message': 'Comment submitted successfully. It will appear after approval.',
            'comment_id': comment.id
        }, status=status.HTTP_201_CREATED)
    except Http404:
        return Response({
            'success': False,
            'message': 'Article not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Journal API comment error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Unable to submit comment. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def journal_api_categories(request):
    try:
        categories = JournalCategory.objects.annotate(
            article_count=models.Count('articles', filter=models.Q(articles__status='published'))
        ).order_by('name')
        data = [
            {
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'description': cat.description,
                'count': cat.article_count
            }
            for cat in categories
        ]
        return Response({
            'success': True,
            'categories': data
        })
    except Exception as e:
        logger.error(f"Journal API categories error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Unable to fetch categories'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def journal_api_tags(request):
    try:
        tags = JournalTag.objects.annotate(
            article_count=models.Count('articles', filter=models.Q(articles__status='published'))
        ).order_by('name')
        data = [
            {
                'id': tag.id,
                'name': tag.name,
                'slug': tag.slug,
                'count': tag.article_count
            }
            for tag in tags
        ]
        return Response({
            'success': True,
            'tags': data
        })
    except Exception as e:
        logger.error(f"Journal API tags error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Unable to fetch tags'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def journal_api_featured(request):
    try:
        articles = Journal.objects.filter(status='published', featured=True).order_by('-published_date')
        serializer = JournalListSerializer(articles, many=True, context={'request': request})
        return Response({
            'success': True,
            'featured': serializer.data
        })
    except Exception as e:
        logger.error(f"Journal API featured error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Unable to fetch featured articles'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================
# AWARDS API - ✅ FIXED
# ============================================================

@api_view(['GET'])
def awards_api_list(request):
    try:
        awards = Award.objects.all().order_by('-year')
        
        year = request.GET.get('year')
        if year and year.isdigit():
            awards = awards.filter(year=int(year))
        
        featured = request.GET.get('featured')
        if featured == 'true':
            awards = awards.filter(featured=True)
        
        data = [
            {
                'id': award.id,
                'title': award.title,
                'slug': award.slug,
                'organization': award.organization,
                'year': award.year,
                'description': award.description,
                'image': award.image.url if award.image else None,
                'location': award.location,
                'link': award.link,
                'featured': award.featured,
            }
            for award in awards
        ]
        return Response({
            'success': True,
            'awards': data
        })
    except Exception as e:
        logger.error(f"Awards API list error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Unable to fetch awards'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)