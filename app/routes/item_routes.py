from fastapi import APIRouter, HTTPException, Request, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse
from app.models.item_models import TemplateWithMetaItem, ImageUrl
from typing import List
from app.libs.image_to_text import extract_text_image
from app.utils.elastic_search import get_es_client
from app.libs.img_to_base64 import convert_image_to_base64
from elasticsearch import Elasticsearch
import zipfile
import io
import requests, base64
from PIL import Image
from pdf2image import convert_from_bytes

item_router = APIRouter()

# Function to test Elasticsearch connection
def test_elasticsearch_connection():
    try:
        es = get_es_client()
        es.ping()  
        return True
    except ConnectionError:
        return False
    
if test_elasticsearch_connection():
    print("Connected to Elasticsearch successfully!")
else:
    print("Failed to connect to Elasticsearch.")

@item_router.post("/extract_text")
async def extract_text(request: Request, es: Elasticsearch = Depends(get_es_client)):
    try:
        data = await request.json()
        template_id = data.get('templateId')
        base64_data = data.get('pdf_base64_img')

        extract_text = await extract_text_image(es=es, template_id=template_id, base64_data=base64_data)

        return extract_text

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   

@item_router.post("/template")
async def template_for_pdf(request: Request, es: Elasticsearch = Depends(get_es_client)):
    try:
        data = await request.json()
        template_index = "template"  
        
        print(data)
        
        item = TemplateWithMetaItem(**data)
        
        # Index the data into Elasticsearch
        es.index(index=template_index, body=item.dict())


        return {
            "statusCode": 200,
            "body": "Record inserted successfully!",
            "data": item
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid data format")
    except Exception as e:
        print("Error:", e)
        return {
            "statusCode": 500,
            "body": str(e)
        }

@item_router.get("/template", response_model=List[TemplateWithMetaItem])
async def get_templates(es: Elasticsearch = Depends(get_es_client)):
    try:
        template_index = "template"  
        # Retrieve all data from Elasticsearch index
        results = es.search(index=template_index, body={"query": {"match_all": {}}})
        
        # Extract the hits from the results
        hits = results["hits"]["hits"] 

        # Return the data
        return [hit["_source"] for hit in hits]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving data from Elasticsearch")

@item_router.post("/upload_zip")
async def upload_zip(file: UploadFile = File(...), template_id: str = Form(...), es: Elasticsearch = Depends(get_es_client)):
    try:
        # Extract the ZIP file
        with zipfile.ZipFile(io.BytesIO(await file.read())) as z:
            extracted_files = [z.open(name) for name in z.namelist()] 

        results = []

        for extracted_file in extracted_files:
            filename = extracted_file.name
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Handle image files
                image = Image.open(extracted_file)
                base64_image = convert_image_to_base64(image)
                extracted_data = await extract_text_image(es, template_id, base64_image)
                results.append({
                    "filename": filename,
                    # "base64_image": base64_image,
                    "extracted_data": extracted_data
                })
            elif filename.lower().endswith('.pdf'):
                # Handle PDF files
                pdf_bytes = extracted_file.read()
                pages = convert_from_bytes(pdf_bytes)
                for page_number, page in enumerate(pages):
                    base64_image = convert_image_to_base64(page, format_hint="jpeg")  # Specify format_hint as "JPEG"
                    extracted_data = await extract_text_image(es, template_id, base64_image)
                    results.append({
                        "filename": f"page_{page_number + 1}_{filename}",
                        # "base64_image": base64_image,
                        "extracted_data": extracted_data
                    })

        return JSONResponse(content=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@item_router.post("/convert-pdf-to-images")
async def convert_pdf_to_images(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(content={"error": "The uploaded file is not a PDF"}, status_code=400)

    pdf_bytes = await file.read()
    pages = convert_from_bytes(pdf_bytes)
    images_base64 = []

    for page_number, page in enumerate(pages):
        base64_image = convert_image_to_base64(page, format_hint="jpeg")
        images_base64.append({
            "page_number": page_number + 1,
            "base64_image": base64_image
        })

    return JSONResponse(content={"images": images_base64})


@item_router.post("/convert-to-base64")
async def convert_to_base64(image_data: ImageUrl):
    try:
        base64_image_str = image_data.image_url["preview"].split(",")[1]  # Extract base64 part
        image_data_bytes = base64.b64decode(base64_image_str)
        image = Image.open(io.BytesIO(image_data_bytes))
        base64_image = convert_image_to_base64(image)
        if base64_image is None:
            raise HTTPException(status_code=500, detail="Failed to convert image to base64.")
        return {"base64_image": base64_image}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {e}")

