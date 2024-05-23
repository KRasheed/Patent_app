import os

from app.Utils.Generation_Util.generations import generation_of_title
from app.Utils.claims_text import claims_maker
from app.Utils.s3_bucket import get_patent_file
from app.Utils.text_processing import final_summary_chunk, chunk_summarize
from app.Utils.read_file import save_text_to_file


def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    except IOError as e:
        raise IOError(f"An error occurred while reading the file {file_path}: {str(e)}")


async def process_title(patent, file_types):
    patent_folder = f"Patent_Files/{patent}"
    final_summary_path = os.path.join(patent_folder, "final_summary.txt")
    claims_path = os.path.join(patent_folder, "patent_claims.txt")

    get_patent_file(file_types, patent)

    if os.path.exists(final_summary_path) and os.path.exists(claims_path):
        final_summary = read_file(final_summary_path)
        claims = read_file(claims_path)
        title = await generation_of_title(final_summary)
    else:
        chunks = final_summary_chunk(patent)
        final_summary = await chunk_summarize(chunks)
        title = await generation_of_title(final_summary)
        claims = await claims_maker(patent, final_summary, title)
        save_text_to_file("Patent_Files", final_summary, patent, "final_summary.txt")
        save_text_to_file("Patent_Files", claims, patent, "patent_claims.txt")

    return title, claims
