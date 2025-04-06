# myapp/management/commands/compress_images.py
import io
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from images.models import Image 
from PIL import Image as PilImage

class Command(BaseCommand):
    help = "Compress all existing images and replace them with a compressed version."

    def handle(self, *args, **options):
        images = Image.objects.all()
        total = images.count()
        self.stdout.write(f"Found {total} images to compress.")
        
        for img_obj in images:
            try:
                # Open the original image from Azure Storage
                with default_storage.open(img_obj.image_file.name, 'rb') as f:
                    pil_img = PilImage.open(f)
                    pil_img.load()

                # Convert image to RGB if needed (JPEG requires RGB)
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")

                # Create a BytesIO buffer to hold the compressed image
                buffer = io.BytesIO()
                pil_img.save(buffer, format="JPEG", quality=60, optimize=True)
                buffer.seek(0)

                # Create a Django ContentFile from the buffer
                compressed_file = ContentFile(buffer.read())
                filename = img_obj.image_file.name

                # Optionally, delete the original file to avoid orphaned files
                if default_storage.exists(filename):
                    default_storage.delete(filename)
                
                # Save the compressed file back to the same path (this re-uploads to Azure)
                img_obj.image_file.save(filename, compressed_file, save=False)
                img_obj.save()

                self.stdout.write(self.style.SUCCESS(f"Compressed image {img_obj.image_name}"))
            except Exception as e:
                self.stderr.write(f"Error compressing image {img_obj.image_name}: {e}")
