#!/usr/bin/env python

from PIL import Image
import pycozmo
from flask import Flask, render_template, Response
import io
from flask_socketio import SocketIO
import nmcli
global cli

last_im = None

def on_camera_image(cli, new_im):
    """ Handle new images, coming from the robot. """
    global last_im
    last_im = new_im

# def on_robot_state(cli, pkt: pycozmo.protocol_encoder.RobotState):
#     print("Battery level: {:.01f} V".format(pkt.battery_voltage))

# def on_robot_charging(cli, state: bool):
#     if state:
#         print("Started charging.")
#     else:
#         print("Stopped charging.")


ssid_Cozmo = 'Cozmo_76517D' # add the Cozmo number
pw_Cozmo = '1P28RTTFWYR8' # put Cozmo WIFI password with the dashes "-" ! 
if_name = 'wlp2s0' # put your wifi interface name (like wlan0)

def wifi_connect():
    # nmcli.device.disconnect(ifname=if_name)
    nmcli.device.wifi_connect(ssid=ssid_Cozmo,
                            password=pw_Cozmo,
                            ifname=if_name)

def gen():
    global byte_im
    while True:
        im = last_im
        im.convert('1')
        buf = io.BytesIO()
        im.save(buf, format='JPEG')
        byte_im = buf.getvalue()
        timer.sleep()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + byte_im + b'\r\n')

try: 
    wifi_connect()
except:
    print('could not connect to robot wifi')
else: 




    with pycozmo.connect(enable_procedural_face=True) as cli:
        
        import events
        # Raise head.
        angle = (pycozmo.robot.MAX_HEAD_ANGLE.radians - pycozmo.robot.MIN_HEAD_ANGLE.radians) / 2.0
        cli.set_head_angle(angle)
        # Register to receive new camera images.
        cli.add_handler(pycozmo.event.EvtNewRawCameraImage, on_camera_image)
        # cli.add_handler(pycozmo.protocol_encoder.RobotState, on_robot_state, one_shot=True)
        # cli.add_handler(pycozmo.event.EvtRobotChargingChange, on_robot_charging)
        # Enable camera.
        cli.enable_camera()
        # Run with 14 FPS. This is the frame rate of the robot camera.
        timer = pycozmo.util.FPSTimer(14)
        #Initialize the Flask app
        app = Flask(__name__)
        socketio = SocketIO(app,cors_allowed_origins="*")

        @app.route('/video_feed')
        def video_feed():
            return Response(gen(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @app.route('/')
        def index():
            return render_template('index.html')
        
        @socketio.on("update")
        def update(data):
            print('current value', data['value'])


        if __name__ == "__main__":
            app.run(debug=False)




    