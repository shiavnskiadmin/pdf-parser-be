import base64
from PIL import Image
import io
import pytesseract

async def extract_data(base64Data, x, y, width, height):
    try:
        # Create image from base64 data
        # image_data = None
        # if ',' ijn base64Data:
        #     image_data = base64.b64decode(base64Data.split(",")[1])
        # else:
        #     image_data = base64.b64decode(base64Data)

        image_data = base64.b64decode(base64Data.split(",")[1])
        # print(image_data)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert coordinates to integer
        x, y, width, height = int(x), int(y), int(width), int(height)
        
        # Crop region from image
        cropped_image = image.crop((x, y, x + width, y + height))

        # Convert to grayscale
        cropped_image = cropped_image.convert('L')

        # Extract text using pytesseract
        extracted_text = pytesseract.image_to_string(cropped_image)

        return extracted_text
    except Exception as e:
        raise e

