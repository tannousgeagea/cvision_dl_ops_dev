import os
import uuid
import django
import shutil
django.setup()
import numpy as np
from pathlib import Path
from typing import List, Dict
from django.conf import settings
from database.models import Image
from database.models import Project
from database.models import Annotation


def get_class_id_from_file(file):
    assert os.path.exists(file) ,f'File Not Found {file}'
    with open(file) as f:
        lb = [x.split()[0] for x in f.read().strip().splitlines() if len(x)]
        lb = np.array(lb, dtype=np.int8)
        lb = np.unique(lb).tolist()
        
    return lb

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

def check_annotations_from_file(file):
    """
    Extract bounding box data from a text file.

    This function reads a text file containing bounding box data. Each line in the file should 
    represent a bounding box or a polygon, starting with a class ID followed by the vertices coordinates.
    If a line contains more than 4 coordinates, it is treated as a polygon and converted to an axis-aligned
    bounding box. The function returns class IDs and bounding boxes.

    Parameters:
    - txt_file (str): The path to the text file containing the bounding box data.

    Returns:
    - A tuple of two lists, the first being class IDs and 
      the second being bounding boxes (each box either as (xmin, ymin, xmax, ymax) or as a polygon)
    """
    assert os.path.exists(file) ,f'File Not Found {file}'
    
    with open(file) as f:
        lb = [x.split() for x in f.read().strip().splitlines() if len(x)]
        lb = np.array(lb, dtype=np.float32)
        
    nl = len(lb)
    if nl:
        assert lb.shape[1] == 5, f"labels require 5 columns, {lb.shape[1]} columns detected"
        assert (lb >= 0).all(), f"negative label values {lb[lb < 0]}"
        assert (lb[:, 1:] <= 1).all(), f"non-normalized or out of bounds coordinates {lb[:, 1:][lb[:, 1:] > 1]}"
        _, i = np.unique(lb, axis=0, return_index=True)
        if len(i) < nl:  # duplicate row check
            lb = lb[i]  # remove duplicates
            msg = f"WARNING ⚠️ {file}: {nl - len(i)} duplicate labels removed"
            print(msg)
    else:
        lb = np.zeros((0, 5), dtype=np.float32)
    
    return lb


def check_annotations_from_raw(data:List[Dict], task):
    success = False
    try:
        data = [obj for obj in data if 'class_id' in obj.keys()]
        if not len(data):
            result = {
                'status': 'failed',
                'reason': 'could not find class_id in data.objects'
            }  
            return success, result, data
        
        if task == 'segmentation':
            data = [obj for obj in data if 'xyn' in obj.keys()]
            if not len(data):
                result = {
                    'status': 'failed',
                    'reason': 'could not find object coordinate [xyn] in data.objects'
                }  
                return success, result, data
            
        if task == 'detection':
            data = [obj for obj in data if 'xyxyn' in obj.keys()]
            if not len(data):
                result = {
                    'status': 'failed',
                    'reason': 'could not find object coordinate [xyxyn] in data.objects'
                }  
                return success, result, data
                
        success = True
        result = {
            'status': 'success'
        }
     
    except Exception as err:
        result = {
            'status': 'failed',
            'reason': str(err)
        }
        
    return success, result, data


def save_annotation_file(file_path, filename, file=None, lines=None):
    success = False
    try:
        assert file is None and lines is None, f'neither file or lines are given'
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        
        if file:
            file_path = Path(file_path + "/" + filename)
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        if lines is not None:
            with open(file_path + "/" + filename, 'w') as f:
                f.writelines(lines)
    
        success = True
    except Exception as err:
        raise ValueError(f'failed to save annotation file: {err}')

    return success


def register_annotation(image, project, annotation_file, meta_info):
    success = False
    try:
        annotation = Annotation()
        annotation.image = image
        annotation.project = project
        annotation.annotation_file = annotation_file
        annotation.meta_info = meta_info
        annotation.save()
        success = True
    except Exception as err:
        raise ValueError(f'failed to register annotation in DB: {err}')

    return success

def save_annotation(file, project_name, meta_info:dict=None):
    success = False
    try:
        project = Project.objects.get(project_name=project_name)
        if not Image.objects.filter(image_name=f'{file.filename.split(".txt")[0]}'): 
            result = {
                'filename': file.filename,
                'status': 'failed',
                'reason': 'Image does not exist'
            }
            return success, result
        
        image = Image.objects.get(image_name=f'{file.filename.split(".txt")[0]}')
        if Annotation.objects.filter(project=project, image=image).exists():
            result = {
                'filename': file.filename,
                'status': 'failed',
                'reason': 'Annotation already exist'
            }
            return success, result
        
        file_path = settings.MEDIA_ROOT + "/labels"
        save_annotation_file_success = save_annotation_file(file_path=file_path, file=file)
        if not save_annotation_file_success:
            result = {
                'filename': file.filename,
                'status': 'failed',
                'reason': 'failed to save annotation file'
            }
            return success, result
        
        lb = get_class_id_from_file(file=file_path)
        meta_info = {cls_id: str(cls_id) for cls_id in lb}
        save_annotation_success = register_annotation(
            image=image,
            project=project,
            annotation_file='labels/' + file.filename,
            meta_info=meta_info
        )
        
        if not save_annotation_success:
            result = {
                'filename': file.filename,
                'status': 'failed',
                'reason': 'failed to register annotation in db'
            }
            return success, result
        
        image.annotated = True
        image.save()
        
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

def save_raw_annotation(data:List[Dict], project):
    success = False
    try:
        
        assert 'filename' in data.keys(), f'key: filename not found in data'
        assert 'objects' in data.keys(), f'key: objects not found in data'
        
        filename = data.get('filename')
        if not Image.objects.filter(image_name=filename): 
            result = {
                'filename': filename,
                'status': 'failed',
                'reason': 'Image does not exist'
            }
            return success, result
        
        image = Image.objects.get(image_name=f'{filename.split(".txt")[0]}')
        if Annotation.objects.filter(project=project, image=image).exists():
            result = {
                'filename': filename,
                'status': 'failed',
                'reason': 'Annotation already exist'
            }
            return success, result
        
        check_annotation_success, check_annotation_result, objects = check_annotations_from_raw(
            data=data.get('objects'),
            task=project.project_type.project_type,
        )
        
        if not check_annotation_success:
            result = {
                'filename': filename,
                **check_annotation_result,
            }
            return success, result
        
        get_annotation_success, class_ids, lines = get_annotation_from_raw(data=objects) 
        if get_annotation_success:
            result = {
                'filename': file.filename,
                'status': 'failed',
                'reason': 'failed to extraxt annotations from data objects'
            }
            return success, result
        
        file_path = settings.MEDIA_ROOT + "/labels"
        save_annotation_success = save_annotation_file(file_path=file_path, lines=lines)
        if not save_annotation_success:
            result = {
                'filename': file.filename,
                'status': 'failed',
                'reason': 'failed to save annotation file'
            }
            return success, result
            
        annotation = Annotation()
        annotation.image = image
        annotation.project = project
        annotation.annotation_file = 'labels/' + filename + '.txt'
        annotation.meta_info = {
            'class_id': {
                cls_id: cls_name for cls_id, cls_name in class_ids.items()
            }
        }
        
        annotation.save()
        image.annotated = True
        image.save()
        
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

    