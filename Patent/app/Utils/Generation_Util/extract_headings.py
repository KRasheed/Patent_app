import re
import os

from app.Utils.read_file import read_file


def check_for_enclosed_text(s):
    curly_braces_pattern = r"\{\{.*?\}\}"
    square_braces_pattern = r"\[\[.*?\]\]"

    if re.search(curly_braces_pattern, s) or re.search(square_braces_pattern, s):
        return True
    else:
        return False


def check_and_pop_title(section_list):
    first_element = section_list[0]
    pattern = r"(?i)\[\[title(?:\s*{{.*?}})?\]\]"
    if re.match(pattern, first_element):
        section_list.pop(0)
    elif section_list:  # Ensure the list is not empty
        first_element = section_list[0].strip().lower()  # Normalize case and whitespace
        if first_element == "title":
            section_list.pop(0)


def is_capitalized(s):
    return all(word[0].isupper() if word else False for word in s.split())


def contains_forbidden_punctuation(s):
    forbidden_punctuation = [":", ".", ";", ","]
    return any(punc in s for punc in forbidden_punctuation)


def extract_headings_subheadings_from_text(text):
    items = []
    lines = text.split("\n")

    # forbidden_headings = ['CLAIMS', 'ABSTRACT', 'aBSTRACT', 'ABSTRACTS', 'abstract', 'Abstract', 'Claims', 'claims']

    for line in lines:
        stripped_line = line.strip()

        if contains_forbidden_punctuation(stripped_line):
            continue

        if stripped_line.lower() == "[[title]]":
            items.append(stripped_line)

        elif is_capitalized(
            stripped_line
        ):  # and stripped_line not in forbidden_headings:
            items.append(stripped_line)

        elif (
            len(stripped_line) < 50 and "[[" not in stripped_line
        ):  # and stripped_line not in forbidden_headings:
            items.append(stripped_line)
    return items


def extract_paragraphs_by_headings(text, headings):
    headings = [h.strip() for h in headings]
    paragraphs = {heading: "" for heading in headings}
    current_heading = None

    lines = text.split("\n")
    for line in lines:
        clean_line = line.strip()
        for heading in headings:
            if clean_line.startswith(heading):
                current_heading = heading
                break
        else:
            if current_heading:
                paragraphs[current_heading] += line + "\n"
    return paragraphs


def extract_paragraphs_from_template(template, patent_name):
    new_template = template_type_check(template, patent_name)
    headings_subheadings = extract_headings_subheadings_from_text(new_template)
    section_list = list(filter(None, headings_subheadings))
    check_and_pop_title(section_list)
    extracted_paragraphs = extract_paragraphs_by_headings(new_template, section_list)
    return extracted_paragraphs, section_list


def template_type_check(template_type, patent_name):
    if template_type not in ["software", "hardware", "custom"]:
        raise ValueError("Invalid template type")
    elif template_type == "software":
        template_path = "Templates/Software_Template.docx"
        new_template = read_file(template_path)
    elif template_type == "hardware":
        template_path = "Templates/Hardware_Template.docx"
        new_template = read_file(template_path)
    elif template_type == "custom":
        new_template = read_file(
            "temp", patent_name, "custom_template/input_customTemplate.docx"
        )
    return new_template
