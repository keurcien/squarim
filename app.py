from flask import Flask, render_template, send_file, request, redirect, url_for
from PIL import Image
from flask.helpers import send_file
import numpy as np
import cv2 as cv
import io

app = Flask(__name__)


def expand_horizontally(img):
    height, width, _ = img.shape
    padding = (height - width) // 2
    img_ = cv.copyMakeBorder(
        img, 0, 0, padding, height - width - padding, cv.BORDER_REPLICATE)
    return Image.fromarray(img_)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def upload_images():

    uploaded_image = request.files["file"]
    img = Image.open(uploaded_image)
    img = np.array(img)

    replicate = expand_horizontally(img)
    img_ = io.BytesIO()
    replicate.save(img_, format="png")
    img_.seek(0)

    return send_file(
        img_,
        mimetype="image/png",
        attachment_filename=f"{uploaded_image.filename}_squarim.jpg",
        as_attachment=True
    )
