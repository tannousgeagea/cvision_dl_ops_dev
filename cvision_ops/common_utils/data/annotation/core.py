import os
import uuid
import django
import shutil
django.setup()
import numpy as np

from annotations.models import (
    Annotation
)



def xyxy2xywh(xyxy):
    """
    Convert bounding box coordinates from (xmin, ymin, xmax, ymax) format to (x, y, width, height) format.

    Parameters:
    - xyxy (Tuple[int, int, int, int]): A tuple representing the bounding box coordinates in (xmin, ymin, xmax, ymax) format.

    Returns:
    - Tuple[int, int, int, int]: A tuple representing the bounding box in (x, y, width, height) format. 
                                 (x, y) are  the center of the bounding box.
    """
    xmin, ymin, xmax, ymax = xyxy
    w = xmax - xmin
    h = ymax - ymin
    return (xmin + w/2, ymin + h/2, w, h)

def save_annotations_into_txtfile(annotations: Annotation, filename:str, dest:str):
    success = False
    try:
        file_name = f"{filename}.txt" 
        label_location = os.path.join(dest, "labels")
        os.makedirs(label_location, exist_ok=True)
        
        if not annotations.exists():
            with open(label_location + "/" + file_name, "w") as file:
                file.writelines([])
                return True
        
        data = [
            [ann.annotation_class.class_id] + list(xyxy2xywh(ann.data)) for ann in annotations
        ]
        
        lines = (("%g " * len(line)).rstrip() % tuple(line) + "\n" for line in data)
        with open(label_location + "/" + file_name, "w") as file:
            file.writelines(lines)
        success = True
            
    except Exception as err:
        raise ValueError(f"Error in saving annotation into txtfile: {err}")
    
    return success