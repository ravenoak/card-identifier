ARG USER_ID=1000
ARG USER_NAME="card-identifier"

FROM tensorflow/tensorflow:2.9.1-gpu-jupyter
ARG USER_ID
ARG USER_NAME

RUN useradd -m -s /bin/bash -u ${USER_ID} -U ${USER_NAME} && \
    apt-get update && \
    apt-get upgrade -y && \
    apt autoremove -y && \
    /usr/bin/python3 -m pip install --upgrade pip && \
    /usr/bin/python3 -m pip install --upgrade setuptools && \
    /usr/bin/python3 -m pip install --upgrade "tensorflow-hub[make_image_classifier]"

USER ${USER_NAME}
EXPOSE 6006
EXPOSE 8888
