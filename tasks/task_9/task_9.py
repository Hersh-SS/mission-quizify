import streamlit as st
import os
import sys
import json
sys.path.append(os.path.abspath('../../'))
from tasks.task_3.task_3 import DocumentProcessor
from tasks.task_4.task_4 import EmbeddingClient
from tasks.task_5.task_5 import ChromaCollectionCreator
from tasks.task_8.task_8 import QuizGenerator

class QuizManager:
    def __init__(self, questions: list):
        """
        Initializes the QuizManager class with a list of quiz questions.
        """
        self.questions = questions
        self.total_questions = len(questions)
    
    def get_question_at_index(self, index: int):
        """
        Retrieves the quiz question object at the specified index. If the index is out of bounds,
        it restarts from the beginning index.
        """
        valid_index = index % self.total_questions
        return self.questions[valid_index]

    def next_question_index(self, direction=1):
        """
        Adjusts the current quiz question index based on the specified direction.
        """
        current_index = st.session_state.get("question_index", 0)
        new_index = (current_index + direction) % self.total_questions
        st.session_state["question_index"] = new_index

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
        st.session_state.question_bank = None
        st.session_state.question_index = 0

    screen = st.empty()  # Screen 1, ingest documents

    if not st.session_state.submitted:
        with screen.container():
            st.header("Quiz Builder")
            
            # Initialize the ChromaCollectionCreator from Task 5
            from tasks.task_3.task_3 import DocumentProcessor
            from tasks.task_4.task_4 import EmbeddingClient
            from tasks.task_5.task_5 import ChromaCollectionCreator

            processor = DocumentProcessor()
            processor.ingest_documents()
    
            embed_client = EmbeddingClient(**embed_config) # Initialize from Task 4
    
            chroma_creator = ChromaCollectionCreator(processor, embed_client)

            with st.form("Load Data to Chroma"):
                st.subheader("Quiz Builder")
                st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")

                # Use streamlit widgets to capture the user's input for the quiz topic and the desired number of questions
                topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
                num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)
                
                submitted = st.form_submit_button("Submit")
                if submitted:
                    chroma_creator.create_chroma_collection()
                    
                    generator = QuizGenerator(topic_input, num_questions, chroma_creator)
                    question_bank = generator.generate_quiz()
                    
                    st.session_state.submitted = True
                    st.session_state.question_bank = question_bank

                    st.rerun()

    if st.session_state.submitted and st.session_state.question_bank is not None:
        screen.empty()  # Clear the initial screen
        with screen.container():
            st.header("Generated Quiz Questions:")

            quiz_manager = QuizManager(st.session_state.question_bank)
            current_index = st.session_state.get("question_index", 0)
            index_question = quiz_manager.get_question_at_index(current_index)

            # Unpack choices for radio
            choices = [f"{choice['key']}) {choice['value']}" for choice in index_question['choices']]

            with st.form("Multiple Choice Question"):
                st.write(index_question['question'])
                answer = st.radio('Choose the correct answer', choices)
                submitted = st.form_submit_button("Submit")
                
                if submitted:
                    correct_answer_key = index_question['answer']
                    if answer.startswith(correct_answer_key):
                        st.success("Correct!")
                    else:
                        st.error("Incorrect!")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Previous"):
                    quiz_manager.next_question_index(direction=-1)
                    st.rerun()
            with col3:
                if st.button("Next"):
                    quiz_manager.next_question_index(direction=1)
                    st.rerun()
    elif st.session_state.submitted and st.session_state.question_bank is None:
        screen.empty()  # Clear the initial screen
        with screen.container():
            st.header("Generated Quiz Questions:")
            st.write("No quiz questions generated.")

if __name__ == "__main__":
    main()
