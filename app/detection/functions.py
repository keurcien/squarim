import numpy as np
import torch
from app.detection.models import *
from app.detection.utils import utils
from torch.autograd import Variable
from torchvision import transforms

config_path = "app/detection/config/yolov3.cfg"
weights_path = "app/detection/config/yolov3.weights"
class_path = "app/detection/config/coco.names"
img_size = 416
conf_thres = 0.8
nms_thres = 0.4


# Load model and weights
import time


def load_model():

    s = time.time()

    model = Darknet(config_path, img_size=img_size)
    model.load_weights(weights_path)
    model.to("cpu")
    model.eval()
    print(f"Took {time.time() - s} seconds to load model on startup")

    return model

Tensor = torch.FloatTensor


def detect_image(img, model):
    # scale and pad image
    ratio = min(img_size / img.size[0], img_size / img.size[1])
    imw = round(img.size[0] * ratio)
    imh = round(img.size[1] * ratio)
    img_transforms = transforms.Compose(
        [
            transforms.Resize((imh, imw)),
            transforms.Pad(
                (
                    max(int((imh - imw) / 2), 0),
                    max(int((imw - imh) / 2), 0),
                    max(int((imh - imw) / 2), 0),
                    max(int((imw - imh) / 2), 0),
                ),
                (128, 128, 128),
            ),
            transforms.ToTensor(),
        ]
    )
    # convert image to Tensor
    image_tensor = img_transforms(img).float()
    image_tensor = image_tensor.unsqueeze_(0)
    input_img = Variable(image_tensor.type(Tensor))
    # run inference on the model and get detections
    with torch.no_grad():
        detections = model(input_img)
        detections = utils.non_max_suppression(detections, 80, conf_thres, nms_thres)
    return detections[0]


def get_mask(img, detections):
    pad_x = max(img.shape[0] - img.shape[1], 0) * (img_size / max(img.shape))
    pad_y = max(img.shape[1] - img.shape[0], 0) * (img_size / max(img.shape))
    unpad_h = img_size - pad_y
    unpad_w = img_size - pad_x

    mask = np.zeros(img.shape)

    if detections is not None:
        # browse detections and draw bounding boxes
        for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:
            box_h = ((y2 - y1) / unpad_h) * img.shape[0]
            box_w = ((x2 - x1) / unpad_w) * img.shape[1]
            y1 = ((y1 - pad_y // 2) / unpad_h) * img.shape[0]
            x1 = ((x1 - pad_x // 2) / unpad_w) * img.shape[1]

            x_l = int(x1)
            x_r = int(x1 + box_w)
            y_b = int(y1)
            y_t = int(y1 + box_h)

            mask[y_b:y_t, x_l:x_r, :] = 255
    return mask
