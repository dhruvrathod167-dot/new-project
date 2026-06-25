# myapp/api_urls.py

from django.urls import path
from . import views

app_name = 'myapp_api'

urlpatterns = [
    # 🔒 Authentication
    path('auth/login/', views.api_login, name='api_login'),
    
    # Projects
    path('projects/', views.ProjectListView.as_view(), name='api_projects'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='api_project_detail'),
    
    # Gallery
    path('gallery/', views.GalleryListView.as_view(), name='api_gallery'),
    
    # Services
    path('services/', views.ServiceListView.as_view(), name='api_services'),
    path('services/<slug:slug>/', views.ServiceDetailView.as_view(), name='api_service_detail'),
    
    # Contact
    path('contact/', views.contact_submit, name='api_contact'),
    
    # Newsletter
    path('newsletter/', views.newsletter_subscribe, name='api_newsletter'),
    
    # Journal
    path('journal/', views.journal_api_list, name='api_journal_list'),
    path('journal/<slug:slug>/', views.journal_api_detail, name='api_journal_detail'),
    path('journal/<slug:slug>/comment/', views.journal_api_comment, name='api_journal_comment'),
    path('journal-categories/', views.journal_api_categories, name='api_journal_categories'),
    path('journal-tags/', views.journal_api_tags, name='api_journal_tags'),
    path('journal-featured/', views.journal_api_featured, name='api_journal_featured'),
    
    # Awards
    path('awards/', views.awards_api_list, name='api_awards'),
    
    # Products
    path('products/', views.get_products, name='api_products'),
    path('products/add/', views.add_product, name='api_add_product'),
    path('products/<int:product_id>/', views.product_detail_api, name='api_product_detail'),
]