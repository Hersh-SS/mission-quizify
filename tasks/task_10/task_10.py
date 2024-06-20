import streamlit as st
import os
import sys
import json
sys.path.append(os.path.abspath('../../'))
from tasks.task_3.task_3 import DocumentProcessor
from tasks.task_4.task_4 import EmbeddingClient
from tasks.task_5.task_5 import ChromaCollectionCreator
from tasks.task_8.task_8 import QuizGenerator
from tasks.task_9.task_9 import QuizManager

if __name__ == "__main__":
    
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "gemini-quizify-426119",
        "location": "us-central1"
    }
    
    # Add Session State
    if 'question_bank' not in st.session_state or len(st.session_state['question_bank']) == 0:
        
        # Step 1: init the question bank list in st.session_state
        st.session_state['question_bank'] = []
    
        screen = st.empty()
        with screen.container():
            st.header("Quiz Builder")
            
            # Create a new st.form flow control for Data Ingestion
            with st.form("Load Data to Chroma"):
                st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")
                
                processor = DocumentProcessor()
                processor.ingest_documents()
            
                embed_client = EmbeddingClient(**embed_config) 
            
                chroma_creator = ChromaCollectionCreator(processor, embed_client)
                
                # Step 2: Set topic input and number of questions
                topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
                num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)
                    
                submitted = st.form_submit_button("Submit")
                
                if submitted:
                    chroma_creator.create_chroma_collection()
                        
                    if len(processor.pages) > 0:
                        st.write(f"Generating {num_questions} questions for topic: {topic_input}")
                    
                    # Step 3: Initialize a QuizGenerator class using the topic, number of questions, and the chroma collection
                    generator = QuizGenerator(topic_input, num_questions, chroma_creator)
                    question_bank = generator.generate_quiz()
                    
                    # Step 4: Initialize the question bank list in st.session_state
                    st.session_state['question_bank'] = question_bank
                    # Step 5: Set a display_quiz flag in st.session_state to True
                    st.session_state['display_quiz'] = True
                    # Step 6: Set the question_index to 0 in st.session_state
                    st.session_state['question_index'] = 0

                    st.rerun()

    elif st.session_state["display_quiz"]:
        
        screen = st.empty()
        with screen.container():
            st.header("Generated Quiz Question:")
            quiz_manager = QuizManager(st.session_state['question_bank'])
            
            # Step 7: Set index_question using the Quiz Manager method get_question_at_index passing the st.session_state["question_index"]
            current_index = st.session_state.get("question_index", 0)
            index_question = quiz_manager.get_question_at_index(current_index)
            
            # Unpack choices for radio button
            choices = [f"{choice['key']}) {choice['value']}" for choice in index_question['choices']]
            
            with st.form("MCQ"):
                # Display the Question
                st.write(f"{st.session_state['question_index'] + 1}. {index_question['question']}")
                answer = st.radio("Choose an answer", choices, index=None)
                answer_choice = st.form_submit_button("Submit")
                
                if answer_choice and answer is not None:
                    correct_answer_key = index_question['answer']
                    if answer.startswith(correct_answer_key):
                        st.success("Correct!")
                    else:
                        st.error("Incorrect!")
                    st.write(f"Explanation: {index_question['explanation']}")
                
                # Step 8: Navigation buttons to move between questions
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.form_submit_button("Previous Question"):
                        quiz_manager.next_question_index(direction=-1)
                        st.rerun()
                with col3:
                    if st.form_submit_button("Next Question"):
                        quiz_manager.next_question_index(direction=1)
                        st.rerun()
