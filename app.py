import streamlit as st
from sqlbot import *

# Set favicon
st.set_page_config(page_title="SQLGPT App", page_icon="static/res/favicon.png")

st.title("SQLGPT👩‍💻📑❔")
st.subheader('A Smart helper to get your answers quickly🚀')

# User input
question_input = st.text_input("Question:")

if question_input:
    # Extract keywords from the question input
    response = generate(question_input)

    st.text_area("Answer:", response)
