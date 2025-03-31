import cv2
import numpy as np
import subprocess
import shlex
import threading
import time
from queue import Queue, Empty
import triangulation as tri
import calibration
import mediapipe as mp
import serial

ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=0.1)

mp_hands = mp.solutions.hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

frame_rate = 5  # FPS
B = 5.5      # 카메라 간 거리 [cm]
f = 3.51     # 초점 거리 [mm]
alpha = 54   # 카메라 시야각 [도]

ema_x, ema_y, ema_depth = None, None, None
ema_alpha = 0.5
ema_delta = 0.5

def capture_stream(camera_id, buffer_queue):
    cmd = f'libcamera-vid --inline --nopreview -t 0 --codec mjpeg --flush --width 960 --height 960 --framerate {frame_rate} -o - --camera {camera_id}'
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=4096)
    buffer = b""
    
    try:
        while process.poll() is None:
            buffer += process.stdout.read(4096)
            a = buffer.find(b'\xff\xd8')
            b = buffer.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = buffer[a:b+2]
                buffer = buffer[b+2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is not None:
                    frame = cv2.rotate(frame, cv2.ROTATE_180)
                    timestamp = time.time()
                    if not buffer_queue.full():
                        buffer_queue.put((timestamp, frame))
    finally:
        process.terminate()

def get_closest_frames(queue0, queue1):
    try:
        t0, frame0 = queue0.get_nowait()
        candidates = []
        while not queue1.empty():
            t1, frame1 = queue1.get()
            candidates.append((t1, frame1))
            if t1 >= t0:
                break
        
        if not candidates:
            return None, None
        
        t1, frame1 = min(candidates, key=lambda x: abs(x[0] - t0))
        return frame0, frame1
    except Empty:
        return None, None

if __name__ == "__main__":
    buffer_queue0 = Queue(maxsize=5)
    buffer_queue1 = Queue(maxsize=5)

    thread0 = threading.Thread(target=capture_stream, args=(0, buffer_queue0), daemon=True)
    thread1 = threading.Thread(target=capture_stream, args=(1, buffer_queue1), daemon=True)
    thread0.start()
    thread1.start()

    last_data = None  

    while True:
        frame_left, frame_right = get_closest_frames(buffer_queue0, buffer_queue1)
        if frame_left is None or frame_right is None:
            continue

        frame_right, frame_left = calibration.undistortRectify(frame_right, frame_left)
        frame_right_rgb = cv2.cvtColor(frame_right, cv2.COLOR_BGR2RGB)
        frame_left_rgb = cv2.cvtColor(frame_left, cv2.COLOR_BGR2RGB)

        results_right = mp_hands.process(frame_right_rgb)
        results_left = mp_hands.process(frame_left_rgb)

        palm_right = palm_left = None

        if results_right.multi_hand_landmarks:
            h, w, _ = frame_right.shape
            palm_right = np.array([int(results_right.multi_hand_landmarks[0].landmark[9].x * w),
                                    int(results_right.multi_hand_landmarks[0].landmark[9].y * h)])
            
            cv2.circle(frame_right, tuple(palm_right), 10, (0, 255, 0), -1) 

        if results_left.multi_hand_landmarks:
            h, w, _ = frame_left.shape
            palm_left = np.array([int(results_left.multi_hand_landmarks[0].landmark[9].x * w),
                                   int(results_left.multi_hand_landmarks[0].landmark[9].y * h)])
            
            cv2.circle(frame_left, tuple(palm_left), 10, (0, 255, 0), -1) 

        if palm_right is not None and palm_left is not None:
            avg_x = (palm_right[0] + palm_left[0]) // 2
            avg_y = (palm_right[1] + palm_left[1]) // 2
            depth = tri.find_depth(palm_right, palm_left, frame_right, frame_left, B, f, alpha)

            if ema_x is None:
                ema_depth = depth
                ema_x = avg_x
                ema_y = avg_y
            else:
                ema_x = ema_alpha * avg_x + (1 - ema_alpha) * ema_x
                ema_y = ema_alpha * avg_y + (1 - ema_alpha) * ema_y
                ema_depth = ema_delta * depth + (1 - ema_delta) * ema_depth

            data = f"{int(avg_x)},{int(avg_y)},{round(ema_depth, 1) * 10}\n"

            if data != last_data:
                last_data = data
                if ser.is_open:
                    ser.write(data.encode()) 
                    print(f"Sent: {data}")  

            cv2.putText(frame_right, f"Depth: {round(ema_depth, 1)} cm", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            cv2.putText(frame_left, f"Depth: {round(ema_depth, 1)} cm", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        else:
            cv2.putText(frame_right, "TRACKING LOST", (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame_left, "TRACKING LOST", (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        combined_frame = cv2.hconcat([frame_left, frame_right])
        cv2.imshow("Stereo View", cv2.resize(combined_frame, (960, 480), interpolation=cv2.INTER_LINEAR))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    ser.close() 
