
import os
import uuid
import shutil
import django
django.setup()
from pathlib import Path
from fastapi import UploadFile
from django.conf import settings
from images.models import Image
from tenants.models import (
    EdgeBox
)

from django.core.files.base import ContentFile
from .integrity import validate_image_exists

def register_image_into_db(file, source=None, meta_info:dict=None):
    success = False
    result = ''
    try:
        file_ext = f".{file.filename.split('.')[-1]}"
        filename = file.filename.split(file_ext)[0]
        if validate_image_exists(filename=filename):
            result = {
                'filename': file.filename,
                'status': 'failed',
                'reason': 'Image already exists'
            }
            
            return success, result
        
        file_content = file.file.read()
        image = Image(
            image_name=filename,
            image_id=str(uuid.uuid4()),
            source_of_origin=source,
            meta_info=meta_info
        )
        image.image_file.save(
            file.filename, 
            ContentFile(file_content)
            )
        image.save()
        success = True
        result = 'success'
    except Exception as err:
        raise ValueError(f'failed to register image into db: {err}')
    
    return success, result
    
def save_image_file(file_path:str, file:UploadFile):
    success = False
    try:
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        
        file_path = Path(file_path + "/" + file.filename)
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)   
        
        success = True
    except Exception as err:
        raise ValueError(f'failed to save image file in {file_path}: {err}')
    
    return success 

def save_image(file, source=None, meta_info:dict=None):
    success = False
    try:
        success, result = register_image_into_db(
            file=file,
            source=source,
            meta_info=meta_info,
        ) 

        if not success:
            return success, result
        
        result = {
            'filename': file.filename,
            'status': 'success',
            }
        
        success = True
        
    except Exception as err:
        result = {
            'filename': file.filename,
            'status': 'failed',
            'reason': str(err)
        }
        
    return success, result

