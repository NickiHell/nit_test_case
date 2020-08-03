FROM python:3

ENV PROJECT_ROOT=/app
ENV SRC=/app/offers
ENV PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT

RUN mkdir $PROJECT_ROOT/
RUN mkdir $SRC/

COPY ./Pipfile ./Pipfile.lock $SRC/
WORKDIR $SRC

RUN pip install --upgrade wheel pip pipenv
RUN pipenv install

COPY ./src/offers $SRC

CMD ["pipenv", "run", "python", "main.py"]
