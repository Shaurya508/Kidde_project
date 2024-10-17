import streamlit as st
import pandas as pd
# from memory import user_input
from ollama123 import user_input4
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import requests
import re
# from trial import translate
from Levenshtein import distance as levenshtein_distance
import os
from OpenAI_Clip import retrieve_best_image
# Define the maximum number of free queries
QUERY_LIMIT = 100

# Initialize session state for tracking the number of queries, conversation history, suggested questions, and authentication
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'suggested_question' not in st.session_state:
    st.session_state.suggested_question = ""

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'generate_response' not in st.session_state:
    st.session_state.generate_response = False

if 'chat' not in st.session_state:
    st.session_state.chat = ""


def clean_text(text):
    # Remove asterisks used for bold formatting
    text = re.sub(r'\*+', '', text)
    # Remove text starting from "For more details"
    text = re.sub(r'For more details.*$', '', text, flags=re.IGNORECASE)
    return text


def get_image_link(article_link, file_path='Article_Links.xlsx'):
    # Load the Excel file
    df = pd.read_excel(file_path)

    # Ensure the columns are named correctly
    df.columns = ['Article Link', 'Image link']

    # Create a dictionary mapping article links to image links
    link_mapping = dict(zip(df['Article Link'], df['Image link']))

    # Find the most similar article link using Levenshtein distance
    most_similar_link = min(df['Article Link'], key=lambda x: levenshtein_distance(x, article_link))
    image_link = link_mapping.get(most_similar_link, "Image link not found")
    
    if image_link == "Image link not found" or image_link == 0:
        return None
    return image_link

def authenticate_user(email):
    # Load the Excel file
    df = pd.read_excel('user.xlsx')
    # Convert the input email to lowercase
    email = email.lower()
    # Convert the emails in the dataframe to lowercase
    df['Email'] = df['Email'].str.lower()
    # Check if the email matches any entry in the file
    user = df[df['Email'] == email]
    if not user.empty:
        return True
    return False

