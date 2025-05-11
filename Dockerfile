FROM python:3.12.10-slim-bullseye


ENV PYTHONUNBUFFERED 1
# ENV LANG en_EN.UTF-8

COPY ./requirements.txt .
# need to understand it...
RUN pip install uv && uv pip install --system -r requirements.txt && pip cache purge && uv cache clean

WORKDIR /code
COPY . /code/

# convert to sh file to needed initialize it
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
EXPOSE 8000


