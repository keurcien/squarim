import io
import base64
import cv2 as cv
import numpy as np
import requests
from PIL import Image
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def stretch_horizontally(img, parameter=50):

    height, width, _ = img.shape

    if height > width:
        padding = (height - width) // 2
        blur_radius = 10
        right = parameter
        left = parameter
        # right = int(0.01 * width)
        # left = int(0.01 * width)

        left_part = img[:, 0:left, :]
        left_width = padding + left

        right_part = img[:, -right:, :]
        right_width = height - width - padding + right

        center_part = img[:, left:-right:, :]

        left_img = cv.resize(left_part, (left_width, height),
                             interpolation=cv.INTER_AREA)
        right_img = cv.resize(
            right_part, (right_width, height), interpolation=cv.INTER_AREA
        )

        res = np.concatenate((left_img, center_part, right_img), axis=1)
        res[:, padding: (padding + 2 * left), :] = cv.blur(
            res[:, padding: (padding + 2 * left),
                :], (blur_radius, blur_radius)
        )
        res[:, -(right_width + right): -(right_width - right), :] = cv.blur(
            res[:, -(right_width + right): -(right_width - right),
                :], (blur_radius, blur_radius)
        )
        return Image.fromarray(res)
    else:
        return Image.fromarray(img)


@app.post("/")
def index(file: str = Form(...), name: str = Form(...), parameter: int = Form(...)):
    try:

        if not file.startswith("http"):
            format, imgstr = file.split(';base64,')
            nparr = np.fromstring(base64.b64decode(imgstr), np.uint8)
            img = cv.imdecode(nparr, cv.IMREAD_COLOR)
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        else:
            response = requests.get(file)
            img = Image.open(io.BytesIO(response.content))
            img = np.asarray(img)

        img_ = stretch_horizontally(img, parameter=parameter)

        buff = io.BytesIO()
        img_.save(buff, format="JPEG")
        imgstr_ = base64.b64encode(buff.getvalue()).decode("utf-8")
        return {
            "name": name,
            "dataURL": f"data:image/jpeg;base64,{imgstr_}"
        }

    except:
        raise HTTPException(
            status_code=500,
            detail=f"Could not process {name}."
        )
