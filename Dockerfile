
# Use official python base image
FROM python:3.12-slim
LABEL org.opencontainers.image.source=https://github.com/dartmouth/todo-demo

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app_dashboard.py .
#COPY app.py .

RUN groupadd -g 1005 appgroup && \
    useradd -u 1005 -g appgroup appuser && \
    chown -R appuser:appgroup /app

USER appuser

ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501

# Command to run the app
CMD ["streamlit", "run", "app_dashboard.py"]
