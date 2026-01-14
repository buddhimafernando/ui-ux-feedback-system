from PIL import Image
import os

def resize_image_if_needed(image_path: str, max_size: int = 2048) -> str:
    """
    Resize image if it's too large (helps with API token limits)
    
    Args:
        image_path: Path to image
        max_size: Maximum dimension (width or height)
        
    Returns:
        Path to resized image (or original if no resize needed)
    """
    img = Image.open(image_path)
    
    # Check if resize needed
    if max(img.size) <= max_size:
        return image_path
    
    # Calculate new size maintaining aspect ratio
    ratio = max_size / max(img.size)
    new_size = tuple(int(dim * ratio) for dim in img.size)
    
    # Resize
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Save with _resized suffix
    base, ext = os.path.splitext(image_path)
    resized_path = f"{base}_resized{ext}"
    img_resized.save(resized_path)
    
    print(f"📐 Resized {img.size} → {new_size}")
    return resized_path

def get_image_info(image_path: str) -> dict:
    """Get basic image information"""
    img = Image.open(image_path)
    return {
        "path": image_path,
        "size": img.size,
        "format": img.format,
        "mode": img.mode
    }