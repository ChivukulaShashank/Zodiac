FROM python:3.11-slim

RUN apt-get update && apt-get install -y python3.11 python3.11-venv python3-pip rustup lua5.4 luarocks liblua5.4-dev build-essential git curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN pip install .

COPY . .

CMD ["python3", "-m", "src.main"]