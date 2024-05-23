import os

from openai import OpenAI, AsyncOpenAI

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

from dotenv import load_dotenv

load_dotenv()

# Uncomment before deploying
# from app.Utils.get_secrets import get_and_set_secrets
# get_and_set_secrets()

llm = ChatOpenAI(
    model_name="gpt-4-turbo",
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_KEY"),
    temperature=0.1,
)


# Function to generate a Title
async def generation_of_title(full_summary):
    prompt_template = """Generate a 'Title' for a Patent Application Based on the Provided Summary
    
    Summary:
    {full_summary}
    
    INSTRUCTIONS:
    - Craft a one-line title suitable for a professional patent application. 
    - Title SHOULD succinctly encapsulate the main invention or method described in the summary.
    - The title must end with the suffix "-tion" or "-ing", using a gerund form or an abstract noun to convey an ongoing process or action.
    - Ensure the title is concise, aiming for no more than 10 words to maintain professionalism and clarity.
    - AVOID vague or generic terms; the title should be specific and clearly related to the innovation detailed in the summary.
    - DO NOT include quotes or backticks around the title.
    - Title must directly relate to the content of the summary without any inconsistency.

    Example of a good title: Enhancing Photovoltaic Efficiency through Layered Filtration
    Example of a bad title: New Method for Solar Panels"""
    prompt_config = PromptTemplate(
        template=prompt_template, input_variables=["full_summary"]
    )
    chain_text = LLMChain(llm=llm, prompt=prompt_config)

    response = await chain_text.ainvoke(full_summary)
    response = (
        response["text"].replace("\n", "").replace(".", "").strip().split(":")[-1]
    )
    return response


