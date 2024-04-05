# Standard library imports
import os
from pathlib import Path
from uuid import uuid4

# Related third-party imports
import fitz  # PyMuPDF
import openai
import pinecone
from flask import Flask, request, jsonify, render_template, send_from_directory
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from threading import Thread, Event
from tqdm.auto import tqdm

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
conversation_memory = None


def extract_text_from_pdf(pdf_path):
  """
  Extracts text from a PDF file.
  Args:
      pdf_path (str): The file path to the PDF document.
  Returns:
      str: The extracted text from the PDF.
  """
  text = ''
  with fitz.open(pdf_path) as pdf:
    for page in pdf:
      text += page.get_text()
  return text


def preprocess_text(text):
  """
  Preprocess the extracted text as needed, for example,
  removing line breaks, page numbers, etc.
  Args:
      text (str): The text to be processed.
  Returns:
      str: The preprocessed text.
  """
  # Example of simple preprocessing, custom adjustments may be needed
  text = text.strip()  # Remove leading and trailing whitespace
  text = ' '.join(
      text.split())  # Replace multiple whitespace with single space
  return text


def batcher(iterable, batch_size=1):
  l = len(iterable)
  for ndx in range(0, l, batch_size):
    yield iterable[ndx:min(ndx + batch_size, l)]


## train() sets up the training data.
## It reads all content in training-data/files folder and
## serializes it into chunks the LLM can parse
def train():

  # Setup Pinecone & add OpenAI API key
  pinecone_api_key = os.environ['PINECONE_API_KEY']
  pinecone.init(api_key=pinecone_api_key, environment='gcp-starter')

  # Assuming 'businesschatbot' is the index name
  index_name = 'businesschatbot'

  # Check if the Pinecone index exists or else create it
  if index_name not in pinecone.list_indexes():
    pinecone.create_index(index_name, 1536)
  index = pinecone.Index(index_name)

  # Prepare the training data
  trainingData = list(Path("training-data/files/").glob("**/*.*"))
  # Load data from files
  data = []
  for training_file_path in trainingData:
    try:
      if training_file_path.suffix.lower() == '.pdf':
        # Extract text from PDF file
        extracted_text = extract_text_from_pdf(training_file_path)
        processed_text = preprocess_text(extracted_text)
        data.append(processed_text)
      else:
        # Process other file types as before
        with training_file_path.open('r', encoding='utf-8') as f:
          print(f"Add {f.name} to dataset")
          data.append(f.read())
    except Exception as e:
      print(f"Failed to read {training_file_path}: {e}")

  # Generate embeddings for the data
  openai_api_key = os.environ['OPENAI_API_KEY']
  model_name = 'text-embedding-ada-002'
  embed = OpenAIEmbeddings(
      model=model_name,
      openai_api_key=openai_api_key,
  )

  # Prepare metadata and embeddings
  # Assuming you have a way to generate unique IDs for each record
  upsert_data = []
  for text in data:
    unique_id = str(uuid4())
    embedding = embed.embed_query(text)  # Generate embeddings
    upsert_data.append((unique_id, embedding, {"text": text}))

  # Batch upsert to Pinecone index
  for batch_data in batcher(upsert_data, batch_size=100):
    response = index.upsert(vectors=batch_data)
    print(response)

  index = pinecone.GRPCIndex(index_name)
  index.describe_index_stats()

  text_field = "text"
  index = pinecone.Index(index_name)
  vectorstore = Pinecone(index, embed, text_field)

  # Setup the LLM
  from sqlalchemy.sql.expression import true
  llm = ChatOpenAI(openai_api_key=openai_api_key,
                   model_name='gpt-4',
                   temperature=0.0)

  conversational_memory = ConversationBufferWindowMemory(
      memory_key='chat_history', k=5, return_messages=True)

  global qa
  qa = RetrievalQA.from_chain_type(llm=llm,
                                   chain_type="stuff",
                                   retriever=vectorstore.as_retriever())

  tools = [
      Tool(name='Knowledge Base',
           func=qa.run,
           description=(
               'use this tool when answering general knowledge queries to get '
               'more information about the topic'))
  ]

  # Setup the Agent
  global agent
  agent = initialize_agent(
      tools=tools,
      llm=llm,
      agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
      verbose=False,
      max_iterations=3,
      early_stopping_method='generate',
      memory=conversational_memory,
  )


static_folder_path = 'frontend/build'
if not os.path.exists(static_folder_path):
  raise FileNotFoundError(
      f"The static_folder {static_folder_path} does not exist.")

### --- ROUTES --- ###


## This requests the home page index.html content
@app.route('/')
def index():
  if app.static_folder is None:
    raise RuntimeError('The static folder is not set.')
  return send_from_directory(app.static_folder, 'index.html')


## This route sends a POST request to the LLM and returns the message to the front end
@app.route('/respond', methods=['POST'])
def respond():
  global agent
  if not request.json:
    # Return an error response if JSON is not provided
    return jsonify({
        'error': 'Bad Request',
        'message': 'Request body must be a JSON object'
    }), 400

  data = request.json
  message = data.get('message', '')
  chat_history = data.get('chat_history', [])

  # Use the agent to generate a response
  tool_response = qa.run(message)
  message_with_context = f"Context: {tool_response} \n\n {message}"
  bot_message = agent.run(message_with_context)

  # Check if the AI was not able to understand the question
  if not bot_message or bot_message.strip() == '':
    bot_message = "I'm sorry, I did not understand your question. Can you please try rephrasing it?"

  chat_history.append((message, bot_message))
  return jsonify({'bot_message': bot_message, 'chat_history': chat_history})


if __name__ == '__main__':
  train()
  app.run(host='0.0.0.0', port=5000)
