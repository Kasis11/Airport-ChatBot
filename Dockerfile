# Base image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose necessary ports
EXPOSE 8000
EXPOSE 8501

# Run both FastAPI and Streamlit
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port 8501 --server.address 0.0.0.0"]