# Function to generate a Background
async def generation_of_background(title, summary, template, banned_word_list):
    prompt_template = """Generate a Background section for a Patent Application based on the provided document summary and title.
  In the 'Description of the Related Art' section, focus on explaining the prior art without discussing the actual invention. Address the deficiencies of the prior art and describe the current state of the industry without mentioning the improvements provided by the invention being drafted. This will contextualize the reader and portray the prior art as somewhat inferior compared to the invention without directly discussing the invention itself.

  The Title of the invention is:

  {title}

  Here's the summary of the Patent:

  {summary}

  Here's the template of the Background section:

  {template}
  
  AVOID using the following words while generating the response:
  
  Claim, {banned_word_list}

  INSTRUCTIONS:
  - DO NOT remove the 'Technical Field' and 'Description of the Related Art'.
  - ONLY alter the content present in the enclosed square brackets given in 'template'.
  - ONLY generate a single paragraph for both 'Technical Field' and 'Description of the Related Art'.
  - ONLY for 'Technical Field', generate a short inventive description.
  - The Background Section SHOULD NOT be enclosed in quotes or backticks.
"""
    prompt_config = PromptTemplate(
        template=prompt_template,
        input_variables=["title", "summary", "template", "banned_word_list"],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(
        {
            "title": title,
            "summary": summary,
            "template": template,
            "banned_word_list": banned_word_list,
        }
    )
    return response["text"]


# Function to generate a Summary
async def generation_of_summary(title, summary, claims, paragraph, banned_word_list):
    prompt_template = """Generate the 'Brief Summary' of a Patent Application, guided by the Title, Summary, Claims, and provided Paragraph.

Title: {title}

Summary:
{summary}

Claims:
{claims}

Paragraph:
{paragraph}

AVOID using the following words while generating the response:
Claim, {banned_word_list}

INSTRUCTIONS:
- DO NOT make more than one paragraph.
- LIMIT TO ONLY ONE PARAGRAPH.
- DO NOT ADD THE HEADING 'Brief Summary'.
- Keep the content of the paragraph which is outside of [[]] brackets AS IT IS. DO NOT ALTER THE PARAGRAPH.
- WRITE the response like a professional Patent Application Personnel is making it.
- Focus on Generating Content Within Double Square Brackets ([[Content to be generated]]): Here, provide a detailed explanation or description that's specifically asked for within the context of the patent's technology or process.
- Generate Content Within Double Curly Brackets ({{Content to be generated and instruction inside to be followed}}): Ensure you closely follow the instructions provided within these brackets to generate content that's both relevant and adherent to the guidelines specified.
- Content Restrictions: Avoid using restricted terms as specified, including but not limited to generic terms such as "invention", or absolutes like "always", "critical". Ensure the language remains neutral, precise, and adheres to formal patent application standards.
- Integrate Relevant Claims: When the template requests specific claims (e.g., "Incorporate details from Claim 2"), locate the corresponding claim from the Claims section provided and integrate this information coherently into your description.
- Preservation of Non-variable Content: Do not modify, remove, or alter any part of the template that is not encased in double square brackets or double curly brackets. The integrity of the provided structure must be maintained.
- DO NOT output the Double Square Brackets and Double Curly Brackets as an output.
"""
    prompt_config = PromptTemplate(
        template=prompt_template,
        input_variables=["title", "summary", "claims", "paragraph", "banned_word_list"],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(
        {
            "title": title,
            "summary": summary,
            "claims": claims,
            "paragraph": paragraph,
            "banned_word_list": banned_word_list,
        }
    )
    return response["text"]


# Function to generate Brief Description of the Drawings
async def generation_of_brief_drawings_description(
    title, summary, claims, paragraph, banned_word_list
):
    prompt_template = """Generate the "Brief Description Of The Drawings" of a Patent Application, guided by the Title, Summary, Claims, and provided Paragraph.

Title: {title}

Summary:
{summary}

Claims:
{claims}

Paragraph:
{paragraph}

AVOID using the following words while generating the response:
Claim, {banned_word_list}

INSTRUCTIONS:
- ONLY replace the content present in [[]] with the respective variable. I.e. If the is asking for [[Title]], replace it with the variable Title.
- Focus on Generating Content Within Double Square Brackets ([[Content to be generated]]): Here, provide a detailed explanation or description that's specifically asked for within the context of the patent's technology or process.
- Generate Content Within Double Curly Brackets ({{Content to be generated and instruction inside to be followed}}): Ensure you closely follow the instructions provided within these brackets to generate content that's both relevant and adherent to the guidelines specified.
- Content Restrictions: Avoid using restricted terms as specified, including but not limited to generic terms such as "invention", or absolutes like "always", "critical". Ensure the language remains neutral, precise, and adheres to formal patent application standards.
- Integrate Relevant Claims: When the template requests specific claims (e.g., "Incorporate details from Claim 2"), locate the corresponding claim from the Claims section provided and integrate this information coherently into your description.
- Preservation of Non-variable Content: Do not modify, remove, or alter any part of the template that is not encased in double square brackets or double curly brackets. The integrity of the provided structure must be maintained.
- Comprehensive and Clear Descriptions: Aim for clarity and thoroughness in your descriptions. Technical details should be accessible to those familiar with the field, and explanations should be structured to facilitate understanding of the patent's scope and implementation.
- DO NOT output the Double Square Brackets and Double Curly Brackets as an output.
"""
    prompt_config = PromptTemplate(
        template=prompt_template,
        input_variables=["title", "summary", "claims", "paragraph", "banned_word_list"],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(
        {
            "title": title,
            "summary": summary,
            "claims": claims,
            "paragraph": paragraph,
            "banned_word_list": banned_word_list,
        }
    )
    return response["text"]


# Function to generate formatted claims
async def generation_of_claim_X_format(paragraph, claims):
    prompt_template = """Generate a formatted claim based on the provided claims and paragraph.
    
    Paragraph:
    {paragraph}
    
    Claims:
    {claims}
    
    INSTRUCTION FOR REFORMATTING CLAIM:
    If this pattern of claim comes up -> [[Claim X]]; where X is the claim number, it SHOULD be replaced like this:
        In an aspect, (restructure the sentence of the claim accordingly).
        E.g. If claim 9 reads: "The device of claim 7, further comprising a headset connected to the earbud”, then the response for [[Claim 9]] would be something like this: "In an aspect, the the device further includes a headset that is connected to the earbud".
    
    INSTRUCTIONS:
- DO NOT MODIFY, ALTER, OR REMOVE any part of the 'Paragraph' EXCEPT which follows the pattern of [[Claim X]] where X is a number.
- IF curly brackets come inside of the square brackets; the curly brackets will be instructions for the generation but it should STRICTLY FOLLOW the instructions which were given in 'INSTRUCTION FOR REFORMATTING CLAIM'.
     Examples: [[Claim 1{{Rewrite in past tense}}]] or [[Claim 2{{Rephrase in past tense}}]]
- DO NOT output the Double Square Brackets and Double Curly Brackets as an output.
"""
    prompt_config = PromptTemplate(
        template=prompt_template,
        input_variables=[
            "claims",
            "paragraph"
        ],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(
        {
            "claims": claims,
            "paragraph": paragraph
        }
    )
    return response["text"]


# Function to generate formatted claims
async def generation_of_claim_PCT_format(paragraph, claims):
    prompt_template = """Generate a formatted claim based on the provided claims and paragraph.

    Paragraph:
    {paragraph}

    Claims:
    {claims}

    INSTRUCTION FOR REFORMATTING CLAIM:
    If this pattern of claim comes up -> [[Claim X-PCT]]; where X would be the claim number: 
        It SHOULD just replace the word claim/claims with the word example/examples
        E.g. if claim 9 reads: "The device of claim 7, further comprising a headset connected to the earbud”, then the response for [[Claim 9-PCT]] would be: "The device of example 7, further comprising a headset connected to the earbud".


    INSTRUCTIONS:
- DO NOT MODIFY, ALTER, OR REMOVE any part of the 'Paragraph' EXCEPT which follows the pattern of [[Claim X-PCT]] where X is a number.
- IF curly brackets come inside of the square brackets; the curly brackets will be instructions for the generation but it should STRICTLY FOLLOW the instructions which were given in 'INSTRUCTION FOR REFORMATTING CLAIM'.
     Examples: [[Claim 1-PCT{{Rewrite in past tense}}]] or [[Claim 2-PCT{{Rephrase in past tense}}]]
- DO NOT output the Double Square Brackets and Double Curly Brackets as an output.
"""
    prompt_config = PromptTemplate(
        template=prompt_template,
        input_variables=[
            "claims",
            "paragraph"
        ],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(
        {
            "claims": claims,
            "paragraph": paragraph
        }
    )
    return response["text"]

# Function to generate formatted claims
async def generation_of_step_claim_format(paragraph, claims):
    prompt_template = """Generate a formatted claim based on the provided claims and paragraph.

    Paragraph:
    {paragraph}

    Claims:
    {claims}

    INSTRUCTION FOR REFORMATTING CLAIM:
    If this pattern of claim comes up -> [[Step M of Claim X]]; where M would be the step number and X would be the claim number:
        It SHOULD be replaced with the step of the claim.
        E.g. If a Claim 1 reads: "The method of claim 1, wherein: the data reduction condition is further based on information about a type of data that is not used by the target microservice, and the type of data is stored as reducible dimensions in the vertical reduction database". 
        Then the response for [[Step 2 of Claim 1]] will ONLY output: "the type of data is stored as reducible dimensions in the vertical reduction database".

    INSTRUCTIONS:
- DO NOT MODIFY, ALTER, OR REMOVE any part of the 'Paragraph' EXCEPT which follows the pattern of [[Step M of Claim X]] where M and X are numbers for each respectively.
- IF curly brackets come inside of the square brackets; the curly brackets will be instructions for the generation but it should STRICTLY FOLLOW the instructions which were given in 'INSTRUCTION FOR REFORMATTING CLAIM'.
     Examples: [[Step 1 of Claim 2{{Rewrite in past tense}}]] or [[Step 3 of Claim 5{{Rephrase in past tense}}]]
- DO NOT output the Double Square Brackets and Double Curly Brackets as an output.
"""
    prompt_config = PromptTemplate(
        template=prompt_template,
        input_variables=[
            "claims",
            "paragraph"
        ],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(
        {
            "claims": claims,
            "paragraph": paragraph
        }
    )
    return response["text"]



# Function to generate Detailed Description
async def generation_of_detailed_description(
    title, subheading, summary, claims, paragraph, banned_word_list
):
    prompt_template = """Generate the "Detailed Description" for the {subheading} section of a Patent Application, guided by the Title, Summary, Claims, and provided Paragraph.

Title: {title}

Summary:
{summary}

Claims:
{claims}

Paragraph:
{paragraph}

AVOID using the following words while generating the response:
Claim, {banned_word_list}

INSTRUCTIONS:
- Capitalize the first letter of the paragraph or of a sentence if not capitalized.
- DO NOT make more than one paragraph unless specified.
- DO NOT MODIFY, ALTER, OR REMOVE any part of the 'Paragraph' that is NOT encased in double square brackets (i.e. [[]]) or double curly brackets (i.e. {{}}).
- ONLY Focus on Generating Content Within Double Square Brackets ([[Content to be generated]]): Here, provide a detailed explanation or description that's specifically asked for within the context of the patent's technology or process.
- Instructions of content to be generated and also appear as ([[INSTRUCTIONS{{INSTRUCTIONS FOR Content to be generated}}]]): JUST FOLLOW THE INSTRUCTIONS. NEVER EVER WRITE/USE THE WORDING OF INSTRUCTIONS IN THE GENERATION/ANSWER.
- Generate Content Within Double Curly Brackets ({{INSTRUCTIONS FOR Content to be generated}}): Ensure you closely follow the instructions provided within these brackets to generate content that's both relevant and adherent to the guidelines specified. NEVER REPEAT THE WORDS/REWRITE THE INSTRUCTIONS WRITTEN IN {{ }} IN THE GENERATION/ANSWER.
- Integrate Relevant Claims: When the template requests specific claims (e.g., "Incorporate details from Claim 2"), locate the corresponding claim from the Claims section provided and integrate this information coherently into your description.
- Aim for clarity and thoroughness in your descriptions. Technical details should be accessible to those familiar with the field, and explanations should be structured to facilitate understanding of the patent's scope and implementation.
- DO NOT output the Double Square Brackets and Double Curly Brackets as an output.

EXAMPLES OF INSTRUCTIONS:
[[Detailed Description{{Described a method for operating the vertical reduction service mesh. Limit it to at most 433 words}}]]. IN this example INSTRUCTIONS ARE: 'Described a method for operating the vertical reduction service mesh. Limit it to at most 433 words'. In answer DO NOT USE/Rewrite THESE WORDS NOR the word 'Detailed Description'.
This is just one example. Look for these instructions carefully.
"""
    prompt_config = PromptTemplate(
        template=prompt_template,
        input_variables=[
            "title",
            "subheading",
            "summary",
            "claims",
            "paragraph",
            "banned_word_list",
        ],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(
        {
            "title": title,
            "subheading": subheading,
            "summary": summary,
            "claims": claims,
            "paragraph": paragraph,
            "banned_word_list": banned_word_list,
        }
    )
    return response["text"]


# Function to generate Set Scene Paragraph (Description Section)
async def gen_set_scene_desc(title, full_summary, banned_word_list):
    prompt_template = """Generate detailed description content for the Detailed Description section of the Patent Application guided by the Title and Summary.
    
Title: {title}

Summary:
{summary}

AVOID using the following words while generating the response:
Claim, {banned_word_list}

INSTRUCTIONS:
- Your response should consist of one paragraph for each of the two sections. Each paragraph should offer a clear and concise explanation of the respective section. Ensure that the description is relevant to the specified sections of the patent application and concludes with a full stop.

Here's the template:
Elaborate on the setting and context relevant to the invention "{title}" mentioned in the patent. The invention details state that "{summary}". Discuss the problems or challenges that the invention aims to address within this environment. Provide pertinent technical or practical details that help create a clear picture of the scenario in which the invention will be applied.
"""
    prompt_config = PromptTemplate(
        template=prompt_template,
        input_variables=["title", "summary", "banned_word_list"],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(
        {"title": title, "summary": full_summary, "banned_word_list": banned_word_list}
    )
    return response["text"]


# Function to generate Set Scene Paragraph (Description Section)
async def gen_desc_current_issues(title, full_summary, banned_word_list):
    prompt_template = """Generate detailed description content for the Detailed Description section of the Patent Application guided by the Title and Summary.

Title: {title}

Summary:
{summary}

AVOID using the following words while generating the response:
Claim, {banned_word_list}

INSTRUCTIONS:
- Your response should consist of one paragraph for each of the two sections. Each paragraph should offer a clear and concise explanation of the respective section. Ensure that the description is relevant to the specified sections of the patent application and concludes with a full stop.

Here's the template:
Discuss the challenges or issues faced by professionals, users, or practitioners in the relevant industry or domain. Highlight the deficiencies and drawbacks of current approaches that your invention aims to overcome. Reference the context provided earlier, where "{summary}" and "{title}" are described. Explain how the existing technologies fall short in meeting the needs or goals of practitioners in the field. Provide specific examples or scenarios that illustrate the problems in practice.
"""
    prompt_config = PromptTemplate(
        template=prompt_template,
        input_variables=["title", "summary", "banned_word_list"],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(
        {"title": title, "summary": full_summary, "banned_word_list": banned_word_list}
    )
    return response["text"]


# Function to generate Detailed Description Section
async def gen_title_paragraph(title, full_summary, banned_word_list):
    prompt_template = """Explain the components of the Patent Application and provide information guided by the Title and Summary.

Title: {title}

Summary:
{summary}

AVOID using the following words while generating the response:
Claim, {banned_word_list}

INSTRUCTIONS:
- Generate whole the whole text in a single paragraph and which DOES NOT contain any headings or bullet points.

Here's the template instruction:
Talk about the Introduction, Summarize, Components Functionality, Variations, Implementation and other list of items that we discussed that the description section can include.
"""
    prompt_config = PromptTemplate(
        template=prompt_template,
        input_variables=["title", "summary", "banned_word_list"],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(
        {"title": title, "summary": full_summary, "banned_word_list": banned_word_list}
    )
    return response["text"]


# Function to generate Component X Description
def gen_component_x_desc(title, claims, banned_word_list):
    prompt_template = """Generate detailed description content for the Detailed Description section of the Patent 
Application guided by the Title and Summary.

Title: {title}

Claims:
{claims}

AVOID using the following words while generating the response:
Claim, {banned_word_list}
    
INSTRUCTIONS:
- IF ONLY '[[Component X]]' is mentioned, just replace it with the provided Title.
- DO NO MAKE ANY HEADINGS
- DO NOT MAKE EXTRA PARAGRAPHS
- DO NOT ALTER the contents of the paragraph.
- DO NOT MAKE CHANGES TO THE TEXT EXCEPT FOR THOSE ENCLOSED IN DOUBLE SQUARE BRACKETS.
- IF ANYTHING ABOUT CLAIMS IS MENTIONED, DO THE GIVEN INSTRUCTION INSIDE THE DOUBLE SQUARE BRACKETS.
- Preservation of Non-variable Content: Do not modify, remove, or alter any part of the template that is not encased in 
double square brackets or double curly brackets. The integrity of the provided structure must be maintained.
- DO NOT output the Double Square Brackets and Double Curly Brackets as an output."""

    prompt_config = PromptTemplate(
        template=prompt_template,
        input_variables=["title", "claims", "banned_word_list"],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = chain_text.invoke(
        {"title": title, "claims": claims, "banned_word_list": banned_word_list}
    )["text"]
    return response


# Function to generate Figures Description
async def gen_figures_description(
    user_prompt, title, claims, patent_summary, banned_word_list, base64_image
):
    image_llm = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"), organization=os.getenv("OPENAI_ORG_KEY")
    )
    response = await image_llm.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": """You are a professional Patent Application Image Describer. You are 
                                      helping me describe an figure/diagram/schematic for a patent application based on the title,
                                      claims, summary and a user based prompt. I have uploaded an image and have provided
                                      a title, a list of claims, and a summary of the application. Use this information to 
                                      craft a detailed description of the image that aligns with these 
                                      elements of the patent application. 

                                      INSTRUCTIONS:
                                      - HARD WORD LIMIT is 2000 words.
                                      - DO NOT output anything enclosed in asterisks
                                      - KEEP the formatting proper i.e. a newline for each paragraph or after a point.
                                      - User based prompt will tell a bit about the figure/diagram/schematic.
                                      - DO NOT include the words in the description present in Profanity List.
                                      - Generate the response such that I am writing it for a patent application.
                                      - The description should be DETAILED and ACCURATE.""",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"User Prompt: {user_prompt}"},
                    {"type": "text", "text": f"Title: {title}"},
                    {"type": "text", "text": f"Claims: {claims}"},
                    {"type": "text", "text": f"Summary: {patent_summary}"},
                    {"type": "text", "text": f"Profanity List: Claim, {banned_word_list}"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
        max_tokens=300,
    )
    description = response.choices[0].message.content
    return description


# Function to generate Abstract
async def generation_of_abstract(title, claims, summary, banned_word_list):
    prompt_template = """Generate an Abstract section for a Patent Application based on the documents provided.

Here's the Title of the Patent Application:

{title}

Here's the Claims of the Patent Application:

{claims}

Here's the Summary of the Patent Application:

{summary}

AVOID using the following words while generating the response:
Claim, {banned_word_list}

INSTRUCTIONS:
- DO NOT use the heading 'ABSTRACT'.
- DO NOT mention things like 'This article' or similar phrases.
- It should be written like an Abstract of a Patent Application, and should be approximately 150 words long.
- KEEP the abstract concise and to the point.
- The Abstract should relate to the provided Summary, Claims and Title.
- A simplified explanation of Independent Claim 1, aiming for a total of less than 150 words.
- Replace references to speakers in transcripts with "We/Ours" pronouns.
- Highlight an apparatus equipped with the 'inventive_component' for executing the method.
- Include a mention of a computer-readable storage medium that facilitates method execution.
"""
    prompt_config = PromptTemplate(
        template=prompt_template,
        input_variables=["title", "summary", "claims", "banned_word_list"],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)

    response = await chain_text.ainvoke(
        {
            "title": title,
            "summary": summary,
            "claims": claims,
            "banned_word_list": banned_word_list,
        }
    )
    return response["text"]


# Function to generate Claims
async def generation_of_claims(generated_title, summary_text):
    prompt_generated_claims = """Generate a Claims Section for an Invention with the material provided below:
    
     Title: {generated_title} 
     
     Summary of the Patent Files: 
     {summary_text}
     
INSTRUCTIONS:
- DO NOT include the heading/title 'Claim' or 'Claims' in the response.
- Describe techniques and apparatuses for {generated_title}.
- Discuss a method performed by the 'Inventive Component' for {generated_title}.
- Mention an apparatus with a 'Inventive Component' for method execution.
- Note a computer-readable storage medium for method execution.
- Describe a system with means for performing '{generated_title}'.
- Make a numbered list separated by a new line for each claim.
- A claim may involve Optional Elements.
- The claims should encompass variations in Specific Variations or Aspects, as required by the invention's scope.
"""
    prompt_config = PromptTemplate(
        template=prompt_generated_claims,
        input_variables=["summary_text", "generated_title"],
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(
        {"summary_text": summary_text, "generated_title": generated_title}
    )
    return response["text"]


# Function to rephrase a text
async def rephrase_text(text):
    prompt_template = """You are a Professional Text Repharser whose job is to critically analyze inputs and to Repharse the piece of text. You have been provided a text below:

{text}

Your job is to just rephrase the generated text while preserving the original format and headings, without adding any extra information or messages.

THINGS YOU MUST FOLLOW AT ALL TIMES:
- PRESERVE THE ORGINAL FORMAT AND HEADINGS.
- DO NOT ADD ANY EXTRA INFORMATION OR MESSAGES.
- JUST REPHARSE THE TEXT.
"""
    prompt_config = PromptTemplate(template=prompt_template, input_variables=["text"])
    chain_text = LLMChain(llm=llm, prompt=prompt_config)

    response = await chain_text.ainvoke(text)
    return response["text"]


# Function to revise a text
async def custom_prompt(text, revision):
    prompt_template = """
You are a Professional Text Reviser whose job is to critically analyze inputs and to Revise the piece of text based on the instruction provided below. You have been provided a text below:

{text}

I want you to make a revision in the given, based on below instruction:

{revision}

THINGS YOU MUST FOLLOW AT ALL TIMES:
- YOUR OUTPUT SHOULD BE THE FULL UNCHANGED INPUT TEXT, WITH THE CHANGES MADE AS PER THE REVISION IN THE PROMPT. KEEPING EVERYTHING ELSE THE SAME AND UNTOUCHED, ONLY ON REWRITING THE PART MENTIONED IN THE REVISION.
- CHANGE THE SPECIFIC AND TARGETED PORTION OF THE CONTENT ONLY WHEN THE REVSION INSTRUCTION ASK YOU TO DO SO.
- WHEN A CONTENT IS TO BE ADDED, JUST ADD THE CONTENT MENTIONED IN THE REVISION INSTRUCTION. DO NOT ALTER THE REMAINING CONTENT.
- WHEN A CONTENT IS TO BE ALTERED, ALTER THE SPECIFIC AND TARGETED CONTENT WHICH IS MENTIONED IN THE REVISION INSTRUCTION. DO NOT ALTER THE REMAINING CONTENT.
- WHEN A CONTENT IS TO BE REMOVED, ONLY REMOVE THE SPECIFIC AND TARGETED CONTENT WHICH IS MENTIONED IN THE REVISION INSTRUCTION. DO NOT ALTER THE REMAINING CONTENT.
"""
    prompt_config = PromptTemplate(
        template=prompt_template, input_variables=["text", "revision"]
    )

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke({"text": text, "revision": revision})
    return response["text"]


# Function to summarize text
async def summarize_text(text):
    prompt_template = """You are a Professional Text Summarizer whose job is to critically analyze inputs and to Summarize the piece of text which has been provided below:

{text}

I want you to make a condensed summary of the given text while preserving the original format and headings, without adding any extra information or messages.

THINGS YOU MUST FOLLOW AT ALL TIMES:
- PRESERVE THE ORIGINAL FORMAT AND HEADINGS.
- DO NOT ADD ANY EXTRA INFORMATION OR MESSAGES.
- JUST SUMMARIZE THE TEXT.
"""
    prompt_config = PromptTemplate(template=prompt_template, input_variables=["text"])

    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(text)
    return response["text"]


# Function to generate a word definition
async def generate_word_def(word):
    prompt_template = """You are a Professional in DEFINING WORDS whose job is to ONLY provide a precise, concise of the words which has been provided below:
{word}
THINGS YOU MUST FOLLOW AT ALL TIMES:
- AVOID adding any extra information, examples, or descriptions that are not strictly part of the word's definition.
- DO NOT ADD ANY EXTRA INFORMATION OR MESSAGES.
- JUST DEFINE THE WORD.
- Define the word in layman terms such that it can be added to a sentence while maintaing a flow to it.
"""
    prompt_config = PromptTemplate(template=prompt_template, input_variables=["word"])
    chain_text = LLMChain(llm=llm, prompt=prompt_config)
    response = await chain_text.ainvoke(word)
    return response["text"]
