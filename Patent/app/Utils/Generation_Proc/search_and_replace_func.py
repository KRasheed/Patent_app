import re
import os

from app.Utils.Generation_Util.generations import (
    generation_of_claim_PCT_format,
    generation_of_claim_X_format,
    generation_of_step_claim_format
)

async def search_and_replace(paragraph, title, claims_file):
    if re.search(r"\[\[title\]\]", paragraph, re.IGNORECASE):
        paragraph = re.sub(
            r"\[\[TITLE\]\]", title.lower(), paragraph, flags=re.IGNORECASE
        )
    if re.search(r"\[\[Component X\]\]", paragraph):
        paragraph = paragraph.replace("[[Component X]]", title.lower())

    if re.search(r"\[\[Claim \d+\]\]", paragraph):
        paragraph = await generation_of_claim_X_format(paragraph, claims_file)

    if re.search(r"\[\[Claim \d+-PCT\]\]", paragraph):
        paragraph = await generation_of_claim_PCT_format(paragraph, claims_file)

    if re.search(r"\[\[Step \d+ of Claim \d+\]\]", paragraph):
        paragraph = await generation_of_step_claim_format(paragraph, claims_file)

    return paragraph
