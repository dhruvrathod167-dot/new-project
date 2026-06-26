from .models import Project

def global_projects(request):
    return {'all_projects': Project.objects.all()}