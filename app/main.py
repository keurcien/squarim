import base64
import io
import time

import cv2 as cv
import numpy as np
import requests
import seam_carving
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from app import Squarim
from app.detection import detect_image, get_mask, load_model

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    app.state.model = load_model()


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


@app.post("/auto")
def carve(request: Request, file: str = Form(...), name: str = Form(...)):

    if not file.startswith("http"):
        _, imgstr = file.split(";base64,")
        nparr = np.fromstring(base64.b64decode(imgstr), np.uint8)
        img = cv.imdecode(nparr, cv.IMREAD_COLOR)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img = Image.fromarray(img)

    else:
        response = requests.get(file)
        img = Image.open(io.BytesIO(response.content))

    if img.size[1] > 1000:
        ratio = img.size[1] / 1000
        new_width = int(img.size[0] / ratio)

        cv_image = cv.resize(
            np.array(img), (new_width, 1000), interpolation=cv.INTER_AREA
        )
        img = Image.fromarray(cv_image)
    start = time.time()
    detections = detect_image(img, request.app.state.model)
    
    img = np.asarray(img)
    mask = get_mask(img, detections=detections)
    s1 = time.time()
    print(f"Took {s1 - start} to detect")

    src_h, src_w, _ = img.shape
    dst = seam_carving.resize(
        img,
        (src_h, src_h),
        energy_mode="forward",  # Choose from {backward, forward}
        order="width-first",  # Choose from {width-first, height-first}
        keep_mask=mask[:, :, 0],
    )
    print(f"Took {time.time() - s1} to process")
    output = Image.fromarray(dst)

    buff = io.BytesIO()
    output.save(buff, format="JPEG")
    imgstr_ = base64.b64encode(buff.getvalue()).decode("utf-8")
    return {"name": name, "dataURL": f"data:image/jpeg;base64,{imgstr_}"}
