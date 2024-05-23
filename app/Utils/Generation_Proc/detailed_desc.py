import re
from app.Utils.Generation_Util.extract_headings import (
    extract_paragraphs_from_template,
    check_for_enclosed_text,
)
from app.Utils.Generation_Util.generations import (
    generation_of_detailed_description,
    gen_set_scene_desc,
    gen_desc_current_issues,
    gen_title_paragraph
)

from app.Utils.Generation_Proc.search_and_replace_func import search_and_replace


def determine_heading(available_headings):
    preferred_order = ["DETAILED DESCRIPTION", "Detailed Description"]
    for heading in preferred_order:
        if heading in available_headings:
            return heading
    return None


def determine_last_heading(available_headings):
    preferred_order = ["CLAIMS", "claims", "Claims"]
    for heading in preferred_order:
        if heading in available_headings:
            return heading
    return None


# Extract Detailed Description
def extract_detailed_description(section_list, extracted_paragraphs):
    detailed_desc_section_dict = {}

    heading = determine_heading(extracted_paragraphs.keys())
    last_heading = determine_last_heading(extracted_paragraphs.keys())
    detailed_subheading_list = section_list[
        section_list.index(heading) : section_list.index(last_heading)
    ]

    for subheading in detailed_subheading_list:
        paragraphs = extracted_paragraphs[subheading]
        paragraph_list = list(filter(None, paragraphs.split("\n")))
        detailed_desc_section_dict[subheading] = paragraph_list

    return detailed_desc_section_dict


# Process detailed description
async def process_detailed_desc(
    title,
    template_type,
    combined_file_summary,
    claims_file,
    patent_name,
    banned_word_list,
):
    extracted_paragraphs, section_list = extract_paragraphs_from_template(
        template_type, patent_name
    )
    detailed_desc_section_dict = extract_detailed_description(
        section_list, extracted_paragraphs
    )

    generated_detailed_description = {}

    for subheading, paragraphs in detailed_desc_section_dict.items():
        generated_detailed_description[subheading] = []
        for paragraph in paragraphs:
            paragraph = await search_and_replace(paragraph, title, claims_file)
            if check_for_enclosed_text(paragraph):
                if paragraph in [
                    "[[Set the scene/environment]]",
                    "[[Scene of the Invention]].",
                ]:
                    gen_paragraph = await gen_set_scene_desc(
                        title, combined_file_summary, banned_word_list
                    )

                elif paragraph in [
                    "[[Describe the problem with current technology]]",
                    "[[Problem with current technology]].",
                ]:
                    gen_paragraph = await gen_desc_current_issues(
                        title, combined_file_summary, banned_word_list
                    )

                elif re.match(r"\[\[title\]\]", subheading, re.IGNORECASE):
                    gen_paragraph = await gen_title_paragraph(
                        title, combined_file_summary, banned_word_list
                    )

                else:
                    gen_paragraph = await generation_of_detailed_description(
                        title,
                        subheading,
                        combined_file_summary,
                        claims_file,
                        paragraph,
                        banned_word_list,
                    )

                gen_paragraph = gen_paragraph.split("\n\n")

                for new_paragraph in gen_paragraph:
                    if not new_paragraph.startswith("\n"):
                        new_paragraph = "\n" + new_paragraph
                    generated_detailed_description[subheading].append(new_paragraph)
            else:
                if not paragraph.startswith("\n"):
                    paragraph = "\n" + paragraph
                generated_detailed_description[subheading].append(paragraph)

    generated_detailed_description = {
        title if k == "[[Title]]" else k: v
        for k, v in generated_detailed_description.items()
    }
    return generated_detailed_description
