# Demo 
<iframe width="560" height="315" src="https://www.youtube.com/embed/Eq3Okb1ZOJg" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

![](https://hackmd.io/_uploads/rJZPyNh8n.png)


# System Architecture
![](https://hackmd.io/_uploads/HJBZkE283.png)



## Interacting with the Line Chatbot Server

In `meowdabot.py`, communication with the Line chatbot server is established using the Line Messaging API, and these interactions are facilitated through a Flask web application.

The Flask application in your `meowdabot.py` **listens for incoming HTTP POST requests on the /webhook endpoint.** These requests are sent from the Line server whenever a user sends a message to the chatbot. The Flask server then handles these incoming requests, parses the user's message, and formulates an appropriate response.



## Interacting with the FastAPI Server for Object Detection

In addition to its chatbot capabilities, `meowdabot.py` is also designed **to interact with a separate YOLOv7 model server via the FastAPI interface** to perform object detection.



**When a user sends an image of a cat to the chatbot**, the chatbot sends this image to the YOLOv7 model server for object detection. This is done through a **POST request** to the `/predict` endpoint of the model server's FastAPI application. The request contains the image file that the user sent.



`The YOLOv7 model server` processes the image and returns a response to the chatbot server. The response includes information about the detected objects in the image (which are cats in this case), such as **the class of the object, the confidence score, and the bounding box coordinates.**

Upon receiving the response from the model server, the chatbot server generates a reply for the user. The chatbot can draw the bounding boxes and class labels on the original image and send this image back to the user. This completes the cycle of the user sending an image, the chatbot processing it, and the user receiving the processed image.

In this manner, `meowdabot.py` creates an interactive Line chatbot that can communicate with users and utilize a YOLOv7 object detection model to analyze images sent by users. The use of Flask and FastAPI offers a simple and efficient way to handle interactions between the Line chatbot server, the YOLOv7 model server, and the user.



## Yolov7 infer method
First, the necessary libraries are imported, and the YOLOv7 model is loaded into memory with the trained weights. This model will be used later for the object detection tasks. The list of cat classes is also defined to be used for interpreting the model's predictions.

```app.py
import io
import os
import cv2
import numpy as np
import torch
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from json import dumps

from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import non_max_suppression
from utils.plots import output_to_keypoint, plot_skeleton_kpts

WEIGHTS = "./22cat_best.pt"
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Load YOLOv7
model = attempt_load(WEIGHTS, DEVICE)
```

### Processing Image and Making Predictions
The FastAPI application also includes a route handler for HTTP POST requests to the "/predict" endpoint. This route handler accepts an uploaded image file, processes it, and uses the pre-loaded model to make predictions on the image.

The image processing includes resizing, transforming the image to a format that can be understood by the model, and running the image through the model to generate predictions. Non-max suppression is then used to filter out overlapping predictions.


```app.py
@app.post("/predict", tags=["進行預測"]) 
def yolo(file: UploadFile = File(...)):

    def predict(image, image_size=640):
        # Image processing...
        
        # Infer
        with torch.no_grad():
            pred = model(image_pt[None], augment=False)[0]
        
        # NMS
        pred = non_max_suppression(pred)[0].cpu().numpy()
        
        # Resize boxes to the original image size
        pred[:, [0, 2]] *= ori_w / image_size
        pred[:, [1, 3]] *= ori_h / image_size
        
        return pred

    image = Image.open(io.BytesIO(file.file.read()))
    pred = predict(image)
    return dumps(pred.tolist())
```

The image predictions are then returned to the requester (Line chatbot in this case) as a JSON object containing the prediction results.

This allows meowdabot.py to interact effectively with the Line bot server via Flask and the FastAPI server via the /predict endpoint. This interactive capability enables the Line chatbot to send cat images to the YOLOv7 model server and receive processed images, making it a powerful tool for cat image analysis.