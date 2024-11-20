import os
import math
import uuid
import time
import django
import shutil
django.setup()


from images.models import Image
from tenants.models import (
    Tenant,
    Plant,
    EdgeBox,
)


images = Image.objects.all()

for image in images:
    print(image.source_of_origin)
    if not image.source_of_origin:
        continue
    
    edge_box = EdgeBox.objects.get(edge_box_id=image.source_of_origin)
    image.edge_box = edge_box
    image.save()