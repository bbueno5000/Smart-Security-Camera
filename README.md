# Smart-Security-Camera

Security webcam running open-cv for object detection. The camera will send an email with an image of any objects it detects. It also runs a server that provides a live video stream over the internet.

## Customization

To get emails when objects are detected, you'll need to make a couple modifications to the `mail.py` file.

Open `mail.py` with vim `vim mail.py`, then press `i` to edit. Scroll down to the following section

```
# Email you want to send the update from (only works with gmail)
fromEmail = 'myemail@gmail.com'
fromEmailPassword = 'password1234'

# Email you want to send the update to
toEmail = 'anotheremail@gmail.com'
```
and replace with your own email/credentials. The `mail.py` file logs into a gmail SMTP server and sends an email with an image of the object detected by the security camera. 

Press `esc` then `ZZ` to save and exit.

You can also modify the `main.py` file to change some other properties.

```
email_update_interval = 600 # sends an email only once in this time interval
video_camera = VideoCamera(flip=True) # creates a camera object, flip vertically
object_classifier = cv2.CascadeClassifier("models/fullbody_recognition_model.xml") # an opencv classifier
```
Notably, you can use a different object detector by changing the path `"models/fullbody_recognition_model.xml"` in `object_classifier = cv2.CascadeClassifier("models/fullbody_recognition_model.xml")`.

to a new model in the models directory.

```
facial_recognition_model.xml
fullbody_recognition_model.xml
upperbody_recognition_model.xml
```

## Running the Program

Run the program

```
python main.py
```

You can view a live stream by visiting the ip address of your pi in a browser on the same network. You can find the ip address of your Raspberry Pi by typing `ifconfig` in the terminal and looking for the `inet` address. 
