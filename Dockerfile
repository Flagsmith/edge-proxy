FROM python:3.12-slim as application

WORKDIR /app

# Install python packages locally in a virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.lock /app/
RUN pip install --no-cache-dir --upgrade -r requirements.lock

COPY . /app/

EXPOSE 8000

USER nobody

CMD ["uvicorn", "edge_proxy.main:app", "--host", "0.0.0.0", "--port", "8000"]
