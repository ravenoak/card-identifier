ARG PACKAGE_NAME="collectable_card_identifier"
ARG PACKAGE_VER="0.1.0"
ARG PYTHON_VERSION="3.10"
ARG USER_ID=1000
ARG USER_NAME="card-identifier"

FROM python:${PYTHON_VERSION} as base
ARG USER_ID
ARG USER_NAME

RUN apt update && \
    apt upgrade -y && \
    apt autoremove -y && \
    apt install -y pipenv && \
    /usr/bin/python3 -m pip install --upgrade pip && \
    /usr/bin/python3 -m pip install --upgrade setuptools

#############################
# Build the application
#############################
FROM base as builder
ARG USER_ID

RUN useradd -m -s /bin/bash -u ${USER_ID} -U builder && \
    mkdir /tmp/build && \
    chown builder /tmp/build

COPY --chown=builder:builder . /tmp/build/

USER builder
WORKDIR /tmp/build/
RUN curl -sSL https://install.python-poetry.org | POETRY_PREVIEW=1 python3 - && \
    /home/builder/.local/bin/poetry build

#############################
# Runtime for the application
#############################
FROM base as runtime
ARG PACKAGE_NAME
ARG PACKAGE_VER
ARG USER_ID
ARG USER_NAME

COPY --from=builder /tmp/build/dist/ /tmp/
RUN useradd -m -s /bin/bash -u ${USER_ID} -U ${USER_NAME}
USER ${USER_NAME}
RUN pip install --user /tmp/${PACKAGE_NAME}-${PACKAGE_VER}-py3-none-any.whl
WORKDIR /home/${USER_NAME}
