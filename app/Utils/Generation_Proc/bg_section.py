from app.Utils.Generation_Util.extract_headings import extract_paragraphs_from_template
from app.Utils.Generation_Util.generations import generation_of_background


def extract_background_section(extracted_paragraphs):
    subheading1 = extracted_paragraphs["Technical Field"]
    subheading2 = extracted_paragraphs["Description of the Related Art"]
    text = f"""Technical Field\n\n{subheading1}\nDescription of the Related Art\n\n{subheading2}"""
    return text


async def process_background_section(
    title, template_type, combined_summary, patent_name, banned_words_list
):
    if not title or not combined_summary:
        raise ValueError("Missing title or combined summary")

    extracted_paragraphs, _ = extract_paragraphs_from_template(
        template_type, patent_name
    )
    background_section = extract_background_section(extracted_paragraphs)

    background = await generation_of_background(
        title, combined_summary, background_section, banned_words_list
    )
    sections = background.split("\n\n")

    # Extracting the technical field and description of the related art
    technical_field = sections[1].strip()
    description_related_art = sections[3].strip()
    # Creating a dictionary
    background_dict = {
        "Technical Field": technical_field,
        "Description of the Related Art": description_related_art,
    }

    return background_dict
