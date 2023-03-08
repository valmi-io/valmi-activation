FROM python:3.10

ARG USER_ID
ARG GROUP_ID

COPY requirements/test-requirements.txt /tmp/test-requirements.txt
RUN set -x \
    && python -m venv /opt/valmi-activation \
    && /opt/valmi-activation/bin/python -m pip install -U pip wheel setuptools \
    && /opt/valmi-activation/bin/python -m pip install --upgrade pip \
    && /opt/valmi-activation/bin/python -m pip install --no-cache-dir --timeout 1000 -r /tmp/test-requirements.txt \
    && mkdir -p /workspace && chown -R $USER_ID:$GROUP_ID /workspace && chown -R $USER_ID:$GROUP_ID /opt/valmi-activation
#RUN addgroup --gid $GROUP_ID user
#RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user

RUN curl -fsSL https://get.docker.com | sh

#USER user

WORKDIR /workspace 
#COPY . /workspace/
ENV PATH="/opt/valmi-activation/bin:${PATH}"
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /workspace/src
ENTRYPOINT ["/workspace/docker-entrypoint.sh"]
CMD ["uvicorn", "main:app",   "--port", "8000", "--host","0.0.0.0", "--log-level" ,"debug"]
