FROM python:3.11.3-slim

ENV PYTHONUNBUFFERED 1
WORKDIR /opt

# Create venv, add it to path and install requirements
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# Copy the basis of app
COPY alembic alembic
COPY alembic.ini .
COPY pyproject.toml .
COPY init.sh .

# Create new user to run app process as unprivilaged user
RUN addgroup --gid 1001 --system uvicorn && \
    adduser --gid 1001 --shell /bin/false --disabled-password --uid 1001 uvicorn
