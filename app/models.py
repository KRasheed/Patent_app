import json
from pydantic import BaseModel
from typing import List, Dict


# Data to be fetched from the user
class TextInputForCustom(BaseModel):
    text: str
    prompt: str


# Data to be fetched from the user
class TextInput(BaseModel):
    text: str


class SectionGeneratorInput(BaseModel):
    patent: str
    title: str
    template_type: str
    profanity_listing: List[str]


class FigureDescGen(BaseModel):
    patent: str
    title: str
    prompt: str
    profanity_listing: List[str]
    file_name: str
    s3_image_key: str


class AbstractGen(BaseModel):
    patent: str
    title: str
    profanity_listing: List[str]


# Downloading the generated document
class PatentDoc(BaseModel):
    patent: str
    subheading_sequence: Dict
    user_payload: Dict
