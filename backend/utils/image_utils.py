"""
AURA AI - Image Processing Utilities
Pillow-based image editing, filters, and transformations
"""

import io
import logging
import base64
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw
import requests

logger = logging.getLogger(__name__)


def url_to_image(image_url):
    """Download an image from URL and return PIL Image object."""
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert('RGBA')
    except Exception as e:
        logger.error(f"Failed to load image from URL: {e}")
        raise


def image_to_base64(image, format='PNG'):
    """Convert PIL Image to base64 string."""
    buffer = io.BytesIO()
    if format == 'JPEG' and image.mode == 'RGBA':
        image = image.convert('RGB')
    image.save(buffer, format=format, quality=95)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


def image_to_bytes(image, format='PNG'):
    """Convert PIL Image to bytes."""
    buffer = io.BytesIO()
    if format == 'JPEG' and image.mode == 'RGBA':
        image = image.convert('RGB')
    image.save(buffer, format=format, quality=95)
    buffer.seek(0)
    return buffer.read()


def base64_to_image(b64_string):
    """Convert base64 string to PIL Image."""
    # Remove data URL prefix if present
    if ',' in b64_string:
        b64_string = b64_string.split(',')[1]
    image_data = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_data)).convert('RGBA')


def resize_image(image, width, height, maintain_aspect=True):
    """Resize image with optional aspect ratio preservation."""
    if maintain_aspect:
        image.thumbnail((width, height), Image.LANCZOS)
        return image
    return image.resize((width, height), Image.LANCZOS)


def crop_image(image, x, y, width, height):
    """Crop image to specified dimensions."""
    return image.crop((x, y, x + width, y + height))


def rotate_image(image, degrees, expand=True):
    """Rotate image by specified degrees."""
    return image.rotate(degrees, expand=expand, resample=Image.BICUBIC)


def flip_image(image, direction='horizontal'):
    """Flip image horizontally or vertically."""
    if direction == 'horizontal':
        return ImageOps.mirror(image)
    return ImageOps.flip(image)


def adjust_brightness(image, factor):
    """Adjust image brightness. Factor: 0.0=black, 1.0=original, 2.0=double."""
    enhancer = ImageEnhance.Brightness(image.convert('RGB'))
    return enhancer.enhance(factor)


def adjust_contrast(image, factor):
    """Adjust image contrast."""
    enhancer = ImageEnhance.Contrast(image.convert('RGB'))
    return enhancer.enhance(factor)


def adjust_saturation(image, factor):
    """Adjust image color saturation."""
    enhancer = ImageEnhance.Color(image.convert('RGB'))
    return enhancer.enhance(factor)


def apply_blur(image, radius=2):
    """Apply Gaussian blur to image."""
    return image.filter(ImageFilter.GaussianBlur(radius=radius))


def apply_sharpen(image, factor=2.0):
    """Apply sharpening to image."""
    enhancer = ImageEnhance.Sharpness(image.convert('RGB'))
    return enhancer.enhance(factor)


def apply_grayscale(image):
    """Convert image to black and white."""
    return ImageOps.grayscale(image).convert('RGB')


def apply_vintage_filter(image):
    """Apply vintage/sepia tone filter."""
    img = image.convert('RGB')
    r, g, b = img.split()
    r = r.point(lambda i: min(255, int(i * 1.1)))
    g = g.point(lambda i: int(i * 0.9))
    b = b.point(lambda i: int(i * 0.7))
    return Image.merge('RGB', (r, g, b))


def apply_hdr_filter(image):
    """Apply HDR-like filter with enhanced contrast and saturation."""
    img = image.convert('RGB')
    # Enhance contrast
    contrast_enhancer = ImageEnhance.Contrast(img)
    img = contrast_enhancer.enhance(1.4)
    # Enhance saturation
    color_enhancer = ImageEnhance.Color(img)
    img = color_enhancer.enhance(1.3)
    # Slight sharpness boost
    sharp_enhancer = ImageEnhance.Sharpness(img)
    img = sharp_enhancer.enhance(1.2)
    return img


def apply_neon_glow(image):
    """Apply neon glow effect."""
    img = image.convert('RGB')
    # Enhance brightness and saturation for glow
    img = ImageEnhance.Brightness(img).enhance(1.3)
    img = ImageEnhance.Color(img).enhance(2.0)
    # Apply soft blur for bloom effect
    blurred = img.filter(ImageFilter.GaussianBlur(radius=3))
    # Blend original and blurred
    return Image.blend(img, blurred, alpha=0.3)


def apply_cartoon_filter(image):
    """Apply cartoon-like filter."""
    img = image.convert('RGB')
    # Edge detection
    edges = img.filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.invert(edges)
    # Posterize for flat colors
    posterized = ImageOps.posterize(img, 3)
    # Multiply blend
    result = Image.blend(posterized, edges, alpha=0.1)
    return result


def apply_sketch_filter(image):
    """Apply pencil sketch filter."""
    img = image.convert('L')  # Grayscale
    # Invert
    inverted = ImageOps.invert(img)
    # Blur the inverted
    blurred = inverted.filter(ImageFilter.GaussianBlur(radius=10))
    # Dodge blend
    blurred_arr = blurred.point(lambda i: min(255, i + 1))
    
    def dodge(a, b):
        return min(255, int(a * 255 / (256 - b)))
    
    sketch = Image.new('L', img.size)
    for x in range(img.width):
        for y in range(img.height):
            a = img.getpixel((x, y))
            b = blurred_arr.getpixel((x, y))
            sketch.putpixel((x, y), dodge(a, b))
    
    return sketch.convert('RGB')


def remove_background(image):
    """
    Simple background removal using edge detection.
    For production, use rembg library or dedicated API.
    """
    img = image.convert('RGBA')
    # Create a simple mask based on corner color (assume background)
    corner_color = img.getpixel((0, 0))
    r, g, b, _ = corner_color
    
    data = img.getdata()
    new_data = []
    threshold = 40
    
    for item in data:
        ir, ig, ib, ia = item
        if (abs(ir - r) < threshold and
            abs(ig - g) < threshold and
            abs(ib - b) < threshold):
            new_data.append((ir, ig, ib, 0))  # Transparent
        else:
            new_data.append(item)
    
    img.putdata(new_data)
    return img


def upscale_image(image, scale=2):
    """Upscale image using Lanczos resampling."""
    new_width = image.width * scale
    new_height = image.height * scale
    return image.resize((new_width, new_height), Image.LANCZOS)


def apply_all_edits(image_url, edits):
    """Apply multiple edits to an image in sequence."""
    image = url_to_image(image_url)
    
    for edit_type, value in edits.items():
        if edit_type == 'brightness' and value != 1.0:
            image = adjust_brightness(image, value)
        elif edit_type == 'contrast' and value != 1.0:
            image = adjust_contrast(image, value)
        elif edit_type == 'saturation' and value != 1.0:
            image = adjust_saturation(image, value)
        elif edit_type == 'blur' and value > 0:
            image = apply_blur(image, value)
        elif edit_type == 'sharpen' and value > 0:
            image = apply_sharpen(image, value)
        elif edit_type == 'filter':
            filter_map = {
                'grayscale': apply_grayscale,
                'vintage': apply_vintage_filter,
                'hdr': apply_hdr_filter,
                'neon': apply_neon_glow,
                'cartoon': apply_cartoon_filter,
                'sketch': apply_sketch_filter
            }
            if value in filter_map:
                image = filter_map[value](image)
        elif edit_type == 'rotate' and value != 0:
            image = rotate_image(image, value)
        elif edit_type == 'flip':
            image = flip_image(image, value)
    
    return image
