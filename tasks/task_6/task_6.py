import sys
import os
import streamlit as st
import tempfile
import uuid
sys.path.append(os.path.abspath('../../'))
from tasks.task_3.task_3 import DocumentProcessor
from tasks.task_4.task_4 import EmbeddingClient
from tasks.task_5.task_5 import ChromaCollectionCreator

def main():
    st.header("Quizify")

    # Configuration for EmbeddingClient
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "gemini-quizify-426119",
        "location": "us-central1"
    }

    if "submitted" not in st.session_state:
        st.session_state.submitted = False
        st.session_state.document = None

    screen = st.empty()  # Screen 1, ingest documents

    if not st.session_state.submitted:
        with screen.container():
            
            # 1) Initialize DocumentProcessor and Ingest Documents from Task 3
            processor = DocumentProcessor()
            processor.ingest_documents()

            # 2) Initialize the EmbeddingClient from Task 4 with embed config
            embed_client = EmbeddingClient(**embed_config)

            # 3) Initialize the ChromaCollectionCreator from Task 5
            chroma_creator = ChromaCollectionCreator(processor, embed_client)

            with st.form("Load Data to Chroma"):
                st.subheader("Quiz Builder")
                st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")

                # 4) Use streamlit widgets to capture the user's input for the quiz topic and the desired number of questions
                topic_input = st.text_input("Topic for Generative Quiz")
                num_questions = st.slider("Number of Questions", min_value=1, max_value=20, value=5)

                submitted = st.form_submit_button("Generate a Quiz!")
                if submitted:
                    st.session_state.submitted = True
                    st.session_state.topic_input = topic_input
                    st.session_state.num_questions = num_questions

                    # 5) Use the create_chroma_collection() method to create a Chroma collection from the processed documents
                    chroma_creator.create_chroma_collection()
                    document = chroma_creator.query_chroma_collection(topic_input)
                    st.session_state.document = document

                    # Switch to the second screen
                    st.experimental_rerun()

    if st.session_state.submitted and st.session_state.document is not None:
        screen.empty()  # Clear the initial screen
        with screen.container():
            st.header("Query Chroma for Topic, top Document: ")
            st.write(st.session_state.document)
    elif st.session_state.submitted and st.session_state.document is None:
        screen.empty()  # Clear the initial screen
        with screen.container():
            st.header("Query Chroma for Topic, top Document: ")
            st.write("No documents found.")

if __name__ == "__main__":
    main()
