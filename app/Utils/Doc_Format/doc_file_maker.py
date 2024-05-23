import os
import json

from app.Utils.Doc_Format.doc_func import (
    document,
    default_format,
    add_heading_with_style,
    add_subheading_with_style,
    add_paragraph_with_style,
    set_margins,
)


def make_patent_application(patent, new_payload):
    # Root Path
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )

    default_format()

    # Title
    title = new_payload["title"]
    add_heading_with_style(title.upper())

    # Background Section
    bg_tech_field = new_payload["background"]["Technical Field"]
    bg_desc = new_payload["background"]["Description of the Related Art"]

    add_heading_with_style("BACKGROUND")
    add_subheading_with_style("Technical Field")
    add_paragraph_with_style(bg_tech_field, True)

    add_subheading_with_style("Description of the Related Art")
    add_paragraph_with_style(bg_desc, True)

    # Brief Summary Section
    summary_section = new_payload["summary"]
    add_heading_with_style("BRIEF SUMMARY")
    for paragraph in summary_section:
        add_paragraph_with_style(paragraph, True)

    # Brief Description of the Drawings Section
    drawings_section = new_payload["brief_description_of_the_drawings"]
    add_heading_with_style("BRIEF DESCRIPTION OF DRAWINGS")
    for paragraph in drawings_section:
        add_paragraph_with_style(paragraph, True)

    # Detailed Description Section
    detailed_description = new_payload["detailed-description"]
    add_heading_with_style("DETAILED DESCRIPTION")
    for subheadings, paragraphs in detailed_description.items():
        add_subheading_with_style(subheadings)
        for paragraph in paragraphs:
            add_paragraph_with_style(paragraph, True)

    # Figures Section
    document.add_page_break()
    add_heading_with_style("FIGURES")

    # Claims Section
    document.add_page_break()
    claims_section = new_payload["claims"]
    add_heading_with_style("CLAIMS")
    add_paragraph_with_style(claims_section)

    # Abstract Section
    document.add_page_break()
    abstract_section = new_payload["abstract"]
    add_heading_with_style("ABSTRACT")
    add_paragraph_with_style(abstract_section)

    set_margins(document, 1, 1, 1, 1)

    # Save Document
    upload_directory = os.path.join(project_root, "Upload_File", patent)
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    file_name = f"{title}.docx"
    file_path = os.path.join(upload_directory, file_name)
    document.save(file_path)

    return file_name, file_path
