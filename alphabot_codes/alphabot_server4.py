"""
alphabot_server.py — AlphaBot Command Server + Pi Camera Streaming
Gira sul Raspberry Pi 3.

Installazione sul Pi:
    pip install flask RPi.GPIO
    sudo apt install -y python3-opencv   # oppure: pip install opencv-python-headless
    # Per il QR code lato client (non serve sul server):
    #   pip install pyzbar  +  sudo apt install libzbar0

Avvio:
    python3 alphabot_server.py --port 5000

    # Se la camera non è /dev/video0, specifica l'indice:
    python3 alphabot_server.py --port 5000 --cam 1

    # Per vedere le device disponibili:
    ls /dev/video*

    # Per ridurre il lag dello stream (qualità JPEG, default 70):
    python3 alphabot_server.py --port 5000 --quality 60

Endpoints:
  GET  /ping    → stato server + disponibilità camera
  POST /command → invia comando motori  {action, speed}
  GET  /stop    → stop emergenza
  GET  /stato   → stato corrente robot
  GET  /stream  → MJPEG stream Pi Camera (apribile anche nel browser)

NOTE sul riconoscimento QR:
  Il client decodifica i QR code direttamente sui frame ricevuti dallo stream.
  Il server non deve fare nulla di speciale: basta che /stream funzioni correttamente.
  Per migliorare il riconoscimento QR assicurarsi che la risoluzione sia >= 640x480
  e la qualità JPEG >= 65 (valori inferiori degradano i QR code).
"""

import time
import argparse
import logging
import threading
from threading import Timer, Lock
from flask import Flask, request, jsonify, Response

# ─── GPIO ──────────────────────────────────────────────────────────────────────
try:
    import RPi.GPIO as GPIO
    ON_PI = True
except (ImportError, RuntimeError):
    ON_PI = False
    print("[WARN] RPi.GPIO non trovato — modalità simulazione attiva")

    class _MockGPIO:
        BCM = OUT = HIGH = LOW = 0
        def setmode(self, *a):    pass
        def setup(self, *a, **k): pass
        def output(self, *a):     pass
        def cleanup(self):        pass
        class PWM:
            def __init__(self, p, f): pass
            def start(self, dc):      pass
            def ChangeDutyCycle(self, dc): pass
            def stop(self):           pass
    GPIO = _MockGPIO()

# ─── OpenCV (per webcam USB) ───────────────────────────────────────────────────
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("[WARN] opencv non trovato — streaming disabilitato")
    print("       Installa con: sudo apt install python3-opencv")

# ─── Pin GPIO (BCM) ────────────────────────────────────────────────────────────

AIN1 = 12; AIN2 = 13; PWMA = 6
BIN1 = 20; BIN2 = 21; PWMB = 26

# ─── Streaming webcam USB ─────────────────────────────────────────────────────

