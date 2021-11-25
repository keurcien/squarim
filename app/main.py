import base64
import io

import cv2 as cv
import numpy as np
import requests
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from app import Squarim

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return "Squarim est désormais disponible à l'adresse suivante : https://squarim.web.app/"


@app.post("/")
def stretch(
    file: str = Form(...),
    name: str = Form(...),
    left: int = Form(...),
    right: int = Form(...),
    mirror: bool = Form(...),
):

    if not file.startswith("http"):
        _, imgstr = file.split(";base64,")
        nparr = np.fromstring(base64.b64decode(imgstr), np.uint8)
        img = cv.imdecode(nparr, cv.IMREAD_COLOR)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    else:
        response = requests.get(file)
        img = Image.open(io.BytesIO(response.content))
        img = np.asarray(img)

    squarimg = Squarim(img)
    img_ = squarimg.stretch(left=left, right=right, mirror=mirror)

    if squarimg.rotated:
        img_ = img_.rotate(90)

    buff = io.BytesIO()
    img_.save(buff, format="JPEG")
    imgstr_ = base64.b64encode(buff.getvalue()).decode("utf-8")
    return {"name": name, "dataURL": f"data:image/jpeg;base64,{imgstr_}"}
