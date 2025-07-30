

# import streamlit as st
# import requests

# API_URL = "http://127.0.0.1:8000/ask"

# st.set_page_config(page_title="Changi Airport Chatbot", page_icon="🛫")
# st.title("🛫 Changi Airport AI Chatbot")
# st.markdown("Ask anything based on Changi Airport and Jewel Changi website content.")

# query = st.text_input("💬 Ask your question:", placeholder="e.g. What are the facilities in Terminal 3?")

# if query:
#     with st.spinner("Getting answer..."):
#         try:
#             response = requests.post(API_URL, json={"question": query})
#             response.raise_for_status()  # raise exception for HTTP errors

#             data = response.json()  # ✅ fix here

#             st.markdown(data["answer"])  # correctly access parsed JSON

#             with st.expander("Sources"):
#                 for i, doc in enumerate(data.get("sources", [])):
#                     st.markdown(f"""
#                     **🔗 Source {i+1}**  
#                     [{doc['url']}]({doc['url']})  
#                     _Excerpt:_  
#                     > {doc['excerpt']} ...
#                     """)
#         except Exception as e:
#             st.error(f"Error: {e}")

import os
os.environ["STREAMLIT_CONFIG_DIR"] = "./.streamlit"
import streamlit as st
from dotenv import load_dotenv
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import chromadb
from chromadb.config import Settings

load_dotenv()

# ========== Config ==========
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "langchain"
MODEL_NAME = "llama3-70b-8192"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ========== Load Embeddings & DB ==========
@st.cache_resource
def load_vector_db():
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    chroma_client = chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False)
    )

    vectordb = Chroma(
        client=chroma_client,
        collection_name=COLLECTION_NAME,
        embedding_function=embedding,
        persist_directory=CHROMA_PATH
    )
    return vectordb

vectordb = load_vector_db()

retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 2})

prompt_template = PromptTemplate.from_template("""
You are a helpful assistant with deep knowledge about Changi Airport and Jewel Singapore.

Use ONLY the context below to answer the user's question. Do not make up answers.

Context:
{context}

Question: {question}

Answer:
""")

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name=MODEL_NAME
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt_template},
    return_source_documents=True
)

# ========== Streamlit UI ==========
st.title("🛫 Changi Airport Chatbot")

query = st.text_input("Ask a question about Changi Airport")

if query:
    with st.spinner("Thinking..."):
        result = qa_chain.invoke({"query": query})
        answer = result["result"]

        st.markdown(f"**Answer:**\n\n{answer}")

        if result.get("source_documents"):
            st.markdown("### 🔍 Sources:")
            for doc in result["source_documents"]:
                url = doc.metadata.get("source", "Unknown")
                excerpt = doc.page_content[:300].replace("\n", " ")
                st.markdown(f"- [{url}]({url})\n\n`{excerpt}`")
