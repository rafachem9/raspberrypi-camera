import os
from flask import Flask, Response, render_template, jsonify, send_from_directory
from camera import Camera

app = Flask(__name__)
camera = Camera()


def generate_frames():
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stream")
def stream():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/record/start", methods=["POST"])
def record_start():
    filename = camera.start_recording()
    if filename:
        return jsonify({"status": "recording", "file": filename})
    return jsonify({"status": "already_recording"}), 400


@app.route("/record/stop", methods=["POST"])
def record_stop():
    filename = camera.stop_recording()
    if filename:
        return jsonify({"status": "stopped", "file": filename})
    return jsonify({"status": "not_recording"}), 400


@app.route("/photo", methods=["POST"])
def take_photo():
    filename = camera.capture_photo()
    return jsonify({"status": "ok", "file": filename})


@app.route("/recordings")
def list_recordings():
    return jsonify(camera.get_recordings())


@app.route("/recordings/<path:filename>")
def download_recording(filename):
    return send_from_directory("recordings", filename, as_attachment=True)


@app.route("/status")
def status():
    return jsonify({"recording": camera.recording})


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, threaded=True)
    finally:
        camera.close()
