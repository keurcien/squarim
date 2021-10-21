import io
import os
import zipfile

import cv2 as cv
import numpy as np
from flask import Flask, render_template, request, send_file, redirect, url_for
from flask.helpers import send_file
from PIL import Image
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/temp"


def expand_horizontally(img):
    height, width, _ = img.shape
    padding = (height - width) // 2
    img_ = cv.copyMakeBorder(
        img, 0, 0, padding, height - width - padding, cv.BORDER_REPLICATE
    )
    return Image.fromarray(img_)


def stretch_horizontally(img, left=50, right=50):
    height, width, _ = img.shape
    padding = (height - width) // 2

    left_part = img[:, 0:left, :]
    left_width = padding + left

    right_part = img[:, -right:, :]
    right_width = height - width - padding + right

    center_part = img[:, left:-right:, :]

    left_img = cv.resize(left_part, (left_width, height),
                         interpolation=cv.INTER_AREA)
    right_img = cv.resize(right_part, (right_width, height),
                          interpolation=cv.INTER_AREA)

    res = np.concatenate((left_img, center_part, right_img), axis=1)
    res[:, padding:(padding+2 * left), :] = cv.blur(res[:,
                                                        padding:(padding+2 * left), :], (30, 30))
    res[:, -(right_width+right):-(right_width-right), :] = cv.blur(res[:,  -
                                                                       (right_width+right):-(right_width-right), :], (30, 30))
    return Image.fromarray(res)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<filename>")
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename=filename), code=301)


@app.route("/", methods=["POST"])
def upload_images():
    # if len(files) == 1 do not zip

    print(request.form)
    if request.form["action"] == "Lancer le traitement":
        processed_images = []
        if request.files.getlist("file"):
            for uploaded_image in request.files.getlist("file"):
                try:
                    img = Image.open(uploaded_image)
                    img = np.array(img)
                    # replicate = expand_horizontally(img)
                    replicate = stretch_horizontally(img)
                    replicate.save(
                        f"app/{app.config['UPLOAD_FOLDER']}/{uploaded_image.filename}")
                    processed_images.append(
                        f"{app.config['UPLOAD_FOLDER']}/{uploaded_image.filename}")
                except:
                    print(f"Could not process {uploaded_image.filename}")

            return render_template("index.html", images=processed_images)

    if request.form["action"] == "Download":
        with zipfile.ZipFile("app/static/squarim.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir('app/static/temp'):
                zipf.write(f"app/{app.config['UPLOAD_FOLDER']}/{file}", file)
                os.remove(f"app/{app.config['UPLOAD_FOLDER']}/{file}")

        return_data = io.BytesIO()
        with open("app/static/squarim.zip", "rb") as fh:
            return_data.write(fh.read())
        return_data.seek(0)

        os.remove("app/static/squarim.zip")
        return send_file(
            return_data,
            mimetype="zip",
            attachment_filename="squarim.zip",
            as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
