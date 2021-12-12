FROM python:3.8-slim-buster

COPY requirements.txt ./

RUN apt-get update \
    && apt-get -y install libglib2.0-0 git \
    && pip install -r requirements.txt \
    && pip install torch==1.10.0+cpu torchvision==0.11.1+cpu torchaudio==0.10.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html \
    && pip install git+https://github.com/keurcien/seam-carving.git@numba \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY app ./app

ENTRYPOINT [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]