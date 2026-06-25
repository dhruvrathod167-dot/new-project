from django.urls import path
from django.http import HttpResponse
from . import views

app_name = 'myapp'

def google_verify(request):
    return HttpResponse(
        "google-site-verification: googleb_Q7NJscK9es-oNQeMlnhGAIH8M7gA0MaDi9WAkW51Y.html",
        content_type="text/html"
    )

urlpatterns = [
    # Google Search Console Verification
    path('googleb_Q7NJscK9es-oNQeMlnhGAIH8M7gA0MaDi9WAkW51Y.html', google_verify, name='google_verify'),

    # Home
    path('', views.home, name='home'),
    path('api/login/', views.api_login, name='api_login'),

    # Public Pages
    path('philosophy/', views.philosophy, name='philosophy'),
    path('projects/', views.projects_list, name='projects'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('services/', views.services_page, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('awards/', views.awards_page, name='awards'),
    path('journal/', views.journal_page, name='journal'),
    path('journal/<slug:slug>/', views.journal_detail, name='journal_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('studio/', views.studio, name='studio'),
    path('contact/', views.contact_page, name='contact'),
    path('products/', views.products_page, name='products'),

    # Authentication (Secure)
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/dashboard/', views.dashboard_view, name='dashboard'),
    path('auth/profile/', views.profile_view, name='profile'),
    path('auth/users/', views.user_list_view, name='user_list'),
    path('auth/users/create/', views.user_create_view, name='user_create'),
    path('auth/users/<int:pk>/toggle/', views.user_toggle_active, name='user_toggle'),
]