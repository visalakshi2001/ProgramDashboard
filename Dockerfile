# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy  Streamlit app code to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8501 (default Streamlit port)
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "app.py"]