FROM python:3.12-slim

LABEL org.opencontainers.image.source=https://github.com/dartmouth/todo-demo

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY db.py .
COPY main.py .

# Create non-root user
RUN groupadd -g 1005 appgroup && \
    useradd -u 1005 -g appgroup appuser && \
    chown -R appuser:appgroup /app

USER appuser

# Streamlit configuration
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]