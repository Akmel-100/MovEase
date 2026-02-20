"""
gesture_client.py — AlphaBot Hand + Face Gesture Controller
con streaming Pi Camera integrato nella finestra e riconoscimento QR code.

Layout finestra:
  ┌──────────────────────────────┐
  │      Pi Camera live          │
  │  (vista robot + QR overlay)  │
  ├──────────────────────────────┤
  │      HUD / Stato             │
  └──────────────────────────────┘

La webcam locale acquisisce i gesti ma NON viene mostrata.

Installazione:
    pip install opencv-python mediapipe requests pyzbar
    # Su Linux potrebbe servire anche: sudo apt install libzbar0

Avvio:
    python3 gesture_client.py --host <IP_DEL_PI> --port 5000
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

import requests
import urllib.request
import argparse
import threading
import time
import sys
import os
import numpy as np
from typing import Optional, List

# QR code decoder — richiede: pip install pyzbar  (+ libzbar0 su Linux)
try:
    from pyzbar import pyzbar as _pyzbar
    QR_AVAILABLE = True
except ImportError:
    _pyzbar = None
    QR_AVAILABLE = False
    print("[WARN] pyzbar non trovato. QR code disabilitato. "
          "Installa con: pip install pyzbar")

# ─── Configurazione ────────────────────────────────────────────────────────────

DEFAULT_HOST    = "192.168.1.100"
DEFAULT_PORT    = 5000
CAMERA_INDEX    = 0

# ── Velocità lineari ──────────────────────────────────────────────────────────
# Range utile motori AlphaBot: ~40 (appena si muove) … 255 (piena velocità).
# 55 dà un avanzamento lento e controllabile, facile da fermare in tempo.
SPEED_AVANTI    = 80
SPEED_INDIETRO  = 80

# ── Micro-step rotazione ───────────────────────────────────────────────────────
# Velocità bassa + impulsi brevissimi = rotazione "a scatti" precisi.
# STEP_DURATA: quanto dura ogni impulso motore  (secondi)
# STEP_PAUSA:  quanto si ferma tra un impulso e l'altro
# Con 60/0.08/0.12 ogni scatto ruota ~3-5° → massima manovrabilità.
SPEED_ROTAZIONE = 60
STEP_DURATA     = 0.08   # impulso 80 ms
STEP_PAUSA      = 0.12   # pausa  120 ms

YAW_SOGLIA      = 0.15
PITCH_SOGLIA    = 0.055

# Risoluzione webcam per il riconoscimento gesture
# 640×480 garantisce buona qualità per MediaPipe senza eccessivo carico
DETECT_W, DETECT_H = 640, 480

# Quanto spesso scansionare QR dalla Pi Camera (ogni N frame del main loop)
# Valore più alto = meno carico CPU, ma QR rilevati con più ritardo
QR_SCAN_EVERY = 5

HAND_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
)
FACE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
)
SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
HAND_MODEL_PATH = os.path.join(SCRIPT_DIR, "hand_landmarker.task")
FACE_MODEL_PATH = os.path.join(SCRIPT_DIR, "face_landmarker.task")

ACTION_COLOR = {
    "avanti":   (0, 220, 100),
    "indietro": (60, 100, 220),
    "sinistra": (220, 200, 0),
    "destra":   (0, 190, 220),
    "stop":     (100, 100, 100),
}

MODI = ["mano", "viso", "entrambi"]


# ─── Download modelli ─────────────────────────────────────────────────────────

def _download(url, path, nome):
    if not os.path.exists(path):
        print(f"[INFO] Download {nome} (~25-30 MB)...")
        try:
            urllib.request.urlretrieve(url, path)
            print(f"[INFO] Salvato: {path}")
        except Exception as e:
            print(f"[ERRORE] Download {nome} fallito: {e}")
            sys.exit(1)

def ensure_models(mode):
    if mode in ("mano",  "entrambi"): _download(HAND_MODEL_URL, HAND_MODEL_PATH, "hand_landmarker")
    if mode in ("viso",  "entrambi"): _download(FACE_MODEL_URL, FACE_MODEL_PATH, "face_landmarker")


# ─── Riconoscimento MANO ──────────────────────────────────────────────────────

class HandRecogniser:
    CONNECTIONS = [
        (0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20),(5,9),(9,13),(13,17),
    ]

    def __init__(self):
        opts = mp_vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=HAND_MODEL_PATH),
            running_mode=mp_vision.RunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=0.70,
            min_hand_presence_confidence=0.70,
            min_tracking_confidence=0.60,
        )
        self._det    = mp_vision.HandLandmarker.create_from_options(opts)
        self._result = None

    def detect(self, bgr_frame) -> Optional[str]:
        rgb          = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        self._result = self._det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
        if not self._result.hand_landmarks:
            return None
        lm        = self._result.hand_landmarks[0]
        thumb_up  = lm[4].x  < lm[3].x
        index_up  = lm[8].y  < lm[6].y
        middle_up = lm[12].y < lm[10].y
        ring_up   = lm[16].y < lm[14].y
        pinky_up  = lm[20].y < lm[18].y
        count     = sum([thumb_up, index_up, middle_up, ring_up, pinky_up])
        if count == 0 or count >= 4:                                    return "stop"
        if index_up and not middle_up and not ring_up and not pinky_up: return "avanti"
        if index_up and middle_up and not ring_up and not pinky_up:     return "indietro"
        if index_up and middle_up and ring_up and not pinky_up:
            return "destra" if lm[0].x < lm[9].x else "sinistra"
        return None


# ─── Riconoscimento VISO ──────────────────────────────────────────────────────

class FaceRecogniser:
    CONTOUR = [10,338,297,332,284,251,389,356,454,323,361,288,
               397,365,379,378,400,377,152,148,176,149,150,136,
               172,58,132,93,234,127,162,21,54,103,67,109,10]

    def __init__(self):
        opts = mp_vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=FACE_MODEL_PATH),
            running_mode=mp_vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.60,
            min_face_presence_confidence=0.60,
            min_tracking_confidence=0.50,
        )
        self._det    = mp_vision.FaceLandmarker.create_from_options(opts)
        self._result = None
        self._yaw    = 0.0
        self._pitch  = 0.0

    def detect(self, bgr_frame) -> Optional[str]:
        rgb          = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        self._result = self._det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
        if not self._result.face_landmarks: return None
        lm       = self._result.face_landmarks[0]
        nose     = lm[1]; forehead = lm[10]; chin = lm[152]
        leye     = lm[33]; reye = lm[263]
        l_dist   = abs(nose.x - leye.x); r_dist = abs(nose.x - reye.x)
        self._yaw   = (l_dist - r_dist) / (l_dist + r_dist + 1e-6)
        face_h      = abs(forehead.y - chin.y) + 1e-6
        self._pitch = (nose.y - forehead.y) / face_h - 0.45
        if abs(self._pitch) > PITCH_SOGLIA:
            return "avanti" if self._pitch < 0 else "indietro"
        if abs(self._yaw) > YAW_SOGLIA:
            return "destra" if self._yaw > 0 else "sinistra"
        return None


# ─── Robot Controller ─────────────────────────────────────────────────────────

class RobotController:
    def __init__(self, host, port):
        self._url = f"http://{host}:{port}"

    def _post(self, action, speed) -> bool:
        try:
            r = requests.post(f"{self._url}/command",
                              json={"action": action, "speed": speed}, timeout=0.4)
            return r.status_code == 200
        except: return False

    def avanti(self):   return self._post("avanti",   SPEED_AVANTI)
    def indietro(self): return self._post("indietro", SPEED_INDIETRO)
    def sinistra(self): return self._post("sinistra", SPEED_ROTAZIONE)
    def destra(self):   return self._post("destra",   SPEED_ROTAZIONE)
    def stop(self):     return self._post("stop",     0)

    def ping(self) -> bool:
        try: return requests.get(f"{self._url}/ping", timeout=1.0).status_code == 200
        except: return False


# ─── Step Rotation ────────────────────────────────────────────────────────────

class StepRotationManager:
    IDLE = "idle"; MOVING = "moving"; PAUSING = "pausing"

    def __init__(self):
        self._state = self.IDLE; self._dir = None; self._t = 0.0

    def update(self, direction: Optional[str], robot: RobotController) -> str:
        now = time.time(); elapsed = now - self._t
        if direction not in ("sinistra", "destra"):
            if self._state != self.IDLE:
                robot.stop(); self._state = self.IDLE; self._dir = None
            return self.IDLE
        if direction != self._dir:
            self._dir = direction; self._state = self.MOVING; self._t = now; elapsed = 0.0
            robot.sinistra() if direction == "sinistra" else robot.destra()
        if self._state == self.MOVING and elapsed >= STEP_DURATA:
            robot.stop(); self._state = self.PAUSING; self._t = now
        elif self._state == self.PAUSING and elapsed >= STEP_PAUSA:
            self._state = self.MOVING; self._t = now
            robot.sinistra() if direction == "sinistra" else robot.destra()
        return self._state


# ─── Pi Camera Stream Receiver ────────────────────────────────────────────────

class PiCameraReceiver:
    """
    Riceve lo stream MJPEG dalla Pi Camera via HTTP in un thread separato.
    Espone l'ultimo frame come numpy array BGR pronto per OpenCV.
    Tiene solo l'ultimo frame per evitare accodamento e lag.
    """

    def __init__(self, host: str, port: int):
        self._url     = f"http://{host}:{port}/stream"
        self._frame   = None
        self._lock    = threading.Lock()
        self._running = False
        self._thread  = None
        self._ok      = False

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._receive_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def get_frame(self) -> Optional[np.ndarray]:
        with self._lock:
            if self._frame is None:
                return None
            # Scambia il riferimento invece di copiare ogni volta
            f = self._frame
            self._frame = None   # reset: il main legge sempre il frame più fresco
            return f

    @property
    def is_ok(self) -> bool:
        return self._ok

    def _receive_loop(self):
        RETRY_DELAY = 3.0
        while self._running:
            try:
                resp = requests.get(
                    self._url, stream=True,
                    timeout=(5, None),
                    headers={"Accept": "multipart/x-mixed-replace"}
                )
                if resp.status_code != 200:
                    print(f"[STREAM] HTTP {resp.status_code} — riprovo tra {RETRY_DELAY}s")
                    self._ok = False
                    time.sleep(RETRY_DELAY)
                    continue

                print("[STREAM] Connesso alla Pi Camera ✓")
                self._ok = True
                buf = b""

                for chunk in resp.iter_content(chunk_size=4096):
                    if not self._running:
                        break
                    buf += chunk

                    # Estrai solo l'ultimo JPEG completo per evitare lag da accodamento
                    last_soi = buf.rfind(b"\xff\xd8")
                    last_eoi = buf.rfind(b"\xff\xd9")
                    if last_soi != -1 and last_eoi != -1 and last_eoi > last_soi:
                        jpg = buf[last_soi:last_eoi + 2]
                        buf = b""   # svuota il buffer: teniamo solo il più recente

                        arr = np.frombuffer(jpg, dtype=np.uint8)
                        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                        if img is not None:
                            with self._lock:
                                self._frame = img   # sovrascrive direttamente

                    # Evita buffer gonfiato se non arrivano EOI
                    elif len(buf) > 200_000:
                        buf = buf[-50_000:]

            except requests.exceptions.ConnectionError:
                print(f"[STREAM] Connessione rifiutata — il server è avviato? Riprovo tra {RETRY_DELAY}s")
                self._ok = False
                time.sleep(RETRY_DELAY)
            except requests.exceptions.Timeout:
                print(f"[STREAM] Timeout connessione — riprovo tra {RETRY_DELAY}s")
                self._ok = False
                time.sleep(RETRY_DELAY)
            except Exception as e:
                print(f"[STREAM] Errore: {e} — riprovo tra {RETRY_DELAY}s")
                self._ok = False
                time.sleep(RETRY_DELAY)


# ─── QR Code Decoder ──────────────────────────────────────────────────────────

class QRDecoder:
    """
    Decodifica QR code da frame BGR usando pyzbar.
    Restituisce una lista di dict con 'data' (stringa) e 'rect' (x,y,w,h).
    Funziona su frame della Pi Camera in background rispetto a MediaPipe.
    """

    def __init__(self):
        self._available = QR_AVAILABLE

    def decode(self, bgr_frame) -> List[dict]:
        """Ritorna lista di QR trovati nel frame. Lista vuota se nessuno."""
        if not self._available or bgr_frame is None:
            return []
        try:
            # pyzbar lavora bene su scala di grigi → più veloce
            gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
            codes = _pyzbar.decode(gray)
            results = []
            for code in codes:
                if code.type == "QRCODE":
                    text = code.data.decode("utf-8", errors="replace")
                    rect = code.rect  # pyzbar.Rect(left, top, width, height)
                    results.append({
                        "data": text,
                        "rect": (rect.left, rect.top, rect.width, rect.height),
                        "polygon": [(p.x, p.y) for p in code.polygon],
                    })
            return results
        except Exception:
            return []

    @property
    def available(self) -> bool:
        return self._available


HAND_GESTURES = [
    ("✊ Pugno / ✋ Palmo", "STOP"),
    ("☝  Solo indice",      "AVANTI"),
    ("✌  Indice + medio",  "INDIETRO"),
    ("3 dita ←",           "SINISTRA (step)"),
    ("3 dita →",           "DESTRA   (step)"),
]
FACE_GESTURES = [
    ("Testa su",    "AVANTI"),
    ("Testa giù",   "INDIETRO"),
    ("Testa ←",     "SINISTRA (step)"),
    ("Testa →",     "DESTRA   (step)"),
    ("Testa ferma", "STOP"),
]

def build_hud_panel(action, source, connected, mode, step_state,
                    panel_h, has_picam, qr_texts: List[str], pw=480) -> np.ndarray:
    """Costruisce il pannello HUD come striscia orizzontale sotto la Pi Camera."""
    panel  = np.zeros((panel_h, pw, 3), dtype=np.uint8)
    panel[:] = (12, 12, 18)
    x0     = 12
    color  = ACTION_COLOR.get(action, (160,160,160))

    # ── Riga 1: connessione + camera status ───────────────────────────────────
    c_col = (0,210,80) if connected else (50,50,220)
    cv2.putText(panel, "● CONNESSO" if connected else "● NON CONNESSO",
                (x0, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.50, c_col, 1, cv2.LINE_AA)
    cam_col = (0,180,60) if has_picam else (80,80,80)
    cam_txt = "PI CAM LIVE" if has_picam else "PI CAM — in attesa..."
    cv2.putText(panel, cam_txt, (220, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, cam_col, 1, cv2.LINE_AA)

    # ── Riga 2: modalità ──────────────────────────────────────────────────────
    mode_lbl = {"mano":"MANO","viso":"VISO","entrambi":"MANO+VISO"}
    cv2.putText(panel, f"MODO: {mode_lbl.get(mode,mode)}  [M] cambia  [Q] esci",
                (x0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (130,130,150), 1, cv2.LINE_AA)

    cv2.line(panel, (0,48),(pw,48),(50,50,60),1)

    # ── Riga 3: comando corrente (grande, colore azione) ──────────────────────
    label   = action.upper() if action else "IN ATTESA..."
    src_lbl = f"[{source}]" if source else ""
    step_info = ""
    if action in ("sinistra","destra"):
        step_info = " ▶" if step_state == "moving" else " ⏸"
    cv2.putText(panel, f"CMD: {label} {src_lbl}{step_info}",
                (x0, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.80, color, 2, cv2.LINE_AA)

    cv2.line(panel, (0,88),(pw,88),(50,50,60),1)

    # ── Gesti (su due colonne per risparmiare spazio verticale) ───────────────
    table = FACE_GESTURES if mode == "viso" else HAND_GESTURES
    title = "GESTI VISO" if mode == "viso" else "GESTI MANO"
    mid   = pw // 2
    cv2.putText(panel, title, (x0, 104),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (130,130,155), 1, cv2.LINE_AA)
    # Prima colonna: gesti 0-2 | seconda colonna: gesti 3-4
    for i, (gesto, cmd) in enumerate(table):
        col_x = x0 if i < 3 else mid
        row_y = 120 + (i % 3) * 18
        attivo = action is not None and cmd.split()[0].lower() == action
        rc     = color if attivo else (120,120,138)
        ww     = 2 if attivo else 1
        cv2.putText(panel, f"{gesto} → {cmd}", (col_x, row_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.30, rc, ww, cv2.LINE_AA)

    if mode == "entrambi":
        cv2.putText(panel, "VISO (fallback): Su/Giù=AVA/IND  Sx/Dx=SIN/DES",
                    (x0, panel_h - 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.29, (80,80,100), 1, cv2.LINE_AA)

    # ── QR Code rilevati ──────────────────────────────────────────────────────
    cv2.line(panel, (0, panel_h - 20),(pw, panel_h - 20),(50,50,60),1)
    if qr_texts:
        qr_col = (0, 230, 160)
        txt    = qr_texts[0]
        extra  = f"  (+{len(qr_texts)-1} altri)" if len(qr_texts) > 1 else ""
        label_qr = f"QR: {txt[:70]}{'…' if len(txt)>70 else ''}{extra}"
        cv2.putText(panel, label_qr, (x0, panel_h - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, qr_col, 1, cv2.LINE_AA)
    else:
        cv2.putText(panel, "QR: nessuno rilevato", (x0, panel_h - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, (60,60,70), 1, cv2.LINE_AA)

    return panel

def build_picam_placeholder(w, h) -> np.ndarray:
    """Frame placeholder mostrato quando lo stream Pi Camera non è disponibile."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = (18, 18, 25)
    cx, cy = w//2, h//2
    cv2.rectangle(img, (cx-60,cy-45),(cx+60,cy+45),(60,60,70),-1)
    cv2.rectangle(img, (cx-60,cy-45),(cx+60,cy+45),(90,90,100),2)
    cv2.circle(img, (cx,cy), 22, (90,90,100), -1)
    cv2.circle(img, (cx,cy), 14, (18,18,25), -1)
    cv2.putText(img, "PI CAMERA", (cx-52, cy+75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80,80,90), 1, cv2.LINE_AA)
    cv2.putText(img, "in attesa stream...", (cx-72, cy+95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (60,60,70), 1, cv2.LINE_AA)
    return img


def draw_qr_overlay(frame, qr_results: List[dict], frame_w: int, frame_h: int,
                    orig_w: int, orig_h: int):
    """
    Disegna poligono e testo QR sul frame Pi Camera ridimensionato.
    Scala le coordinate originali al frame mostrato.
    """
    if not qr_results:
        return
    sx = frame_w / orig_w if orig_w > 0 else 1.0
    sy = frame_h / orig_h if orig_h > 0 else 1.0
    for qr in qr_results:
        # Poligono del QR
        if qr["polygon"]:
            pts = np.array([(int(x*sx), int(y*sy)) for x,y in qr["polygon"]],
                           dtype=np.int32)
            cv2.polylines(frame, [pts], True, (0, 230, 160), 3, cv2.LINE_AA)
            # Angolo in alto a sinistra del poligono per il testo
            tx = pts[:,0].min()
            ty = pts[:,1].min() - 10
        else:
            rx, ry, rw, rh = qr["rect"]
            rx2, ry2 = int(rx*sx), int(ry*sy)
            rw2, rh2 = int(rw*sx), int(rh*sy)
            cv2.rectangle(frame, (rx2,ry2),(rx2+rw2,ry2+rh2),(0,230,160),3)
            tx, ty = rx2, ry2 - 10

        ty = max(ty, 18)
        text = qr["data"][:50] + ("…" if len(qr["data"]) > 50 else "")
        # Sfondo testo
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        cv2.rectangle(frame, (tx-4, ty-th-6),(tx+tw+4, ty+4),(0,0,0),-1)
        cv2.putText(frame, text, (tx, ty),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,230,160), 2, cv2.LINE_AA)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AlphaBot - Controllo Gesti")
    parser.add_argument("--host",  default=DEFAULT_HOST)
    parser.add_argument("--port",  default=DEFAULT_PORT, type=int)
    parser.add_argument("--cam",   default=CAMERA_INDEX, type=int)
    parser.add_argument("--mode",  default="entrambi", choices=MODI)
    args = parser.parse_args()

    mode = args.mode
    ensure_models(mode)

    print("[INFO] Caricamento modelli...")
    hand_rec = HandRecogniser() if mode in ("mano",  "entrambi") else None
    face_rec = FaceRecogniser() if mode in ("viso",  "entrambi") else None

    robot   = RobotController(args.host, args.port)
    stepper = StepRotationManager()
    qr_dec  = QRDecoder()

    if not qr_dec.available:
        print("[INFO] Per abilitare QR: pip install pyzbar  (Linux: sudo apt install libzbar0)")

    # ── Pi Camera stream receiver (sempre attivo) ─────────────────────────────
    pi_cam = PiCameraReceiver(args.host, args.port)
    pi_cam.start()
    print(f"[INFO] Stream Pi Camera: http://{args.host}:{args.port}/stream")

    connected = robot.ping()
    last_ping = time.time()

    # ── Webcam locale (solo per gesture, non mostrata) ────────────────────────
    cap = cv2.VideoCapture(args.cam)
    if not cap.isOpened():
        print(f"[ERRORE] Webcam {args.cam} non disponibile. Prova --cam 1")
        sys.exit(1)
    # 640×480: risoluzione ottimale per MediaPipe (buon riconoscimento gesti)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  DETECT_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DETECT_H)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)   # evita accumulo frame in coda

    # Dimensioni finestra: tutta la larghezza è della Pi Camera
    # 860×645 (4:3) — più grande per vedere meglio l'ambiente e i QR code
    PICAM_W, PICAM_H = 860, 645
    HUD_H            = 180   # striscia HUD compatta sotto

    print(f"[INFO] Robot {args.host}:{args.port} — {'ONLINE ✓' if connected else 'OFFLINE ✗'}")
    print(f"[INFO] Modalità: {mode}  |  Webcam locale nascosta (solo gesture)")
    print(f"[INFO] M=cambia modo  |  Q=esci")

    action: Optional[str] = None
    source: str = ""
    last_pi_frame: Optional[np.ndarray] = None
    last_pi_orig_size = (640, 480)   # dimensioni originali del frame Pi Camera
    qr_results: List[dict] = []      # ultimi QR trovati
    qr_scan_counter = 0

    while True:
        ret, raw = cap.read()
        if not ret:
            print("[ERRORE] Lettura webcam fallita"); break

        # Flip orizzontale per effetto specchio naturale
        detect_frame = cv2.flip(raw, 1)

        # ── Riconosci gesto (ogni frame, risoluzione piena per qualità) ───────
        hand_action = face_action = None
        if hand_rec: hand_action = hand_rec.detect(detect_frame)
        if face_rec: face_action = face_rec.detect(detect_frame)

        if hand_action is not None:   action, source = hand_action, "mano"
        elif face_action is not None: action, source = face_action, "viso"
        else:                         action, source = None, ""

        # ── Invia comandi ─────────────────────────────────────────────────────
        step_state = "idle"
        if connected:
            if action in ("sinistra","destra"):
                step_state = stepper.update(action, robot)
            else:
                stepper.update(None, robot)
                if action == "avanti":     robot.avanti()
                elif action == "indietro": robot.indietro()
                else:                      robot.stop()

        # ── Ping periodico ────────────────────────────────────────────────────
        if time.time() - last_ping > 3.0:
            connected = robot.ping()
            last_ping = time.time()

        # ── Recupera frame Pi Camera ──────────────────────────────────────────
        new_pi = pi_cam.get_frame()
        if new_pi is not None:
            last_pi_frame = new_pi
            last_pi_orig_size = (new_pi.shape[1], new_pi.shape[0])  # (w, h)
        has_picam = pi_cam.is_ok

        # ── Scansione QR (ogni QR_SCAN_EVERY frame, sul frame Pi Camera raw) ──
        qr_scan_counter += 1
        if qr_dec.available and last_pi_frame is not None and \
                qr_scan_counter % QR_SCAN_EVERY == 0:
            found = qr_dec.decode(last_pi_frame)
            if found:
                qr_results = found
                for qr in found:
                    print(f"[QR] Rilevato: {qr['data']}")
            else:
                qr_results = []

        if last_pi_frame is not None:
            pi_frame = cv2.resize(last_pi_frame, (PICAM_W, PICAM_H),
                                  interpolation=cv2.INTER_LINEAR)
        else:
            pi_frame = build_picam_placeholder(PICAM_W, PICAM_H)

        # Overlay QR code sulla Pi Camera
        if qr_results:
            orig_w, orig_h = last_pi_orig_size
            draw_qr_overlay(pi_frame, qr_results, PICAM_W, PICAM_H, orig_w, orig_h)

        # Overlay comando attivo sulla Pi Camera
        if action:
            color = ACTION_COLOR.get(action, (200,200,200))
            label = action.upper()
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)
            tx, ty = (PICAM_W - tw) // 2, PICAM_H - 20
            cv2.putText(pi_frame, label, (tx, ty),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,0), 5, cv2.LINE_AA)
            cv2.putText(pi_frame, label, (tx, ty),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3, cv2.LINE_AA)

        # ── Assembla la finestra: Pi Camera + HUD sotto ───────────────────────
        qr_texts = [qr["data"] for qr in qr_results]
        hud = build_hud_panel(action, source, connected, mode,
                              step_state, HUD_H, has_picam, qr_texts, pw=PICAM_W)
        canvas = np.vstack([pi_frame, hud])

        cv2.imshow("AlphaBot - Controllo Gesti", canvas)

        # ── Tasti ─────────────────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('m'):
            mode = MODI[(MODI.index(mode)+1) % len(MODI)]
            ensure_models(mode)
            hand_rec = HandRecogniser() if mode in ("mano","entrambi") else None
            face_rec = FaceRecogniser() if mode in ("viso","entrambi") else None
            print(f"[INFO] Modalità → {mode}")

    robot.stop()
    pi_cam.stop()
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Uscito. Robot fermato.")


if __name__ == "__main__":
    main()
