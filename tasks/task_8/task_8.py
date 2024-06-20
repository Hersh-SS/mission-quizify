import re
import streamlit as st
import os
import sys
import json
import logging
from pydantic import BaseModel, Field, ValidationError
sys.path.append(os.path.abspath('../../'))
from tasks.task_3.task_3 import DocumentProcessor
from tasks.task_4.task_4 import EmbeddingClient
from tasks.task_5.task_5 import ChromaCollectionCreator

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_vertexai import VertexAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Choice(BaseModel):
    key: str
    value: str

class QuizQuestion(BaseModel):
    question: str
    choices: list[Choice]
    answer: str
    explanation: str

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
        self.question_bank = [] # Initialize the question bank to store questions
        self.system_template = """
            You are a subject matter expert on the topic: {topic}
            
            Follow the instructions to create a quiz question:
            1. Generate a question based on the topic provided and context as key "question"
            2. Provide 4 multiple choice answers to the question as a list of key-value pairs "choices"
            3. Provide the correct answer for the question from the list of answers as key "answer"
            4. Provide an explanation as to why the answer is correct as key "explanation"
            
            Ensure your response is a valid JSON object with the following structure:
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
        """
        Initializes and configures the Large Language Model (LLM) for generating quiz questions.

        This method should handle any setup required to interact with the LLM, including authentication,
        setting up any necessary parameters, or selecting a specific model.

        :return: An instance or configuration for the LLM.
        """
        self.llm = VertexAI(
            model_name = "gemini-pro",
            temperature = 0.8, # Increased for less deterministic questions 
            max_output_tokens = 500
        )

    def generate_question_with_vectorstore(self):
        """
        Generates a quiz question based on the topic provided using a vectorstore

        :return: A JSON object representing the generated quiz question.
        """
        if not self.llm:
            self.init_llm()
        if not self.vectorstore:
            raise ValueError("Vectorstore not provided.")

        # Retrieve context from the vectorstore
        context_documents = self.vectorstore.query_chroma_collection(self.topic)
        if context_documents:
            if isinstance(context_documents[0], tuple):
                context_document = context_documents[0][0]  # Extract the Document object from the tuple
            else:
                context_document = context_documents[0]  # Assume it's a list of Document objects directly
            context = context_document.page_content
        else:
            context = "No context available"

        # Set up a parser + inject instructions into the prompt template
        parser = JsonOutputParser(pydantic_object=QuizQuestion)
        prompt = PromptTemplate(
            template=self.system_template,
            input_variables=["topic", "context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # Create the chain with prompt, model, and parser
        chain = prompt | self.llm | parser

        # Generate the quiz question
        response = chain.invoke({"topic": self.topic, "context": context})

        return response

    def generate_quiz(self) -> list:
        """
        Task: Generate a list of unique quiz questions based on the specified topic and number of questions.

        This method orchestrates the quiz generation process by utilizing the `generate_question_with_vectorstore` method to generate each question and the `validate_question` method to ensure its uniqueness before adding it to the quiz.

        Steps:
            1. Initialize an empty list to store the unique quiz questions.
            2. Loop through the desired number of questions (`num_questions`), generating each question via `generate_question_with_vectorstore`.
            3. For each generated question, validate its uniqueness using `validate_question`.
            4. If the question is unique, add it to the quiz; if not, attempt to generate a new question (consider implementing a retry limit).
            5. Return the compiled list of unique quiz questions.

        Returns:
        - A list of dictionaries, where each dictionary represents a unique quiz question generated based on the topic.

        Note: This method relies on `generate_question_with_vectorstore` for question generation and `validate_question` for ensuring question uniqueness. Ensure `question_bank` is properly initialized and managed.
        """
        self.question_bank = [] # Reset the question bank
        retry_limit = 5

        for _ in range(self.num_questions):
            for attempt in range(retry_limit):
                question = self.generate_question_with_vectorstore()
                logger.info(f"Raw LLM Response: {question}")

                if question:
                    break  # Exit retry loop if successful

            if question and self.validate_question(question):
                logger.info("Successfully generated unique question")
                # Add the valid and unique question to the bank
                self.question_bank.append(question)
            else:
                logger.error("Duplicate or invalid question detected after retries.")

        return self.question_bank

    def validate_question(self, question: QuizQuestion) -> bool:
        """
        Task: Validate a quiz question for uniqueness within the generated quiz.

        This method checks if the provided question (as a dictionary) is unique based on its text content compared to previously generated questions stored in `question_bank`. The goal is to ensure that no duplicate questions are added to the quiz.

        Steps:
            1. Extract the question text from the provided dictionary.
            2. Iterate over the existing questions in `question_bank` and compare their texts to the current question's text.
            3. If a duplicate is found, return False to indicate the question is not unique.
            4. If no duplicates are found, return True, indicating the question is unique and can be added to the quiz.

        Parameters:
        - question: A dictionary representing the generated quiz question, expected to contain at least a "question" key.

        Returns:
        - A boolean value: True if the question is unique, False otherwise.

        Note: This method assumes `question` is a valid dictionary and `question_bank` has been properly initialized.
        """
        # Consider missing 'question' key as invalid in the dict object
        if 'question' not in question:
            return False

        # Check if a question with the same text already exists in the self.question_bank
        for existing_question in self.question_bank:
            if existing_question.get('question') == question['question']:
                return False

        return True

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
            st.header("Generated Quiz Questions: ")
            for question in st.session_state.question_bank:
                st.write(question)
    elif st.session_state.submitted and st.session_state.question_bank is None:
        screen.empty()  # Clear the initial screen
        with screen.container():
            st.header("Generated Quiz Questions: ")
            st.write("No quiz questions generated.")

if __name__ == "__main__":
    main()
