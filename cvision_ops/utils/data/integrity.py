
import django
django.setup()
from django.conf import settings
from database.models import Image
from database.models import Project
from database.models import Annotation

def validate_image_exists(filename):
    if Image.objects.filter(image_name=filename).exists(): 
        return True
        
    return False

def validate_annotation_exists(image, project):
    if Annotation.objects.filter(project=project, image=image).exists():
        return True

    return False