def create_ui():
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    footer:after {content:''; display:block; position:relative; top:2px; color: transparent; background-color: transparent;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stActionButton {display: none !important;}
    ::-webkit-scrollbar {
        width: 12px;  /* Keep the width of the scrollbar */
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    ::-webkit-scrollbar-thumb {
        background: #888;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    .scroll-icon {
        position: fixed;
        bottom: 40px;  /* Adjusted the position upwards */
        right: 150px;
        font-size: 32px;
        cursor: pointer;
        color: #0adbfc;
        z-index: 1000;
    }
    </style>
    <script>
    function scrollToBottom() {
        window.scrollTo(0, 50000);
    }
    </script>
    """

    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # st.markdown("<h2 style='text-align: center; color: #0adbfc;'><u>Aryma Labs - MMMGPT(Mini)</u></h2>", unsafe_allow_html=True)
    # Create columns for title and logo
    st.markdown("<h2 style='text-align: center; color: #0adbfc;'><u>Aryma Labs - MMMGPT(Mini)</u></h2>", unsafe_allow_html=True)
    st.image('Client_logo.png', width=50)
    st.sidebar.image("Aryma Labs Logo.jpeg")
    st.sidebar.markdown("<h2 style='color: #08daff;'>Welcome to Aryma Labs</h2>", unsafe_allow_html=True)
    st.sidebar.write("Ask anything about your MMM project and get accurate insights.")

    if not st.session_state.authenticated:
        st.markdown("<h3 style='color: #4682B4;'>Login</h3>", unsafe_allow_html=True)
        with st.form(key='login_form'):
            email = st.text_input("Email")
            login_button = st.form_submit_button(label='Login')

            if login_button:
                if authenticate_user(email):
                    st.session_state.authenticated = True
                    st.experimental_rerun()
                else:
                    st.error("Invalid email or password. Please try again.")
        return

    # Display the conversation history in reverse order to resemble a chat interface
    chat_container = st.container()
    with chat_container:
        if st.session_state.conversation_history == []:
            col1, col2 = st.columns([1, 8])
            with col1:
                st.image('download.png', width=30)
            with col2:
                st.write("Hello, I am MMMGPT(mini) from Aryma Labs. How can I help you?")
                
    for idx, (q, r, suggested_questions,language) in enumerate(st.session_state.conversation_history):
        st.markdown(f"<p style='text-align: right; color: #484f4f;'><b>{q}</b></p>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 8])
        r1 = r
        with col1:
            st.image('download.png', width=30)
        with col2:
            st.write(r)
            image_path = retrieve_best_image(q)
            # st.write(f"Image path: {image_path}")

            print(image_path)
            if(image_path != None):
                if os.path.exists(image_path):
                    image = Image.open(image_path)
                    st.image(image, use_column_width=True)
                else:
                    print(f"Image not found at {image_path}")
            
            # LANGUAGES = {
            #     'Arabic': 'ar', 'Azerbaijani': 'az', 'Catalan': 'ca', 'Chinese': 'zh', 'Czech': 'cs',
            #     'Danish': 'da', 'Dutch': 'nl', 'English': 'en', 'Esperanto': 'eo', 'Finnish': 'fi',
            #     'French': 'fr', 'German': 'de', 'Greek': 'el', 'Hebrew': 'he', 'Hindi': 'hi',
            #     'Hungarian': 'hu', 'Indonesian': 'id', 'Irish': 'ga', 'Italian': 'it', 'Japanese': 'ja',
            #     'Korean': 'ko', 'Persian': 'fa', 'Polish': 'pl', 'Portuguese': 'pt', 'Russian': 'ru',
            #     'Slovak': 'sk', 'Spanish': 'es', 'Swedish': 'sv', 'Turkish': 'tr', 'Ukrainian': 'uk',
            #     'Bengali': 'bn'
            # }
            # # st.write(r)
            # if(language != "en"):
            #     r = translate(clean_text(r) , "en" , language)
            #     st.write(r + "\n")
            # else:
            #     st.write(clean_text(r1) + "\n")
        
                # print(image_path)
            # if(image_path != None):
            #     if os.path.exists(image_path):
            #         image = Image.open(image_path)
            #         st.image(image, use_column_width=True)
            #     else:
            #         print(f"Image not found at {image_path}")
            # # Language selection
            # target_language = st.selectbox(
            #     'Select target language', options=list(LANGUAGES.keys()), key=f'target_language_{idx}'
            # )

            # if st.button('Translate', key=f'translate_button_{idx}'):
    
            #     if target_language:
            #         # Translation
            #         if(target_language == "English"):
            #             st.write(r1)
            #             # st.write("For more details, please visit : " + post_link)
            #         else:
            #             if(language != LANGUAGES[target_language]):
            #                 # print(language + "\n" + LANGUAGES[target_language])
            #                 translated_text = translate(clean_text(r1), from_lang= "en" , to_lang=LANGUAGES[target_language])
            #             else:
            #                 translated_text = clean_text(r)
            #             st.write(translated_text)


    st.markdown("---")
    instr = "Ask a question:"
    with st.form(key='input_form', clear_on_submit=True):
        col1, col2 = st.columns([8, 1])
        with col1:
            if st.session_state.suggested_question:
                question = st.text_input(instr, value=st.session_state.suggested_question, key="input_question", label_visibility='collapsed')
            else:
                question = st.text_input(instr, key="input_question", placeholder=instr, label_visibility='collapsed')
        with col2:
            submit_button = st.form_submit_button(label='Chat')
        # st.image('Client_logo.png')
        if submit_button and question:
            st.session_state.generate_response = True
    
    if st.session_state.generate_response and question:
        if st.session_state.query_count >= QUERY_LIMIT:
            st.warning("You have reached the limit of free queries. Please consider our pricing options for further use.")
        else:
            with st.spinner("Generating response..."):
                response, docs , suggested_questions , language = user_input4(question)
                output_text = response.get('output_text', 'No response')  # Extract the 'output_text' from the response
                st.session_state.chat += str(output_text)
                st.session_state.conversation_history.append((question, output_text ,suggested_questions, language))
                st.session_state.suggested_question = ""  # Reset the suggested question after submission
                st.session_state.query_count += 1  # Increment the query count
                st.session_state.generate_response = False
                st.experimental_rerun()

    # Scroll to bottom icon
    st.markdown("""
        <div class="scroll-icon" onclick="scrollToBottom()">⬇️</div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #A9A9A9;'>Powered by: Aryma Labs</p>", unsafe_allow_html=True)

# Main function to run the app
def main():
    create_ui()

if __name__ == "__main__":
    main()
