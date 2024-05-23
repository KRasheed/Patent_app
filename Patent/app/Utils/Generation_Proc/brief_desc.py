import re
from app.Utils.Generation_Util.extract_headings import (
    check_for_enclosed_text,
    extract_paragraphs_from_template,
)
from app.Utils.Generation_Util.generations import (
    generation_of_brief_drawings_description,
)


def determine_heading(available_headings):
    preferred_order = [
        "Brief Description Of Drawings",
        "BRIEF DESCRIPTION OF DRAWINGS",
        "BRIEF DESCRIPTION OF THE DRAWINGS",
        "Brief Description of the Drawings",
    ]
    for heading in preferred_order:
        if heading in available_headings:
            return heading
    return None


def extract_brief_desc(extracted_paragraphs):
    heading = determine_heading(extracted_paragraphs.keys())
    section_dict = {}

    if heading:
        paragraphs = extracted_paragraphs[heading]
        paragraph_list = list(filter(None, paragraphs.split("\n")))
        section_dict[heading] = paragraph_list

    return section_dict


def ensure_newline_start(text):
    """Ensure text starts with a newline if it does not already."""
    if not text.startswith("\n"):
        text = "\n" + text
    return text


async def process_brief_desc(
    title,
    template_type,
    combined_file_summary,
    claims_file,
    patent_name,
    banned_word_list,
):
    generated_brief_desc = {}

    extracted_paragraphs, _ = extract_paragraphs_from_template(
        template_type, patent_name
    )
    brief_desc_section_dict = extract_brief_desc(extracted_paragraphs)

    for heading, paragraphs in brief_desc_section_dict.items():
        generated_brief_desc[heading] = []

        for paragraph in paragraphs:
            while check_for_enclosed_text(paragraph):
                title_replaced = False
                if re.search(r"\[\[title\]\]", paragraph, re.IGNORECASE):
                    paragraph = re.sub(
                        r"\[\[title\]\]", title.lower(), paragraph, flags=re.IGNORECASE
                    )
                    title_replaced = True

                if re.search(r"\[\[.*?\]\]", paragraph):
                    brief_desc_section = await generation_of_brief_drawings_description(
                        title,
                        combined_file_summary,
                        claims_file,
                        paragraph,
                        banned_word_list,
                    )
                    brief_desc_section = brief_desc_section.split("\n\n")
                    for brief_desc_paragraph in brief_desc_section:
                        brief_desc_paragraph = ensure_newline_start(
                            brief_desc_paragraph
                        )
                        generated_brief_desc[heading].append(brief_desc_paragraph)
                    break

                elif title_replaced:
                    paragraph = ensure_newline_start(paragraph)
                    generated_brief_desc[heading].append(paragraph)
                    break
            else:
                paragraph = ensure_newline_start(paragraph)
                generated_brief_desc[heading].append(paragraph)

    return generated_brief_desc
