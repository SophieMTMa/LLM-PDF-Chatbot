# An example LLM chatbot using Cohere API and Streamlit that references a PDF
# Adapted from the StreamLit OpenAI Chatbot example - https://github.com/streamlit/llm-examples/blob/main/Chatbot.py

import streamlit as st
import cohere
import fitz # An alias for PyMuPDF
from PIL import Image
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import csv
import os

# Change: reading csv file 
csv_path = 'docs/amazon.csv'
# Handle PDF or CSV 
def documents_from_file(file_path):

    ext = os.path.splitext(file_path)[1]

    if ext == '.pdf':  
        return pdf_to_documents(file_path) 
    elif ext == '.csv':
        return csv_to_documents(file_path)
 
# New CSV function   
def csv_to_documents(csv_path):

  documents = []

  with open(csv_path) as f:
    reader = csv.DictReader(f)

    for row in reader:

      document_old = {
        "product_id": row["product_id"],
        "product_name": row["product_name"],
        "category": row["category"],
        "discounted_price": row["discounted_price"],
        "actual_price": row["actual_price"],
        "discount_percentage": row["discount_percentage"], 
        "rating": row["rating"],
        "rating_count": row["rating_count"],
        "about_product": row["about_product"],
        "user_id": row["user_id"],
        "user_name": row["user_name"],
        "review_id": row["review_id"],
        "review_title": row["review_title"],
        "review_content": row["review_content"],
        "img_link": row["img_link"],
        "product_link": row["product_link"],
      }

    document = {
        "title": row["product_name"], "text": f'category: {row["category"]}, actual_price: {row["actual_price"]}, rating: {row["rating"]},  about_product: {row["about_product"]}, img_link: {row["img_link"]}, product_link: {row["product_link"]}'
      }
    
    documents.append(document)
      
  return documents

# Orginal from gnolan's github (forked)
def pdf_to_documents(pdf_path):
    """
    Converts a PDF to a list of 'documents' which are chunks of a larger document that can be easily searched 
    and processed by the Cohere LLM. Each 'document' chunk is a dictionary with a 'title' and 'snippet' key
    
    Args:
        pdf_path (str): The path to the PDF file.
    
    Returns:
        list: A list of dictionaries representing the documents. Each dictionary has a 'title' and 'snippet' key.
        Example return value: [{"title": "Page 1 Section 1", "snippet": "Text snippet..."}, ...]
    """

# Orginal from gnolan's github (forked)
    doc = fitz.open(pdf_path)
    documents = []
    text = ""
    chunk_size = 1000
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        part_num = 1
        for i in range(0, len(text), chunk_size):
            documents.append({"title": f"Page {page_num + 1} Part {part_num}", "snippet": text[i:i + chunk_size]})
            part_num += 1
    return documents


# Isolate the required columns
# df_subset = df[['product_name', 'actual_price', 'rating']]

# Convert review numbers to star emojis
# star_emojis = {
#     1: '⭐',
#     2: '⭐⭐',
#     3: '⭐⭐⭐',
#     4: '⭐⭐⭐⭐',
#     5: '⭐⭐⭐⭐⭐'
# }

# df_subset['Review'] = df_subset['Review'].map(star_emojis)


# Check if a valid Cohere API key is found in the .streamlit/secrets.toml file
# Learn more about Streamlit secrets here - https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
# Orginal from gnolan's github (forked)
api_key_found = False
if hasattr(st, "secrets"):
    if "COHERE_API_KEY" in st.secrets.keys():
        if st.secrets["COHERE_API_KEY"] not in ["", "PASTE YOUR API KEY HERE"]:
            api_key_found = True

# Add a sidebar to the Streamlit app
with st.sidebar:
    if api_key_found:
        cohere_api_key = st.secrets["COHERE_API_KEY"]
        st.write("API key found.")
    else:
        cohere_api_key = st.text_input("Cohere API Key", key="chatbot_api_key", type="password")
        st.markdown("[Get a Cohere API Key](https://dashboard.cohere.ai/api-keys)")
    
    # my_documents = []
    # selected_doc = st.selectbox("Occasion", ["Birthday", "Father's Day", "Mother's Day", "Anniversary", "Valentines", "Celebratory"])
    # if selected_doc == "Birthday Presents":
        # my_documents = pdf_to_documents('docs/GOTY-shortlist-2024-interactive.pdf')
    # elif selected_doc == "Valentines":    
        # my_documents = pdf_to_documents('WishList.pdf')
    # else:
        # my_documents = pdf_to_documents('docs/GOTY-shortlist-2024-interactive.pdf')

