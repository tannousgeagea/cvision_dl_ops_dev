
import os
import uuid
import django
import shutil
django.setup()
from typing import List, Dict
from django.conf import settings
from database.models import Image
from utils.data.integrity import validate_image_exists
from utils.data.integrity import validate_annotation_exists
from utils.data.annotation.utils import register_annotation_into_db
from utils.data.annotation.utils import save_annotation_raw_into_txtfile

def get_annotation_from_raw(data):
    success = False
    class_ids = []
    lines = []
    try:
        for obj in data:
            class_id = int(obj.get('class_id'))
            line = [class_id]
            if 'xyn' in obj.keys():
                xyn  = obj.get('xyn')            
                line = (*line, *xyn)
            
            if 'xyxyn' in obj.keys():
                xyxyn  = obj.get('xyn')            
                line = (*line, *xyxyn)
                
            if not class_id in class_ids.keys():
                class_ids[class_id] = str(class_id)
                
            lines.append(("%g " * len(line)).rstrip() %line + "\n")
            success = True
    except Exception as err:
        raise ValueError(f'failed to extract class_id and object coordinate from raw data: {err}')

    return success, class_ids, lines


def check_annotations_from_raw(data:List[Dict], task):
    success = False
    try:
        data = [obj for obj in data if 'class_id' in obj.keys()]
        if not len(data):
            return success, data
        
        if task == 'segmentation':
            data = [obj for obj in data if 'xyn' in obj.keys()]
            if not len(data):
                raise ValueError(f'Error in checking annotation content - xyn is missing')
            
        if task == 'detection':
            data = [obj for obj in data if 'xyxyn' in obj.keys()]
            if not len(data):
                raise ValueError(f'Error in checking annotation content - xyxyn is missing')  
            
        success = True
    except Exception as err:
        raise ValueError(f'Error in checking annotation content - something is missing: {err}')
        
    return success, data


def save_raw_annotation(data:List[Dict], project):
    success = False
    try:
        
        assert 'filename' in data.keys(), f'key: filename not found in data'
        assert 'objects' in data.keys(), f'key: objects not found in data'
        
        filename = data.get('filename')
        if not validate_image_exists(filename=filename):
            result = {
                'filename': filename,
                'status': 'failed',
                'reason': 'Image does not exist'
                }
            return success, result
         
        image = Image.objects.get(image_name=filename)
        if validate_annotation_exists(image=image, project=project):
            result = {
                'filename': filename,
                'status': 'failed',
                'reason': 'Annotation already exist'
            }
            return success, result
        
        _, objects = check_annotations_from_raw(
            data=data.get('objects'),
            task=project.project_type.project_type,
        )
        
        _, class_ids, lines = get_annotation_from_raw(data=objects) 
        
        file_path = settings.MEDIA_ROOT + "/labels"
        save_annotation_raw_into_txtfile(file_path=file_path, filename=f'{filename}.txt', data=lines)
        register_annotation_into_db(
            image=image, project=project, 
            annotation_file=f'labels/{filename}.txt',
            meta_info={
                cls_id: cls_name for cls_id, cls_name in class_ids.items()
            }
        )
        
        success = True
        result = {
            'filename': filename,
            'status': 'success',
        }
        
    except Exception as err:
        result = {
            'filename': filename,
            'status': 'failed',
            'reason': str(err)
        }
        
    return success, result
