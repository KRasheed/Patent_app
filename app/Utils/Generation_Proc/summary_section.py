import re
from app.Utils.Generation_Util.extract_headings import (
    check_for_enclosed_text,
    extract_paragraphs_from_template,
)
from app.Utils.Generation_Util.generations import generation_of_summary


def determine_heading(available_headings):
    preferred_order = ["Brief Summary", "Summary", "SUMMARY", "BRIEF SUMMARY"]
    for heading in preferred_order:
        if heading in available_headings:
            return heading
    return None


def extract_brief_summary(extracted_paragraphs):
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


async def process_brief_summary(
    title,
    template_type,
    combined_file_summary,
    claims_file,
    patent_name,
    banned_word_list,
):
    generated_brief_summary = {}

    extracted_paragraphs, _ = extract_paragraphs_from_template(
        template_type, patent_name
    )
    brief_summary_section_dict = extract_brief_summary(extracted_paragraphs)

    for heading, paragraphs in brief_summary_section_dict.items():
        generated_brief_summary[heading] = []

        for paragraph in paragraphs:
            while check_for_enclosed_text(paragraph):
                title_replaced = False

                if re.search(r"\[\[title\]\]", paragraph, re.IGNORECASE):
                    paragraph = re.sub(
                        r"\[\[title\]\]", title.lower(), paragraph, flags=re.IGNORECASE
                    )
                    title_replaced = True

                if re.search(r"\[\[.*?\]\]", paragraph):
                    summary_section = await generation_of_summary(
                        title,
                        combined_file_summary,
                        claims_file,
                        paragraph,
                        banned_word_list,
                    )
                    summary_section = summary_section.split("\n\n")

                    for summary_para in summary_section:
                        summary_para = ensure_newline_start(summary_para)
                        generated_brief_summary[heading].append(summary_para)
                    break

                elif title_replaced:
                    paragraph = ensure_newline_start(paragraph)
                    generated_brief_summary[heading].append(paragraph)
                    break

            else:
                paragraph = ensure_newline_start(paragraph)
                generated_brief_summary[heading].append(paragraph)

    return generated_brief_summary
