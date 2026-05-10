FROM mcr.microsoft.com/dotnet/sdk:8.0

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
