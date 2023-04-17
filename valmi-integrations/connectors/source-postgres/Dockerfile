FROM  python:3.9.16-slim  as base

# build and load all requirements
FROM base as builder
WORKDIR /valmi/integration_code

# upgrade pip to the latest version
RUN apt upgrade \
    && pip install --upgrade pip \
    && apt install tzdata  


COPY setup.py ./
# install necessary packages to a temporary folder
RUN pip install --prefix=/install .

# build a clean environment
FROM base
WORKDIR /valmi/integration_code

# copy all loaded and built libraries to a pure basic image
COPY --from=builder /install /usr/local
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

# bash is installed for more convenient debugging.
RUN apt install bash

# copy payload code only
COPY main.py ./
COPY source_postgres ./source_postgres
COPY valmi_dbt ./valmi_dbt 
 
COPY docker-entrypoint.sh ./
RUN chmod +x ./docker-entrypoint.sh

RUN groupadd -r valmi_group && useradd -r -g valmi_group valmi_user
RUN chown  -R valmi_user:valmi_group /valmi/integration_code
USER valmi_user 

ENV PYTHONUNBUFFERED 1
ENV VALMI_ENTRYPOINT "python /valmi/integration_code/main.py"
ENV VALMI_INTERMEDIATE_STORE "{\"provider\": \"local\", \"local\": {\"directory\": \"/tmp/shared_dir/intermediate_store\"}}"
ENTRYPOINT ["./docker-entrypoint.sh"]

ARG VERSION
LABEL io.valmi.version=${VERSION}
LABEL io.valmi.name=valmiio/source-postgres
