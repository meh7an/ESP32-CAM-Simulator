import imutils
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import time
import cv2

lock = threading.Lock()
app = Flask(__name__)
vs = VideoStream(src=0).start()
time.sleep(3)
opf = None

@app.route("/")
def index():
	return render_template("index.html")

def initiate():
	global vs, opf, lock
	while True:
		frame = vs.read()
		frame = imutils.resize(frame, width=416)
		with lock:
			opf = frame.copy()

def generate():
	global opf, lock

	while True:
		with lock:
			if opf is None:
				continue
			(flag, img) = cv2.imencode(".jpg", opf)

			if not flag:
				continue

		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(img) + b'\r\n')

@app.route("/stream")
def video_feed():
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
	thread = threading.Thread(target=initiate, args=())
	thread.daemon = True
	thread.start()
	app.run(host="127.0.0.1", port=81,
		threaded=True, use_reloader=False)
vs.stop()
