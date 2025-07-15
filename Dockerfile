ARG PYTHON_VER="3.8"

FROM python:${PYTHON_VER}-slim as BASE

WORKDIR /local

COPY . .

RUN pip3 install --no-cache-dir --upgrade jinja2 pip setuptools wheel \
    && python3 setup.py install \
# Clean up pycache
    && find / | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf \
# Clean up local folder
    && rm /local/* -rf

ARG J2LINT_VER=""
ARG RELEASE_DATE=""

LABEL org.opencontainers.image.authors="Arista Ansible Team <ansible@arista.com>" \
    org.opencontainers.image.created=${RELEASE_DATE} \
    org.opencontainers.image.title="j2lint" \
    org.opencontainers.image.vendor="Arista" \
    org.opencontainers.image.version=${J2LINT_VER}
