import io
import os
import time
import threading
from datetime import datetime
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, MJPEGEncoder
from picamera2.outputs import FileOutput, CircularOutput

RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class Camera:
    def __init__(self):
        self.picam2 = Picamera2()
        self.streaming_output = StreamingOutput()
        self.recording = False
        self.record_file = None
        self._lock = threading.Lock()
        self._setup()

    def _setup(self):
        video_config = self.picam2.create_video_configuration(
            main={"size": (1280, 720), "format": "RGB888"},
            lores={"size": (640, 360), "format": "YUV420"},
            encode="lores",
        )
        self.picam2.configure(video_config)
        self.mjpeg_encoder = MJPEGEncoder()
        self.mjpeg_encoder.output = FileOutput(self.streaming_output)
        self.picam2.start_encoder(self.mjpeg_encoder, name="lores")
        self.picam2.start()

    def get_frame(self):
        with self.streaming_output.condition:
            self.streaming_output.condition.wait(timeout=5)
            return self.streaming_output.frame

    def start_recording(self):
        with self._lock:
            if self.recording:
                return None
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(RECORDINGS_DIR, f"video_{timestamp}.h264")
            self.h264_encoder = H264Encoder(bitrate=4000000)
            self.h264_encoder.output = FileOutput(filename)
            self.picam2.start_encoder(self.h264_encoder, name="main")
            self.recording = True
            self.record_file = filename
            return filename

    def stop_recording(self):
        with self._lock:
            if not self.recording:
                return None
            self.picam2.stop_encoder(self.h264_encoder)
            self.recording = False
            saved = self.record_file
            self.record_file = None
            return saved

    def capture_photo(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(RECORDINGS_DIR, f"photo_{timestamp}.jpg")
        self.picam2.capture_file(filename)
        return filename

    def get_recordings(self):
        files = []
        for f in sorted(os.listdir(RECORDINGS_DIR), reverse=True):
            full = os.path.join(RECORDINGS_DIR, f)
            stat = os.stat(full)
            files.append({
                "name": f,
                "size": round(stat.st_size / 1024 / 1024, 2),
                "date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            })
        return files

    def close(self):
        if self.recording:
            self.stop_recording()
        self.picam2.stop()
