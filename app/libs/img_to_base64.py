import base64
from PIL import Image
import io

def convert_image_to_base64(image: Image.Image, format_hint: str = None) -> str:
    try:
        # Determine the image format
        image_format = "JPEG" if format_hint == "jpeg" else image.format
        if not image_format:
            image_format = "JPEG"
        
        # Save image to memory buffer with the determined format
        buffered = io.BytesIO()
        image.save(buffered, format=image_format)
        
        # Encode the image data to base64
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Construct data URL
        data_url = f"data:image/{image_format.lower()};base64,{image_base64}"
        return data_url
    except Exception as e:
        print(f"Error: {e}")
        return None