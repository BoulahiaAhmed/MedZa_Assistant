from duckduckgo_search import DDGS
import google.generativeai as genai
from dotenv import load_dotenv

import streamlit as st
import os

# Everything is accessible via the st.secrets dict:
st.write("Gemini API Key:", st.secrets["GOOGLE_API_KEY"])

# And the root-level secrets are also accessible as environment variables:
st.write(
    "Has environment variables been set:",
    os.environ["GOOGLE_API_KEY"] == st.secrets["GOOGLE_API_KEY"],
)


load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')  


def DDGS_RAG(query, max_results=2):
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, safesearch='on', timelimit='y', max_results=max_results)]

    snippets = []
    for result in results:
        title = result['title']
        body = result['body']
        link = result['href']
        snippet = {'title': title, 'body': body, 'link': link}
        snippets.append(snippet)

    return snippets


def Gemini_generation(request, context):
    prompt = f"""Your main task is to respond to the request using the context provided.
    The context is indicated with the tag 'context' and the request is indicated with
    the tag 'request'.
    If the context doesn't have relevant information about the request, or if
    the request is a basic and very simple one, you can then respond using your own
    knowledge.
    Here's some examples of a basic request: 'hello', 'whats 1+1?', 'who are you?'
    If the knowledge you have contradicts the context provided. Then use the context
    information.

    Context:{context}
    Request:{request}
    """
    response = model.generate_content(prompt,
                                        generation_config=genai.types.GenerationConfig(
                                        candidate_count=1,
                                        max_output_tokens=500,
                                        temperature=0.1))
    return response


def Gemini_digest(list_of_context, list_of_titles):
    prompt = f""" Your task is to generate a text summary based on the provided data.
    To complete this task successfully you need to follow these steps:

    1- Generate separate summaries for each text in the provided list indicated with the tag 'list_of_context'.
    2- Understand the context of each summary and generate separate summaries.
    3- The final summary must be in bullet points, add a title for each bullet point, titles must be from the provided list indicated with the tag 'list_of_titles'.
    4- Generate a good title for this complete and unified summary.

    make sure the output is clear and easy to read.

    list_of_context: {list_of_context}.
    list_of_titles: {list_of_titles}.
    """
    response = model.generate_content(prompt,
                                        generation_config=genai.types.GenerationConfig(
                                        candidate_count=1,
                                        max_output_tokens=500,
                                        temperature=0.2))
    return response


def Chatbot(query):
    # Call DDGS_RAG function to retrieve the data
    source_data = DDGS_RAG(query)
    answers=[]
    links=[]
    titles=[]
    ref=[]

    # Loop on the retrieved data and generate responses with Gemini_generation function
    for data in source_data:
        response = Gemini_generation(query, data['body'])
        answers.append(response.text)
        links.append(data['link'])
        titles.append(data['title'])

    # Reference creation (titles, link)
    for i in range(len(links)):
        ref.append(titles[i]+".  \nLink: "+links[i])

    # Call the Gemini_digest function to return the final answer
    summary = Gemini_digest(answers, titles)
    ref_string = "\n\n".join(ref)
    digest = f"""{summary.text}\n\nReferences:\n\n  {ref_string}"""
    return digest
