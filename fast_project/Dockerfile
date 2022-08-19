# https://fastapi.tiangolo.com/deployment/docker/
# 
FROM python:3.10

# install poetry - pinning version
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.1.14

# 
WORKDIR /code

# 
#COPY ./requirements-docker.txt /code/requirements.txt
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock

#RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN poetry install

# 
COPY ./app /code/app

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

EXPOSE 8080