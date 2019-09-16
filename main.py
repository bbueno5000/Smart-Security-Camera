import cv2
import flask
import flask_basicauth
import imutils
import smtplib
import sys
import threading
import time

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = flask.Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'username'
app.config['BASIC_AUTH_PASSWORD'] = 'p@ssw0rd'
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = flask_basicauth.BasicAuth(app)

class Mail:
    """
    You can generate an app password here to avoid storing your password in plain text:
    https://support.google.com/accounts/answer/185833?hl=en
    """

    def __init__(self):
        self.sender_email = 'sender@gmail.com'
        self.sender_password = 'p@ssw0rd'
        self.recepient_email = 'recepient@gmail.com'

    def send_email(self, image):
        msg_root = MIMEMultipart('related')
        msg_root['Subject'] = 'Security Update'
        msg_root['From'] = self.sender_email
        msg_root['To'] = self.recepient_email
        msg_root.preamble = 'Security Camera Update'
        msg_alternative = MIMEMultipart('alternative')
        msg_root.attach(msg_alternative)
        msg_text = MIMEText('Smart security cam found object')
        msg_alternative.attach(msg_text)
        msg_text = MIMEText('<img src="cid:image1">', 'html')
        msg_alternative.attach(msg_text)
        msgImage = MIMEImage(image)
        msgImage.add_header('Content-ID', '<image1>')
        msg_root.attach(msgImage)
        try:
            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com')
            smtp_server.ehlo()
            smtp_server.login(self.sender_email, self.sender_password)
            smtp_server.sendmail(self.sender_email, self.recepient_email, msg_root.as_string())
            smtp_server.close()
            print("email successfully sent")
        except:
            print("email unsuccessfully sent")

class VideoCamera:

    def __init__(self):
        self.video_capture = cv2.VideoCapture(0)

    def __del__(self):
        self.video_capture.release()

    def get_frame(self):
        _, frame = self.video_capture.read()
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def get_object(self, classifier):
        found_objects = False
        _, frame = self.video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        objects = classifier.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
            )
        
        if len(objects) > 0:
            found_objects = True
            # Draw a rectangle around the objects
            for (x, y, w, h) in objects:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        _, jpeg = cv2.imencode('.jpg', frame)
        return (jpeg.tobytes(), found_objects)

email_update_interval = 600 # sends an email only once in this time interval    
object_classifier = cv2.CascadeClassifier("models/facial_recognition_model.xml") # an opencv classifier
video_camera = VideoCamera() 
last_epoch = 0
mail = Mail()

def check_for_objects():
    while True:
        frame, found_obj = video_camera.get_object(object_classifier)
        if found_obj:
            # if (time.time() - last_epoch) > email_update_interval:
            last_epoch = time.time()
            mail.send_email(frame)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
@basic_auth.required
def index():
    return flask.render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return flask.Response(gen(video_camera), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    thread = threading.Thread(target=check_for_objects, args=())
    thread.daemon = True
    thread.start()
    app.run(host='0.0.0.0')
