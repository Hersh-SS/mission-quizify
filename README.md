# **Quizify**

## **Overview**

Quizify is an interactive web application built using Streamlit, designed to generate quizzes based on user-uploaded documents and specified topics. The application features a robust quiz generator powered by Google Vertex AI, which creates multiple-choice questions and validates them to ensure uniqueness. Quizify interacts with users through a user-friendly interface, making quiz generation seamless and engaging.

The project leverages Vertex AI's generative models and Streamlit's interactive web framework to create a dynamic and user-friendly platform for generating educational quizzes. The application captures user input to tailor the quiz generation process, ensuring each quiz is relevant and informative.

## **Key Features**

- **Personalized Interaction**: Captures user input to generate relevant quiz questions.
- **Generative Model Integration**: Utilizes Vertex AI's generative models for dynamic question generation.
- **Interactive Chat Interface**: Built with Streamlit for real-time user interaction.
- **Question Validation**: Ensures generated questions are unique and informative.

## **Installation**

### **Prerequisites**

Before you begin, ensure you have the following installed on your system:

- Python 3.6 or higher
- Streamlit
- Vertex AI Python SDK

### **Step-by-Step Installation Guide**

#### **1. Clone the Repository**

Start by cloning the repository to your local machine. Use the following command:

```bash
git clone https://github.com/Hersh-SS/mission-quizify.git
cd mission-quizify
```

#### **2. Set Up a Virtual Environment**

It's a good practice to create a virtual environment for your Python projects. This keeps your project dependencies isolated. If you have virtualenv installed, create a new environment with:

```bash
python -m venv venv
```

Activate the virtual environment:

Windows (PowerShell):
```bash
.\venv\Scripts\Activate.ps1
```

Windows (CMD):
```bash
.\venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

#### **3. Install Dependencies**

Inside the virtual environment, install all necessary dependencies by running:
```bash
pip install -r requirements.txt
```

#### **4. Set Up Authentication for Vertex AI**
Download the JSON key file for your Google Cloud service account and set the GOOGLE_APPLICATION_CREDENTIALS environment variable:

Windows (PowerShell):
```bash
$env:GOOGLE_APPLICATION_CREDENTIALS="path\to\your\service-account-file.json"
```

Windows (CMD):
```bash
set GOOGLE_APPLICATION_CREDENTIALS=path\to\your\service-account-file.json
```

macOS/Linux:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-file.json"
```

#### **5. Run the Streamlit Application**
With the virtual environment activated and dependencies installed, you can start the Streamlit application by running:

```bash
streamlit run gemini_explorer.py
```

### **Accessing the Application**
With the server running, you can access the application at http://localhost:8501.

## **How It Works**

#### **1. Initialization:**
- The application initializes the Vertex AI generative model with the specified project ID.
- The document processor ingests user-uploaded documents.

#### **2. User Interaction:**
- The application captures user input for the quiz topic and the number of questions.
- Users can enter queries to generate quiz questions through an intuitive interface.

#### **3. Generative Responses:**
- The quiz generator creates questions using Vertex AI's generative models.
- The questions are validated to ensure uniqueness and then displayed in the user interface.

#### **4. Session Management:**
- The application maintains the state using Streamlit's session state.
- Each generated quiz is stored and displayed sequentially for easy navigation.

## **Example Use**

#### **1. Upload Documents:**
- Users upload documents to be processed.

#### **2. Enter Quiz Details:**
- Users specify the topic and number of questions for the quiz.

#### **3. Generate and Navigate Quiz:**
- The generated quiz questions are displayed, and users can navigate through them.
