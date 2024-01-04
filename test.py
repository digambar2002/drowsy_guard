import base64
import os

import cv2
import dlib
import imutils
import numpy as np
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from scipy.spatial import distance
from imutils import face_utils

app = Flask(__name__, static_folder="./templates/static")
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("models/models/shape_predictor_68_face_landmarks.dat")
thresh = 0.25
frame_check = 30
flag  = 0
setAlert = False
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]

def base64_to_image(base64_string):
    # Extract the base64 encoded binary data from the input string
    base64_data = base64_string.split(",")[1]
    # Decode the base64 data to bytes
    image_bytes = base64.b64decode(base64_data)
    # Convert the bytes to a numpy array
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    # Decode the numpy array as an image using OpenCV
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image

def detect_drowsiness(shape):
    # Example: Calculate the eye aspect ratio (EAR)

    global flag
    global setAlert
    global state
    shape = face_utils.shape_to_np(shape)
    left_eye = shape[lStart:lEnd]
    right_eye = shape[rStart:rEnd]

    leftEyeHull = cv2.convexHull(left_eye)
    rightEyeHull = cv2.convexHull(right_eye)

    left_ear = eye_aspect_ratio(left_eye)
    right_ear = eye_aspect_ratio(right_eye)


    ear = (left_ear + right_ear) / 2.0

    if ear < thresh:
        flag += 1
        print (flag)
        if flag >= frame_check:
            print('drowsi')
            socketio.emit('alert', '1')
            setAlert = True
    else:
        flag = 0
        if setAlert == True:
            print('not drowsi')
            socketio.emit('alert', '0')
            setAlert = False

    # Your drowsiness detection logic here
    # Example: if left_ear < threshold and right_ear < threshold, then drowsy

    return left_ear, right_ear, leftEyeHull, rightEyeHull

def eye_aspect_ratio(eye):
	A = distance.euclidean(eye[1], eye[5])
	B = distance.euclidean(eye[2], eye[4])
	C = distance.euclidean(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	return ear

@socketio.on("connect")
def test_connect():
    print("Connected")
    emit("my response", {"data": "Connected"})
    

@socketio.on("image")
def receive_image(image):

    # Decode the base64-encoded image data
    image = base64_to_image(image)
    image = imutils.resize(image, width=1080)
    # Perform face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    for rect in rects:
        shape = predictor(gray, rect)
        landmarks = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

        # Drowsiness detection
        left_ear, right_ear, leftEyeHull, rightEyeHull = detect_drowsiness(shape)
        
        # Display landmarks and drowsiness status (for testing)
        cv2.putText(image, f"Left EAR: {left_ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(image, f"Right EAR: {right_ear:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.drawContours(image, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(image, [rightEyeHull], -1, (0, 255, 0), 1)

        # for (x, y) in landmarks:
        #     cv2.circle(image, (x, y), 1, (0, 0, 255), -1)

    # Continue with your existing image processing code...

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, frame_encoded = cv2.imencode(".jpg", image, encode_param)

    processed_img_data = base64.b64encode(frame_encoded).decode()

    b64_src = "data:image/jpg;base64,"
    processed_img_data = b64_src + processed_img_data

    emit("processed_image", processed_img_data)
    
    # print(state)

@app.route("/")
def index():
    return render_template("test.html")

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000, host="192.168.1.224", ssl_context=('cert.pem', 'key.pem'))
