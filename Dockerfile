# Use specified image as base
FROM python:3.11.5-bookworm

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory and copy requirements
WORKDIR /code
COPY . /code/
RUN pip install -r requirements.txt

# Switch to a non-root user
RUN mkdir -p /home/appuser && useradd appuser && chown -R appuser /code && chown -R appuser /home/appuser
USER appuser

# Expose port
EXPOSE 8502
WORKDIR /code

RUN ls -la /code

CMD streamlit run /code/streamlit_app.py --server.port=8502 --logger.level=info 2> streamlit_logs.log