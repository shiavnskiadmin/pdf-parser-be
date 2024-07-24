from typing import List
from pydantic import BaseModel

class ImageUrl(BaseModel):
    image_url: dict


class Coordinates(BaseModel):
    width: int
    height: int
    x: float
    y: float

class Label(BaseModel):
    labelName: str
    coordinates: Coordinates
    page: int

class TemplateWithMetaItem(BaseModel):
    annoted_region: List[Label]
    company_name: str
    pdf_base64_img: str
    pdf_category: str
    multipage: bool
    hasTables: bool
    pdf_name: str
    pdf_sub_category: str
    pdf_sub_sub_category: str
    id: str

    class Config:
        orm_mode = True