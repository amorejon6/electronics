from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from lxml import etree

import os
import json
import tiktoken

MAX_TOKENS = 270000
TOKEN_CHAR_ESTIMATE = 2

def extract_input(file_xml):
    tree = etree.parse(file_xml)
    root = tree.getroot()

    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    text_element = root.find('.//tei:text', namespaces=ns)
    if text_element is None:
        print("The <text> tag was not found in the file.")
        return

    content_xml = etree.tostring(text_element, pretty_print=True, encoding='unicode')

    return content_xml

def split_text_into_chunks(text, max_chars=MAX_TOKENS*TOKEN_CHAR_ESTIMATE):
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + max_chars, length)
        chunks.append(text[start:end])
        start = end
    return chunks

def generate_metadata(file_path, prompts_path, api_key):
    with open(prompts_path / 'prompt_metadata_v4.txt', 'r') as file:
        template = file.read()

    prompt = PromptTemplate(
        input_variables=["xml_novel"],
        template=template
    )

    model = ChatOpenAI(
                model="gpt-5-mini",
                temperature=0,
                # openai_api_base=os.environ.get("OPENAI_API_BASE", "http://localhost:8000/v1"),
                openai_api_key=os.environ.get("OPENAI_API_KEY", api_key),
            )

    xml_novel = extract_input(file_path)

    encoder = tiktoken.get_encoding("cl100k_base")

    tokens = encoder.encode(xml_novel)

    json_data = "{}"

    if len(tokens) <= MAX_TOKENS:
        prompt_text = prompt.format_prompt(xml_novel=xml_novel).to_string()
        human_message = HumanMessage(content=prompt_text)

        try:
            response = model.invoke([human_message])
            json_data = response.content
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            # print(type(e))
    else:
        # Divide in chunks and process each chunk separately
        print(f"File {file_path} exceeds the maximum token limit of {MAX_TOKENS} tokens.")
        chunks = split_text_into_chunks(xml_novel)
        all_responses = []
        for i, chunk in enumerate(chunks):
            prompt_text = prompt.format_prompt(xml_novel=chunk).to_string()
            human_message = HumanMessage(content=prompt_text)
            try:
                response = model.invoke([human_message])
            except Exception as e:
                print(f"Error processing chunk {i} of {file_path}: {e}")
                continue
            all_responses.append(response.content)

        # Combine all JSON responses into one
        with open(prompts_path / 'prompt_combination.txt', 'r') as file:
            template_combination = file.read()

        prompt_combination = PromptTemplate(
            input_variables=["jsons_partial"],
            template=template_combination
        )
        jsons_partial_text = "\n".join(all_responses)
        prompt_combination_text = prompt_combination.format_prompt(jsons_partial=jsons_partial_text).to_string()
        human_message = HumanMessage(content=prompt_combination_text)
        try:
            combined_response = model.invoke([human_message])
            json_data = combined_response.content
        except Exception as e:
            print(f"Error generating combined JSON: {e}")

    return json.loads(json_data)

if __name__ == "__main__":
    print(generate_metadata("ENG18400_Trollope.xml"))