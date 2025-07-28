

import streamlit as st
import requests

API_URL = "https://6887313def0ea37977f205df--voluble-custard-6ec933.netlify.app/ask"

st.set_page_config(page_title="Changi Airport Chatbot", page_icon="🛫")
st.title("🛫 Changi Airport AI Chatbot")
st.markdown("Ask anything based on Changi Airport and Jewel Changi website content.")

query = st.text_input("💬 Ask your question:", placeholder="e.g. What are the facilities in Terminal 3?")

if query:
    with st.spinner("Getting answer..."):
        try:
            response = requests.post(API_URL, json={"question": query})
            response.raise_for_status()  # raise exception for HTTP errors

            data = response.json()  # ✅ fix here

            st.markdown(data["answer"])  # correctly access parsed JSON

            with st.expander("Sources"):
                for i, doc in enumerate(data.get("sources", [])):
                    st.markdown(f"""
                    **🔗 Source {i+1}**  
                    [{doc['url']}]({doc['url']})  
                    _Excerpt:_  
                    > {doc['excerpt']} ...
                    """)
        except Exception as e:
            st.error(f"Error: {e}")
