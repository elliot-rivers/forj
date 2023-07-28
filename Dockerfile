FROM python:3.10-slim AS base

RUN apt-get update
RUN apt-get install -y build-essential
RUN pip install pipenv==2022.3.28

ARG environment
ARG artifactory_url

WORKDIR /app

COPY Pipfile  setup.py VERSION ./
COPY Pipfile setup.py VERSION ./
RUN export ARTIFACTORY_URL=$artifactory_url && \
    pipenv install --deploy --verbose --ignore-pipfile \
    $(if [ "$environment" = "development" ]; then echo "--dev"; fi)

COPY . .

ENTRYPOINT ["pipenv", "run"]
CMD ["/bin/bash"]
