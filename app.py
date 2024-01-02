from flask import Flask, Response, render_template
from flask_socketio import SocketIO
import cv2

from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2



app = Flask(__name__)

# intialize sockets
socketio = SocketIO(app)


camera = cv2.VideoCapture(0)
streaming = False


def eye_aspect_ratio(eye):
	A = distance.euclidean(eye[1], eye[5])
	B = distance.euclidean(eye[2], eye[4])
	C = distance.euclidean(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	return ear

thresh = 0.25
frame_check = 30
detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("models/models/shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
# cap=cv2.VideoCapture(0)
flag=0

def genrate_frame():
    setAlert = False
    global streaming
    while streaming:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = imutils.resize(frame, width=1080)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            subjects = detect(gray, 0)
            for subject in subjects:
                shape = predict(gray, subject)
                shape = face_utils.shape_to_np(shape)
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                leftEAR = eye_aspect_ratio(leftEye)
                rightEAR = eye_aspect_ratio(rightEye)
                ear = (leftEAR + rightEAR) / 2.0
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
                if ear < thresh:
                    flag += 1
                    print (flag)
                    if flag >= frame_check:
                        cv2.putText(frame, "*************************************************** ALERT! ***************************************************", (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.putText(frame, "*************************************************** ALERT! ***************************************************", (20,325),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        socketio.emit('alert_event', '1')
                        setAlert = True

                else:
                    flag = 0
                    if setAlert == True:
                        socketio.emit('alert_event', '2')
                        setAlert = False

            # cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cv2.destroyAllWindows()
    camera.release() 



               


@app.route("/")
def hello_world():
    global streaming
    camera.release() 
    streaming = False
    return render_template('index.html')

@app.route("/video_stream")
def video_stream():
    return Response(genrate_frame(), mimetype= 'multipart/x-mixed-replace; boundary=frame')
    
@app.route('/start_stream')
def start_stream():
    
    global streaming
    camera.open(0)
    streaming = True
    return render_template('index.html')

@app.route('/stop_stream')
def stop_stream():

    global streaming
    camera.release() 
    streaming = False
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True, host='192.168.163.224')

