FROM python:3.11-alpine
WORKDIR /app
COPY . .
RUN apk add --no-cache musl-dev linux-headers g++
RUN pip install --install-option="--jobs=5" --no-cache-dir -r requirements.txt
RUN apk del --no-cache musl-dev linux-headers g++
CMD ["python", "main.py"]
