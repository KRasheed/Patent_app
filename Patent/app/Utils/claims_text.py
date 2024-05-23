import os
import re

from app.Utils.Generation_Util.generations import generation_of_claims
from langchain_community.document_loaders import UnstructuredFileLoader


# Function for loading the claims file
def get_claims_loader(patent):
    temp_dir = os.path.join("temp", patent)
    files_check = os.listdir(temp_dir)
    claims_file_path = None
    for file_name in files_check:
        if file_name.startswith("input_claims."):
            claims_file_path = os.path.join(temp_dir, file_name)
            break
    if claims_file_path is not None:
        print("File check: ", claims_file_path)
        claims_file_url = os.path.abspath(claims_file_path)
        claims_loader = UnstructuredFileLoader(claims_file_url)
    else:
        claims_loader = None
    return claims_loader


# Function to create claims
async def claims_maker(patent, final_summary, title):
    claims_loader = get_claims_loader(patent)
    if claims_loader:
        claims_raw = claims_loader.load()
        page_content = claims_raw[0].page_content
        claims = re.sub(r"CLAIMS|Claims|Page\s+\d+\s+of\s+\d+|Docket No\.\s+[^\s]", "", page_content)
    else:
        claims = await generation_of_claims(title, final_summary)

    return claims
