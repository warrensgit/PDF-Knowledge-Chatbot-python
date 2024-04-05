# PDF Knowledge Chatbot

This Repl uses [OpenAI](https://platform.openai.com/), [Pinecone](https://app.pinecone.io/), [LangChain](https://www.langchain.com/), and [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) to allow you to chat with any PDFs you upload to the training data.

In order to use this Repl, you'll need to fork your own copy, and follow the setup instructions below to get started.

## Setup

1. Fork the Repl from your Replit account. You'll want to make sure the Repl is Private, as you'll be using your OpenAI and Pinecone API keys, and you want to make sure they are not available publicly.
2. In your Pinecone account, set up a new index called `businesschatbot`. Take note of the environment and size. 
3. Use the **Secrets** to add in your `OPENAI_API_KEY` and `PINECONE_API_KEY`. Storing them in Secrets keeps your API keys secure and accessible from within your code. 
4. Fill the folder called `/training-data/files/` with all of the PDFs you'd like your chatbot to be able to query.
5. Make sure the Pinecone index initialization code on lines 67-75 in the `main.py` file matches the index you created in step 2. 
6. Click **Run** and let the script process, batch, and generate embeddings for your PDFs. 
7. In the Webview, you'll be able to preview chatting with your PDF Knowledge Chatbot. Select **New tab** to preview the Webview in a new browser tab.
8. To share this chatbot with others, select **Deploy** and choose the deployment option that works best for you. You'll have a custom URL you can share with others to securely access your bot, and separate dev and prod instances so you can keep making changes if you'd like. 

## Notes
* You'll need to be a [Replit Core member](https://replit.com/pricing) to create private Repls. 
* The app will automatically add in any new PDFs you drop in when you click **Run**.
* The limit of how many chunks of knowledge you can feed to this bot depends on your Pinecone subscription. You may need to upgrade your account to give your bot more training data.