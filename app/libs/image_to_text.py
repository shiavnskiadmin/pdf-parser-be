from fastapi import HTTPException
from app.libs.extract_data import extract_data

async def extract_text_image(es, template_id: str, base64_data: str):
    template_index = "template"

    if not base64_data:
        raise HTTPException(status_code=400, detail="Missing base64Data in request body")
    if not template_id:
        raise HTTPException(status_code=400, detail="Missing templateId in request body")

    try:
        # Retrieve the template from Elasticsearch
        response = es.search(index=template_index, body={
            "query": {
                "match": {
                    "id": template_id
                }
            }
        })

        # Check if any hits were returned
        if response['hits']['total']['value'] == 0:
            raise HTTPException(status_code=404, detail="Template not found")

        # Extract the template document
        template = response['hits']['hits'][0]['_source']

        # Extract 'annoted_region' from the template
        annoted_region_template = template.get('annoted_region')
        if not annoted_region_template:
            raise HTTPException(status_code=404, detail="Annotated regions not found in template")

        # Extract coordinates from annoted_region based on label and page number
        extracted_data = []

        for region in annoted_region_template:
            label_name = region.get('labelName')
            page = region.get('page')
            x = region['coordinates']['x']
            y = region['coordinates']['y']
            height = region['coordinates']['height']
            width = region['coordinates']['width']

            extracted_text = await extract_data(
                base64Data=base64_data,
                x=x,
                y=y,
                height=height,
                width=width
            )

            extracted_data.append({
                "labelName": label_name,
                "page": page,
                "extracted_data": extracted_text
            })

        return extracted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))