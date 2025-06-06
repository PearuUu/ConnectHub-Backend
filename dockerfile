FROM python:3.10-slim

WORKDIR /app

COPY requirements/req.txt .
RUN pip install --no-cache-dir -r req.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]