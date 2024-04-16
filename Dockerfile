FROM python:3.12-slim as application

WORKDIR /app

# Install python packages locally in a virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY src /app/src
COPY requirements.lock pyproject.toml /app/
RUN pip install --no-cache-dir -r requirements.lock && edge-proxy-config

EXPOSE 8000

USER nobody

CMD ["edge-proxy-serve"]
