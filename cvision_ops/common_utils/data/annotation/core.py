import os
import uuid
import django
import shutil
django.setup()
import numpy as np
from pathlib import Path
from typing import List, Dict
from fastapi import UploadFile
from django.conf import settings
from common_utils.data.integrity import validate_image_exists
from common_utils.data.integrity import validate_annotation_exists
from .utils import save_annotation_file
from .utils import get_class_id_from_file
from .utils import register_annotation_into_db

def save_annotation(file, project_name, meta_info:dict=None):
    success = False
    try:
        filename = f'{file.filename.split(".txt")[0]}'
        project = Project.objects.get(project_name=project_name)
        if not validate_image_exists(filename=filename):
            result = {
                'filename': file.filename,
                'status': 'failed',
                'reason': 'Image does not exist'
                }
            return success, result
         
        image = Image.objects.get(image_name=filename)
        if validate_annotation_exists(image=image, project=project):
            result = {
                'filename': file.filename,
                'status': 'failed',
                'reason': 'Annotation already exist'
            }
            return success, result
        
        file_path = settings.MEDIA_ROOT + "/labels"
        save_annotation_file(file_path=file_path, file=file)
        
        lb = get_class_id_from_file(file=file_path + '/' + file.filename)
        register_annotation_into_db(
            image=image,
            project=project,
            annotation_file='labels/' + file.filename,
            meta_info={cls_id: str(cls_id) for cls_id in lb}
        )
        
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