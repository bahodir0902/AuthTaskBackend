from django.core.exceptions import ValidationError


def validate_image_size(image):
    max_size = 8 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError("Image size can't exceed 4 MB.")
