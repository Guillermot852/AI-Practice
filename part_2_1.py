from langchain_ollama import OllamaLLM 
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st

# Define the template for the conversation
template = """
Answer the question below:

Here is the conversation history: {context}

Question: {question}

Answer: 
"""

# Initialize the model and prompt
model = OllamaLLM(model='llama3.2')
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Initialize session state for context
if 'context' not in st.session_state:
    st.session_state['context'] = ""
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ""

def process_input():
    """Handle user input and update the conversation context."""
    user_input = st.session_state['user_input']
    if user_input:
        # Get the current conversation context
        context = st.session_state['context']
        
        # Generate the bot response
        result = chain.invoke({"context": context, "question": user_input})
        
        # Update the context with the new user and bot exchange
        new_context = f"\nYou: {user_input}\nBot: {result}"
        st.session_state['context'] += new_context
        
        # Clear the input box
        st.session_state['user_input'] = ""

def main():
    st.title("Ollama Chatbot")
    st.write("Chat with the bot below:")

    # Display the conversation history
    st.text_area("Conversation History", st.session_state['context'], height=400, disabled=True)

    # Input box for user input
    st.text_input("You:", key='user_input', on_change=process_input)

if __name__ == "__main__":
    main()
