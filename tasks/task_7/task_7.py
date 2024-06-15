import streamlit as st
from langchain_google_vertexai import VertexAI
from langchain_core.prompts import PromptTemplate
import os
import sys
sys.path.append(os.path.abspath('../../'))

class QuizGenerator:
    def __init__(self, topic=None, num_questions=1, vectorstore=None):
        """
        Initializes the QuizGenerator with a required topic, the number of questions for the quiz,
        and an optional vectorstore for querying related information.

        :param topic: A string representing the required topic of the quiz.
        :param num_questions: An integer representing the number of questions to generate for the quiz, up to a maximum of 10.
        :param vectorstore: An optional vectorstore instance (e.g., ChromaDB) to be used for querying information related to the quiz topic.
        """
        if not topic:
            self.topic = "General Knowledge"
        else:
            self.topic = topic

        if num_questions > 10:
            raise ValueError("Number of questions cannot exceed 10.")
        self.num_questions = num_questions

        self.vectorstore = vectorstore
        self.llm = None
        self.system_template = """
            You are a subject matter expert on the topic: {topic}
            
            Follow the instructions to create a quiz question:
            1. Generate a question based on the topic provided and context as key "question"
            2. Provide 4 multiple choice answers to the question as a list of key-value pairs "choices"
            3. Provide the correct answer for the question from the list of answers as key "answer"
            4. Provide an explanation as to why the answer is correct as key "explanation"
            
            You must respond as a JSON object with the following structure:
            {{
                "question": "<question>",
                "choices": [
                    {{"key": "A", "value": "<choice>"}},
                    {{"key": "B", "value": "<choice>"}},
                    {{"key": "C", "value": "<choice>"}},
                    {{"key": "D", "value": "<choice>"}}
                ],
                "answer": "<answer key from choices list>",
                "explanation": "<explanation as to why the answer is correct>"
            }}
            
            Context: {context}
            """
    
    def init_llm(self):
        self.llm = VertexAI(
            model_name="gemini-pro",
            temperature=0.7,
            max_output_tokens=512
        )
        
    def generate_question_with_vectorstore(self):
        if not self.llm:
            self.init_llm()

        if not self.vectorstore:
            raise ValueError("Vectorstore is not initialized.")

        # Retrieve context from the vectorstore
        context_document = self.vectorstore.query_chroma_collection(self.topic)
        context = context_document[0].page_content if context_document else "No context available"

        # Create the prompt
        prompt = self.system_template.format(topic=self.topic, context=context)

        # Generate the quiz question
        response = self.llm(prompt)

        return response

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
        st.session_state.question = None

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
                    st.session_state.submitted = True
                    st.session_state.topic_input = topic_input
                    st.session_state.num_questions = num_questions

                    chroma_creator.create_chroma_collection()
                    
                    generator = QuizGenerator(topic_input, num_questions, chroma_creator)
                    question = generator.generate_question_with_vectorstore()
                    st.session_state.question = question

                    st.experimental_rerun()

    if st.session_state.submitted and st.session_state.question is not None:
        screen.empty()  # Clear the initial screen
        with screen.container():
            st.header("Generated Quiz Question: ")
            st.write(st.session_state.question)
    elif st.session_state.submitted and st.session_state.question is None:
        screen.empty()  # Clear the initial screen
        with screen.container():
            st.header("Generated Quiz Question: ")
            st.write("No quiz question generated.")

if __name__ == "__main__":
    main()