class WebcamStreamer:
    """
    Cattura frame da una webcam USB tramite OpenCV,
    sovrappone la freccia di direzione e li serve come MJPEG stream HTTP.
    """

    ACTION_COLOR = {
        "avanti":   (0,  220, 100),
        "indietro": (60, 100, 220),
        "sinistra": (220, 200,  0),
        "destra":   (0,  190, 220),
        "stop":     (100, 100, 100),
    }

    def __init__(self, cam_index=0, width=640, height=480, fps=30, quality=70):
        """
        quality: 65-80 è il range ideale — buona qualità per il QR decoder,
                 stream fluido senza saturare la rete Wi-Fi del Pi.
        """
        self._cam_index = cam_index
        self._width     = width
        self._height    = height
        self._fps       = fps
        self._quality   = quality
        self._frame     = None
        self._lock      = Lock()
        self._running   = False
        self._action    = "stop"
        self._thread    = None

    def start(self):
        if not HAS_CV2:
            logger.warning("OpenCV non disponibile — stream disabilitato")
            return
        self._running = True
        self._thread  = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.info(f"Webcam stream avviato (indice={self._cam_index}, "
                    f"{self._width}x{self._height} @{self._fps}fps)")

    def stop(self):
        self._running = False

    def set_action(self, action: str):
        self._action = action

    # ── Loop di cattura ───────────────────────────────────────────────────────

    def _capture_loop(self):
        cap = cv2.VideoCapture(self._cam_index)
        if not cap.isOpened():
            logger.error(f"Impossibile aprire webcam {self._cam_index}. "
                         f"Prova --cam 1 o controlla 'ls /dev/video*'")
            self._running = False
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self._width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        cap.set(cv2.CAP_PROP_FPS,          self._fps)
        cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)   # buffer minimo = latenza minima

        logger.info(f"Webcam aperta: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x"
                    f"{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))} "
                    f"@{int(cap.get(cv2.CAP_PROP_FPS))}fps")

        while self._running:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Lettura webcam fallita — riprovo...")
                time.sleep(0.1)
                continue

            # Sovrapponi freccia e info
            self._draw_overlay(frame)

            # Comprimi in JPEG
            ok, buf = cv2.imencode(
                ".jpg", frame,
                [cv2.IMWRITE_JPEG_QUALITY, self._quality])
            if ok:
                with self._lock:
                    self._frame = buf.tobytes()

        cap.release()
        logger.info("Webcam rilasciata.")

    # ── Overlay direzione ─────────────────────────────────────────────────────

    def _draw_overlay(self, frame):
        h, w   = frame.shape[:2]
        action = self._action
        color  = self.ACTION_COLOR.get(action, (200, 200, 200))
        cx, cy = w // 2, h // 2
        s      = min(w, h) // 5   # dimensione freccia proporzionale al frame

        if action == "avanti":
            cv2.arrowedLine(frame, (cx, cy+s), (cx, cy-s), color, 6, tipLength=0.3)
        elif action == "indietro":
            cv2.arrowedLine(frame, (cx, cy-s), (cx, cy+s), color, 6, tipLength=0.3)
        elif action == "sinistra":
            cv2.arrowedLine(frame, (cx+s, cy), (cx-s, cy), color, 6, tipLength=0.3)
        elif action == "destra":
            cv2.arrowedLine(frame, (cx-s, cy), (cx+s, cy), color, 6, tipLength=0.3)
        elif action == "stop":
            cv2.circle(frame, (cx, cy), s-10, color, 4)
            cv2.line(frame, (cx-s//2, cy-s//2), (cx+s//2, cy+s//2), color, 4)
            cv2.line(frame, (cx+s//2, cy-s//2), (cx-s//2, cy+s//2), color, 4)

        # Label comando in alto a sinistra
        cv2.rectangle(frame, (0, 0), (230, 38), (0, 0, 0), -1)
        cv2.putText(frame, f"CMD: {action.upper()}", (8, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)

        # Timestamp in basso a destra
        ts = time.strftime("%H:%M:%S")
        cv2.putText(frame, ts, (w-80, h-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (130,130,130), 1, cv2.LINE_AA)

    # ── MJPEG generator per Flask ─────────────────────────────────────────────

    def get_frame(self):
        with self._lock:
            return self._frame

    def mjpeg_generator(self):
        """
        Genera frames MJPEG il più velocemente possibile.
        Non usa sleep fisso: aspetta solo il tempo necessario per avere
        un frame nuovo, riducendo la latenza al minimo.
        """
        last_frame = None
        min_delay  = 1.0 / (self._fps * 2)   # polling massimo al doppio degli fps
        while True:
            frame = self.get_frame()
            if frame and frame is not last_frame:
                last_frame = frame
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n"
                       b"Content-Length: " + str(len(frame)).encode() + b"\r\n"
                       b"\r\n" + frame + b"\r\n")
            else:
                time.sleep(min_delay)

    @property
    def is_active(self) -> bool:
        return self._running and self._frame is not None


# ─── Driver motori ─────────────────────────────────────────────────────────────

class AlphaBot:
    def __init__(self, pwm_freq=500):
        GPIO.setmode(GPIO.BCM)
        for pin in (AIN1, AIN2, PWMA, BIN1, BIN2, PWMB):
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        self._pwm_a = GPIO.PWM(PWMA, pwm_freq)
        self._pwm_b = GPIO.PWM(PWMB, pwm_freq)
        self._pwm_a.start(0)
        self._pwm_b.start(0)
        self._stato           = "stop"
        self._watchdog_sec    = 1.0
        self._watchdog: Timer = None
        self._avvia_watchdog()

    def _motore_sx(self, speed, avanti):
        dc = min(100, speed * 100 // 255)
        GPIO.output(AIN1, GPIO.HIGH if avanti else GPIO.LOW)
        GPIO.output(AIN2, GPIO.LOW  if avanti else GPIO.HIGH)
        self._pwm_a.ChangeDutyCycle(dc)

    def _motore_dx(self, speed, avanti):
        dc = min(100, speed * 100 // 255)
        GPIO.output(BIN1, GPIO.HIGH if avanti else GPIO.LOW)
        GPIO.output(BIN2, GPIO.LOW  if avanti else GPIO.HIGH)
        self._pwm_b.ChangeDutyCycle(dc)

    def stop(self):
        self._pwm_a.ChangeDutyCycle(0)
        self._pwm_b.ChangeDutyCycle(0)
        for pin in (AIN1, AIN2, BIN1, BIN2):
            GPIO.output(pin, GPIO.LOW)
        self._stato = "stop"

    def avanti(self, speed=180):
        self._motore_sx(speed, False); self._motore_dx(speed, False)
        self._stato = "avanti"

    def indietro(self, speed=180):
        self._motore_sx(speed, True); self._motore_dx(speed, True)
        self._stato = "indietro"

    def sinistra(self, speed=160):
        self._motore_sx(speed, True); self._motore_dx(speed, False)
        self._stato = "sinistra"

    def destra(self, speed=160):
        self._motore_sx(speed, False); self._motore_dx(speed, True)
        self._stato = "destra"

    def esegui(self, azione, speed):
        self._avvia_watchdog()
        azione = azione.lower()
        if   azione == "avanti":   self.sinistra(speed)
        elif azione == "indietro": self.destra(speed)
        elif azione == "sinistra": self.avanti(speed)
        elif azione == "destra":   self.indietro(speed)
        else:                      self.stop()
        if camera:
            camera.set_action(azione)

    def _avvia_watchdog(self):
        if self._watchdog:
            self._watchdog.cancel()
        self._watchdog = Timer(self._watchdog_sec, self._watchdog_scattato)
        self._watchdog.daemon = True
        self._watchdog.start()

    def _watchdog_scattato(self):
        logger.warning("[WATCHDOG] Nessun comando — robot fermato")
        self.stop()
        if camera:
            camera.set_action("stop")

    def cleanup(self):
        self.stop()
        if self._watchdog:
            self._watchdog.cancel()
        self._pwm_a.stop()
        self._pwm_b.stop()
        GPIO.cleanup()


# ─── Flask ────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)s  %(message)s")
logger = logging.getLogger("alphabot")

app    = Flask(__name__)
robot:  AlphaBot       = None
camera: WebcamStreamer = None

AZIONI_VALIDE = {"avanti", "indietro", "sinistra", "destra", "stop"}


@app.route("/ping")
def ping():
    return jsonify({
        "status": "ok",
        "on_pi":  ON_PI,
        "camera": HAS_CV2 and camera is not None and camera.is_active,
    })


@app.route("/command", methods=["POST"])
def command():
    data   = request.get_json(silent=True)
    if not data:
        return jsonify({"errore": "Nessun JSON"}), 400
    azione = str(data.get("action", "stop")).lower()
    speed  = max(0, min(255, int(data.get("speed", 180))))
    if azione not in AZIONI_VALIDE:
        return jsonify({"errore": f"Azione '{azione}' non valida"}), 400
    logger.info(f"► {azione.upper():<10}  vel={speed}")
    robot.esegui(azione, speed)
    return jsonify({"status": "ok", "azione": azione})


@app.route("/stop")
def emergency_stop():
    robot.stop()
    if camera:
        camera.set_action("stop")
    logger.info("⚠ STOP EMERGENZA")
    return jsonify({"status": "fermato"})


@app.route("/stato")
def stato():
    return jsonify({"azione_corrente": robot._stato, "on_pi": ON_PI})


@app.route("/stream")
def stream():
    """MJPEG stream della camera. Apribile anche nel browser."""
    if not HAS_CV2 or camera is None:
        return jsonify({"errore": "Camera non disponibile"}), 503
    resp = Response(
        camera.mjpeg_generator(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"]        = "no-cache"
    resp.headers["Expires"]       = "0"
    return resp


# ─── Avvio ────────────────────────────────────────────────────────────────────

def main():
    global robot, camera
    parser = argparse.ArgumentParser(description="AlphaBot Server")
    parser.add_argument("--port",    default=5000, type=int)
    parser.add_argument("--host",    default="0.0.0.0")
    parser.add_argument("--cam",     default=0,    type=int,
                        help="Indice webcam USB (default 0). Vedi: ls /dev/video*")
    parser.add_argument("--cam-w",   default=640,  type=int)
    parser.add_argument("--cam-h",   default=480,  type=int)
    parser.add_argument("--cam-fps", default=30,   type=int)
    parser.add_argument("--quality", default=70,   type=int,
                        help="Qualità JPEG stream 1-100 (default 70). "
                             "Min 65 per QR code leggibili, max 85 per non saturare il Wi-Fi.")
    parser.add_argument("--no-cam",  action="store_true",
                        help="Disabilita streaming camera")
    args = parser.parse_args()

    robot = AlphaBot()

    if not args.no_cam:
        camera = WebcamStreamer(
            cam_index=args.cam,
            width=args.cam_w,
            height=args.cam_h,
            fps=args.cam_fps,
            quality=args.quality,
        )
        camera.start()

    ip = "IP_DEL_PI"
    logger.info(f"Server AlphaBot su {args.host}:{args.port}")
    if camera:
        logger.info(f"Stream camera:  http://{ip}:{args.port}/stream  "
                    f"(qualità JPEG={args.quality}, {args.cam_w}x{args.cam_h}@{args.cam_fps}fps)")
        logger.info(f"  → QR code: il client li decodifica automaticamente dallo stream")
    logger.info(f"Stop emergenza: http://{ip}:{args.port}/stop")
    logger.info("In attesa di comandi...")

    try:
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        if camera:
            camera.stop()
        robot.cleanup()
        logger.info("Server spento.")


if __name__ == "__main__":
    main()