FROM python:3.10-slim as application

WORKDIR /app

# arm architecture platform builds need postgres drivers installing via apt
ARG TARGETARCH
RUN if [ "${TARGETARCH}" != "amd64" ]; then apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*; fi;

# Install python packages locally in a virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app/

EXPOSE 8000

USER nobody

CMD ["gunicorn", "src.main:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]