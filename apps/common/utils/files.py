import os
import time
import uuid


def unique_image_path(instance, filename):
    ext = filename.split(".")[-1]
    unique_filename = f"{int(time.time())}_{uuid.uuid4().hex}.{ext}"
    folder = f"{instance.__class__.__name__.lower()}_images"
    return os.path.join(folder, unique_filename)
