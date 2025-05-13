FROM python:3.12.10-slim-bullseye


# ENV PYTHONUNBUFFERED 1
# ENV LANG en_US.utf8
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends\
#     locales\
#     python3 \
#     python3-pip \
#     python3-venv \
#     git && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*


COPY ./requirements.txt .
# need to understand it...
RUN pip install uv && uv pip install --system -r requirements.txt && pip cache purge && uv cache clean

WORKDIR /code
COPY . /code

# convert to sh file to needed initialize it
# CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
CMD [ "/code/.dockerinit.sh" ]
EXPOSE 8000


