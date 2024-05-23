import os
from langchain_openai import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from app.Utils.get_secrets import get_and_set_secrets

get_and_set_secrets()

# from dotenv import load_dotenv
# load_dotenv()

openai_llm = OpenAI(model="gpt-3.5-turbo-instruct",
                    api_key=os.getenv("OPENAI_API_KEY"),
                    organization=os.getenv("OPENAI_ORG_KEY"),
                    temperature=0.5, max_tokens=1000)


# Function to generate a final summary for the all the patent files
def final_summary_chunk(patent):
    temp_path = os.path.join('temp', patent)
    if not os.path.exists(temp_path):
        raise FileNotFoundError("No document found in this Patent! Please upload at least one document.")
    uploaded_files_path = os.path.abspath(temp_path)
    loader = DirectoryLoader(uploaded_files_path)
    chunks = loader.load_and_split(text_splitter=RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=150))
    return chunks


# Function to Summarize each chunk
async def chunk_summarize(chunks):
    chain = load_summarize_chain(openai_llm, chain_type="map_reduce")
    full_summary = await chain.ainvoke(chunks)
    output_text = full_summary["output_text"]
    return output_text.strip()

# <<----NOT NEEDED ANYMORE-->>
# # Function to format paragraph numbers
# def renumber_paragraphs_incrementally(text):
#     counter = [1]
#
#     def replacement(match):
#         replacement_text = f"[{counter[0]:04d}]"
#         counter[0] += 1
#         return replacement_text
#     new_text = re.sub(r'\[\d{4}]', replacement, text)
#     return new_text
#
#
# # Function to save document
# def save_as_word_document(text, output_file):
#     text = renumber_paragraphs_incrementally(text)
#     doc = Document()
#     doc.add_paragraph(text)
#     doc.save(output_file)
