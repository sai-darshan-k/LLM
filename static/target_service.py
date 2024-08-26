# target_service.py

from flask import Flask, request, jsonify
import chainlit as cl
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")  # Get the API key

app = Flask(__name__)

prompt = """
    (system: ,You are a crop assistant, answer the user queries related to specific topic),
    (user:, Question: {question})  
"""
promptinstance = ChatPromptTemplate.from_template(prompt)

@cl.on_message
async def assistant(message: cl.Message):
    input_text = message.content
    groqllm = ChatGroq(model="llama3-8b-8192", temperature=0)
    output = StrOutputParser()
    chain = promptinstance | groqllm | output
    res = chain.invoke({'question': input_text})
    await cl.Message(content=res).send()

@app.route('/process', methods=['POST'])
async def process_request():
    data = request.get_json()
    question = data.get('question')
    response = await assistant(question)  # Call the Chainlit assistant
    return jsonify({'answer': response})

if __name__ == '__main__':
    app.run(port=5001)  # Run on port 5001