# Change: added selectboxes and slider for users to select appropriate criteria that influences the bot's response
    age = st.selectbox( "Age",
       ['0-1', '1-2', '3-4', '5-7', '8-9', '10-12', '13-15', '16-17', '18-30', '31-40', '41-55', '56-64', '65-75', '75+'])

    gender = st.selectbox( "Gender",
        ("Female", "Male", "Either", "Couple"), placeholder="Select Gender")
    
    # personality = st.multiselect(
    # "What are your favorite colors",
    # ["Green", "Yellow", "Red", "Blue"],
    # ["Yellow", "Red"])

    # st.write("You selected:", personality)

    personality = st.multiselect(
    "Personality",
    ["Sporty/Fit", "Creative/Arty", "Nature Lover", "Lively/Bubbly", "Fashionable", "Gadget Lover", "Hobbyist", "DIY Enthusiast", "Intellectual","Adventurous", "Hippy/Spiritual", "Indoor Type", "Outdoor Type"],
    ["Creative/Arty"])
    
    # st.write("You selected:", personality)

    # personality = st.selectbox( "Personality", 
        # ("Sporty/Fit", "Creative/Arty", "Nature Lover", "Lively/Bubbly", "Fashionable", "Gadget Lover", "Hobbyist", "DIY Enthusiast", "Intellectual", "Adventurous", "Hippy/Spiritual", "Indoor Type", "Outdoor Type"), placeholder = "Select Personality")

    price_range = st.slider(
    "Select the price range in USD",
    0.0, 300.0, (25.0, 75.0))

#my_documents = []
    # selected_doc = st.selectbox("Select your departure location", ["Tai Tam Middle School", "Repulse Bay"])
    # if selected_doc == "Tai Tam Bus Schedule":
        # my_documents = pdf_to_documents('docs/HKISTaiTamBusSchedule.pdf')
    # elif selected_doc == "Repulse Bay Bus Schedule":    
        # my_documents = pdf_to_documents('docs/HKISRepulseBayBusSchedule.pdf')
    # else:
        # my_documents = pdf_to_documents('docs/HKISTaiTamBusSchedule.pdf') 

        # GOTY-shortlist-2024-interactive.pdf

    # st.write(f"Selected document: {selected_doc}")

# Change: Set the icon image of the app
image_path = "docs/GiftGenie_icon.png"
image = Image.open(image_path)
image = image.resize((75,75))
st.image(image)

# Change: Set the title of the Streamlit app and incorporate image
st.title("Gift Genie")

# Orginal from gnolan's github (forked)
# Initialize the chat history with a greeting message
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "text": "Hi! I'm the Gift Genie. Select the age, gender, personality of your intended gift recipent along with the price range from the dropdown then ask me for suggestions. I'll do my best to find gifts that would be suitable for your intended gift recipent!!"}]

# Display the chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["text"])

# Get user input
if prompt := st.chat_input():
    # Stop responding if the user has not added the Cohere API key
    if not cohere_api_key:
        st.info("Please add your Cohere API key to continue.")
        st.stop()

    # Create a connection to the Cohere API
    client = cohere.Client(api_key=cohere_api_key)
    
    # Display the user message in the chat window
    st.chat_message("user").write(prompt)

# Change: Better guide for a better response. 
    preamble = f"""You are the Gift Genie. You help people decide what gifts to give their loved ones.
    Be concise with your response and provide the best possible answer. 
    The user's intended gift recipient is {age} years old, and a {gender}. They are {personality}. 
    The user needs you to provide gift suggestions based on above criteria, which are within {price_range} USD. 
    Respond with the most suitable gifts, product name that fit the criteria, the price and the review number out of 5.
    Group the gifts you recommend by price range, from low price to high price. 
    """

# Orginal from gnolan's github (forked)
    # Send the user message and pdf text to the model and capture the response
    response = client.chat(chat_history=st.session_state.messages,
                           message=prompt,
                           documents=documents_from_file(csv_path),
                           prompt_truncation='AUTO',
                           preamble=preamble)
    
    # Add the user prompt to the chat history
    st.session_state.messages.append({"role": "user", "text": prompt})
    
    # Add the response to the chat history
    msg = response.text
    st.session_state.messages.append({"role": "assistant", "text": msg})

    # Write the response to the chat window
    st.chat_message("assistant").write(msg)