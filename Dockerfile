FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
COPY scripts/ scripts/
COPY data/ data/
RUN python -m scripts.train_model
RUN useradd --create-home appuser && mkdir -p /app/runtime \
    && chown appuser:appuser /app/runtime
ENV DB_PATH=/app/runtime/tickets.db
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
