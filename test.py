#!/usr/bin/env python

from PIL import Image
import pycozmo
#Import necessary libraries
from flask import Flask, render_template, Response
import io



# Last image, received from the robot.
last_im = None


def on_camera_image(cli, new_im):
    """ Handle new images, coming from the robot. """
    global last_im
    last_im = new_im
    


with pycozmo.connect(enable_procedural_face=True) as cli:

    # Raise head.
    angle = (pycozmo.robot.MAX_HEAD_ANGLE.radians - pycozmo.robot.MIN_HEAD_ANGLE.radians) / 2.0
    cli.set_head_angle(angle)

    # Register to receive new camera images.
    cli.add_handler(pycozmo.event.EvtNewRawCameraImage, on_camera_image)

    # Enable camera.
    cli.enable_camera()

    # Run with 14 FPS. This is the frame rate of the robot camera.
    timer = pycozmo.util.FPSTimer(14)

    #Initialize the Flask app
    app = Flask(__name__)

    @app.route('/video_feed')
    def video_feed():
        if last_im:
            im = last_im
            im.convert('1')
            buf = io.BytesIO()
            im.save(buf, format='JPEG')
            byte_im = buf.getvalue()
        return  Response ((b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + byte_im + b'\r\n'), mimetype='multipart/x-mixed-replace; boundary=frame')


    @app.route('/')
    def index():
        return render_template('index.html')



    if __name__ == "__main__":
        app.run(debug=False)


