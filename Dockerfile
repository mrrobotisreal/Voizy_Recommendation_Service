FROM python:3.10

RUN apt-get update && apt-get install -y build-essential python3-dev libatlas-base-dev gfortran && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && pip install --no-use-pep517 -r requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python", "app.py"]