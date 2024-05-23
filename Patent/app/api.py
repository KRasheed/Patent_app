# Logging and Exception Handling
import os
import json
import logging
import traceback

# Third-party imports
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Models
from app.models import (
    TextInput,
    TextInputForCustom,
    SectionGeneratorInput,
    AbstractGen,
    FigureDescGen,
    PatentDoc,
)

# Utilities
from app.Utils.s3_bucket import download_file_from_s3, upload_file_to_s3
from app.Utils.read_file import read_file, encode_image, remove_folder
from app.Utils.Doc_Format.doc_file_maker import make_patent_application
from app.Utils.payload_util import format_payload_seq, remove_empty_keys

# Generation
from app.Utils.Generation_Proc.title import process_title
from app.Utils.Generation_Proc.bg_section import process_background_section
from app.Utils.Generation_Proc.summary_section import process_brief_summary
from app.Utils.Generation_Proc.brief_desc import process_brief_desc
from app.Utils.Generation_Proc.detailed_desc import process_detailed_desc

from app.Utils.Generation_Util.generations import (
    gen_figures_description,
    generation_of_abstract,
    rephrase_text,
    summarize_text,
    custom_prompt,
    generate_word_def,
)

# docs_url=None, redoc_url=None add to FASTAPI object before production
app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# Endpoint for generating title
@app.get("/generate-title")
async def generate_title(
        patent: str = Query(..., description="The patent name"),
        include_custom_template: str = Query(..., description="The type parameter"),
):
    try:
        file_types = ["claims", "disclosure", "transcript"]
        if include_custom_template:
            file_types.append("customTemplate")
        title, claims = await process_title(patent, file_types)
        return {"title": title, "claims": claims, "status": True}

    except ValueError as ve:
        logging.error(f"ValueError: {str(ve)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid input or Missing Parameter: {ve}"
        )
    except FileNotFoundError as fe:
        logging.error(f"FileNotFoundError: {str(fe)}")
        raise HTTPException(status_code=404, detail=f"Required file not found: {fe}")
    except Exception as e:
        logging.error(f"Exception: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Endpoint for generating background section
@app.post("/background-section")
async def generate_background(bg_input: SectionGeneratorInput):
    try:
        banned_words_list = ", ".join(f"'{s}'" for s in bg_input.profanity_listing)
        final_summary = read_file("Patent_Files", bg_input.patent, "final_summary.txt")
        background = await process_background_section(
            bg_input.title,
            bg_input.template_type,
            final_summary,
            bg_input.patent,
            banned_words_list,
        )
        return {"background": background, "status": True}

    except ValueError as ve:
        logging.error(f"ValueError: {str(ve)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid input or Missing Parameter: {ve}"
        )
    except FileNotFoundError as fe:
        logging.error(f"FileNotFoundError: {str(fe)}")
        raise HTTPException(status_code=404, detail=f"Required file not found: {fe}")
    except Exception as e:
        logging.error(f"Exception: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Endpoint for generating summary section
@app.post("/brief-summary")
async def generate_brief_summary(gen_input: SectionGeneratorInput):
    try:
        banned_word_list = ", ".join(f"'{s}'" for s in gen_input.profanity_listing)
        final_summary = read_file("Patent_Files", gen_input.patent, "final_summary.txt")
        claims = read_file("Patent_Files", gen_input.patent, "patent_claims.txt")
        summary = await process_brief_summary(
            gen_input.title,
            gen_input.template_type,
            final_summary,
            claims,
            gen_input.patent,
            banned_word_list,
        )
        return {"brief-desc": summary, "status": True}

    except ValueError as ve:
        logging.error(f"ValueError: {str(ve)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid input or Missing Parameter: {ve}"
        )
    except FileNotFoundError as fe:
        logging.error(f"FileNotFoundError: {str(fe)}")
        raise HTTPException(status_code=404, detail=f"Required file not found: {fe}")
    except Exception as e:
        logging.error(f"Exception: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Endpoint for generating brief drawing description section
@app.post("/brief-description")
async def generate_brief_description(gen_input: SectionGeneratorInput):
    try:
        banned_word_list = ", ".join(f"'{s}'" for s in gen_input.profanity_listing)
        final_summary = read_file("Patent_Files", gen_input.patent, "final_summary.txt")
        claims = read_file("Patent_Files", gen_input.patent, "patent_claims.txt")
        summary = await process_brief_desc(
            gen_input.title,
            gen_input.template_type,
            final_summary,
            claims,
            gen_input.patent,
            banned_word_list,
        )
        return {"brief-summary": summary, "status": True}

    except ValueError as ve:
        logging.error(f"ValueError: {str(ve)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid input or Missing Parameter: {ve}"
        )
    except FileNotFoundError as fe:
        logging.error(f"FileNotFoundError: {str(fe)}")
        raise HTTPException(status_code=404, detail=f"Required file not found: {fe}")
    except Exception as e:
        logging.error(f"Exception: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Endpoint for generating detailed description section
@app.post("/detailed-description")
async def generate_detailed_description(gen_input: SectionGeneratorInput):
    try:
        banned_word_list = ", ".join(f"'{s}'" for s in gen_input.profanity_listing)
        final_summary = read_file("Patent_Files", gen_input.patent, "final_summary.txt")
        claims = read_file("Patent_Files", gen_input.patent, "patent_claims.txt")
        detailed_description = await process_detailed_desc(
            gen_input.title,
            gen_input.template_type,
            final_summary,
            claims,
            gen_input.patent,
            banned_word_list,
        )
        return {"detailed-description": detailed_description, "status": True}

    except ValueError as ve:
        logging.error(f"ValueError: {str(ve)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid input or Missing Parameter: {ve}"
        )
    except FileNotFoundError as fe:
        logging.error(f"FileNotFoundError: {str(fe)}")
        raise HTTPException(status_code=404, detail=f"Required file not found: {fe}")
    except Exception as e:
        logging.error(f"Exception: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Function to generate figure description
@app.post("/figure-description")
async def generate_figure_desc(fig_input: FigureDescGen):
    try:
        final_summary = read_file("Patent_Files", fig_input.patent, "final_summary.txt")
        claims = read_file("Patent_Files", fig_input.patent, "patent_claims.txt")

        banned_word_list = ", ".join(f"'{s}'" for s in fig_input.profanity_listing)

        directory_path = os.path.join("temp", fig_input.patent, "images")
        os.makedirs(directory_path, exist_ok=True)

        image_file_path = download_file_from_s3(
            fig_input.s3_image_key, directory_path, fig_input.file_name
        )

        with open(image_file_path, "rb") as file:
            image_data = file.read()

        base64_image = encode_image(image_data)

        description = await gen_figures_description(
            fig_input.title,
            claims,
            final_summary,
            fig_input.prompt,
            banned_word_list,
            base64_image,
        )
        return {"fig_desc": description, "status": True}
    except ValueError as ve:
        logging.error(f"ValueError: {str(ve)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid input or Missing Parameter: {ve}"
        )
    except FileNotFoundError as fe:
        logging.error(f"FileNotFoundError: {str(fe)}")
        raise HTTPException(status_code=404, detail=f"Required file not found: {fe}")
    except Exception as e:
        logging.error(f"Exception: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Endpoint for generating claims section
@app.post("/abstract")
async def generate_abstract(abstract_input: AbstractGen):
    try:
        banned_word_list = ", ".join(f"'{s}'" for s in abstract_input.profanity_listing)
        final_summary = read_file(
            "Patent_Files", abstract_input.patent, "final_summary.txt"
        )
        claims = read_file("Patent_Files", abstract_input.patent, "patent_claims.txt")
        abstract = await generation_of_abstract(
            abstract_input.title, claims, final_summary, banned_word_list
        )
        return {"abstract": abstract, "status": True}

    except ValueError as ve:
        logging.error(f"ValueError: {str(ve)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid input or Missing Parameter: {ve}"
        )
    except FileNotFoundError as fe:
        logging.error(f"FileNotFoundError: {str(fe)}")
        raise HTTPException(status_code=404, detail=f"Required file not found: {fe}")
    except Exception as e:
        logging.error(f"Exception: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Endpoint for rephrasing text
@app.post("/rephrase")
async def rephrase_text_post(input_data: TextInput):
    try:
        rephrased = await rephrase_text(input_data.text)
        return {"rephrased_text": rephrased, "status": True}

    except ValueError as ve:
        logging.error(f"ValueError: {str(ve)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid input or Missing Parameter: {ve}"
        )
    except FileNotFoundError as fe:
        logging.error(f"FileNotFoundError: {str(fe)}")
        raise HTTPException(status_code=404, detail=f"Required file not found: {fe}")
    except Exception as e:
        logging.error(f"Exception: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Endpoint for summarizing text
@app.post("/summarize")
async def summarize(input_data: TextInput):
    try:
        summarize_data = await summarize_text(input_data.text)
        return {"summarize_text": summarize_data, "status": True}

    except ValueError as ve:
        logging.error(f"ValueError: {str(ve)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid input or Missing Parameter: {ve}"
        )
    except FileNotFoundError as fe:
        logging.error(f"FileNotFoundError: {str(fe)}")
        raise HTTPException(status_code=404, detail=f"Required file not found: {fe}")
    except Exception as e:
        logging.error(f"Exception: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Endpoint for generating text using custom prompt
@app.post("/user-custom-prompt")
async def user_custom_prompt(input_data: TextInputForCustom):
    try:
        summarize_data = await custom_prompt(input_data.text, input_data.prompt)
        return {"custom_prompt": summarize_data, "status": True}

    except ValueError as ve:
        logging.error(f"ValueError: {str(ve)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid input or Missing Parameter: {ve}"
        )
    except FileNotFoundError as fe:
        logging.error(f"FileNotFoundError: {str(fe)}")
        raise HTTPException(status_code=404, detail=f"Required file not found: {fe}")
    except Exception as e:
        logging.error(f"Exception: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Endpoint for generating word definition
@app.post("/define-word")
async def define_word(input_data: TextInput):
    try:
        word_definition = await generate_word_def(input_data.text)
        return {"word_definition": word_definition, "status": True}

    except ValueError as ve:
        logging.error(f"ValueError: {str(ve)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid input or Missing Parameter: {ve}"
        )
    except FileNotFoundError as fe:
        logging.error(f"FileNotFoundError: {str(fe)}")
        raise HTTPException(status_code=404, detail=f"Required file not found: {fe}")
    except Exception as e:
        logging.error(f"Exception: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Endpoint for uploading file
@app.post("/upload-file")
async def upload_file(user_data: PatentDoc):
    try:
        patent_id = user_data.patent
        formatted_payload = remove_empty_keys(format_payload_seq(user_data.subheading_sequence, user_data.user_payload))

        file_name, file_path = make_patent_application(patent_id, formatted_payload)
        main_file_upload_url = upload_file_to_s3(file_name, patent_id)
        remove_folder(f"Upload_File/{patent_id}")
        return {"status": True, "file_url": main_file_upload_url}
    except Exception as e:
        logging.error(f"Exception: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
