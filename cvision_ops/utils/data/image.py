
import os
import uuid
import shutil
import django
django.setup()
from pathlib import Path
from fastapi import UploadFile
from django.conf import settings
from database.models import Image
from .integrity import validate_image_exists

def register_image_into_db(image_id, image_name, image_file, meta_info:dict=None):
    success = False
    try:
        image = Image(
            image_name=image_name,
            image_id= image_id,
            image_file=image_file,
            meta_info=meta_info
        )
        image.save()
        success = True
    except Exception as err:
        raise ValueError(f'failed to register image into db: {err}')
    
    return success
    
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

def save_image(file, meta_info:dict=None):
    success = False
    try:
        file_ext = f".{file.filename.split('.')[-1]}"
        filename = file.filename.split(file_ext)[0]
        if validate_image_exists(filename=filename):
            result = {
                'filename': filename,
                'status': 'failed',
                'reason': 'Image already exists'
            }
            
            return success, result
        
        file_path = settings.MEDIA_ROOT + "/images"
        save_image_file(
            file_path=file_path, file=file
        )    
        
        register_image_into_db(
            image_id=str(uuid.uuid4()),
            image_name=filename,
            image_file=f'images/{file.filename}',
            meta_info=meta_info,
        )    

        result = {
            'filename': filename,
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

