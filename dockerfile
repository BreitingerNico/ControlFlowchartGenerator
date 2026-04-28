# Use an official Python slim image
FROM python:3.11-slim

# Install Graphviz system dependencies
RUN apt-get update && apt-get install -y \
    graphviz \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR CONTROLFLOWCHARTGENERATOR/app

# Install python dependencies
RUN echo "graphviz" > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY app/ .

# Ensure python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1

# Run the main script
CMD ["python", "Main.py"]