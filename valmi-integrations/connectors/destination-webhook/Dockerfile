FROM  python:3.10.0-alpine  as base

# build and load all requirements
FROM base as builder
WORKDIR /valmi/integration_code

# upgrade pip to the latest version
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base


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
RUN apk --no-cache add bash

# copy payload code only
COPY main.py ./
COPY destination_webhook ./destination_webhook
COPY extensions ./extensions
COPY destination_container_wrapper.py ./
COPY proc_stdout_handler.py ./
COPY handlers.py ./
COPY docker-entrypoint.sh ./
RUN chmod +x ./docker-entrypoint.sh

ENV PYTHONUNBUFFERED 1
ENV VALMI_ENTRYPOINT "python /valmi/integration_code/main.py"
ENV VALMI_INTERMEDIATE_STORE "{\"provider\": \"local\", \"local\": {\"directory\": \"/tmp/shared_dir/intermediate_store\"}}"
ENTRYPOINT ["./docker-entrypoint.sh"]

LABEL io.valmi.version=0.1.0
LABEL io.valmi.name=valmi/destination-webhook
