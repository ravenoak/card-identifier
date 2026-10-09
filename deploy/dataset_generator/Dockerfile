# syntax=docker/dockerfile:1
# Build from the repository root: docker build -f deploy/dataset_generator/Dockerfile .
ARG PYTHON_VERSION="3.14"
ARG UV_VERSION="0.13.0"
ARG USER_ID=1000
ARG USER_NAME="card-identifier"

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

#############################
# Build the virtual environment
#############################
FROM python:${PYTHON_VERSION}-slim-trixie AS builder
COPY --from=uv /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies first, so source changes do not invalidate this layer.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

#############################
# Runtime for the application
#############################
FROM python:${PYTHON_VERSION}-slim-trixie AS runtime
ARG USER_ID
ARG USER_NAME

RUN useradd -m -s /bin/bash -u ${USER_ID} -U ${USER_NAME}
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:${PATH}"

USER ${USER_NAME}
WORKDIR /home/${USER_NAME}
