from django import template
from django.conf import settings
import os
from PIL import Image
import io
from django.core.cache import cache

register = template.Library()

@register.simple_tag
def optimized_image(image_path, width=None, height=None, quality=85):
    original_path = os.path.join(settings.STATIC_ROOT, image_path)
    cache_key = f"optimized_{image_path}_{width}_{height}_{quality}"
    
    # Vérifier le cache
    cached_url = cache.get(cache_key)
    if cached_url:
        return cached_url
    
    try:
        with Image.open(original_path) as img:
            # Conserver le ratio si une seule dimension est spécifiée
            if width and not height:
                ratio = width / float(img.size[0])
                height = int(float(img.size[1]) * float(ratio))
            elif height and not width:
                ratio = height / float(img.size[1])
                width = int(float(img.size[0]) * float(ratio))
            
            if width or height:
                img = img.resize((width or img.size[0], height or img.size[1]), Image.LANCZOS)
            
            output = io.BytesIO()
            img_format = img.format if img.format else 'JPEG'
            img.save(output, format=img_format, quality=quality, optimize=True)
            
            # Enregistrer dans le cache
            static_url = f"{settings.STATIC_URL}{image_path}"
            cache.set(cache_key, static_url, 60*60*24*30)  # Cache 30 jours
            
            return static_url
            
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return f"{settings.STATIC_URL}{image_path}"