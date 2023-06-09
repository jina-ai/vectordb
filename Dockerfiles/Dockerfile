ARG PY_VERSION=3.9

FROM python:${PY_VERSION}-slim

RUN apt-get update && apt-get install --no-install-recommends -y gcc libc6-dev pkg-config wget build-essential

COPY . /vectordb/

RUN cd /vectordb && pip install -U pip && pip install .

RUN pip install -U docarray[hnswlib]>=0.33

ENTRYPOINT ["vectordb"]