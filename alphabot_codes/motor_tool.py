"""
motor_tool.py — Test e calibrazione motori AlphaBot
Gira sul Raspberry Pi. Non richiede Flask o altri server.

Avvio:
    python3 motor_tool.py              # menu principale
    python3 motor_tool.py --test       # vai diretto al test interattivo
    python3 motor_tool.py --auto       # esegui sequenza automatica ed esci
    python3 motor_tool.py --calibra    # vai diretto alla calibrazione
    python3 motor_tool.py --speed 120  # velocità di partenza personalizzata
"""

import time, argparse, sys, json, os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "motor_config.json")

# ─── GPIO ─────────────────────────────────────────────────────────────────────
try:
    import RPi.GPIO as GPIO
    ON_PI = True
except (ImportError, RuntimeError):
    ON_PI = False
    print("[WARN] RPi.GPIO non trovato — modalità simulazione (nessun movimento reale)")
    class _MockGPIO:
        BCM = OUT = HIGH = LOW = 0
        def setmode(self, *a):        pass
        def setup(self, *a, **k):     pass
        def output(self, *a):         pass
        def cleanup(self):            pass
        class PWM:
            def __init__(self, p, f):      pass
            def start(self, dc):           pass
            def ChangeDutyCycle(self, dc): pass
            def stop(self):                pass
    GPIO = _MockGPIO()

# ─── Pin GPIO (BCM) ───────────────────────────────────────────────────────────
AIN1, AIN2, PWMA = 12, 13, 6    # Motore sinistro
BIN1, BIN2, PWMB = 20, 21, 26   # Motore destro
PWM_FREQ = 500

# ─── Trim globale (aggiornato da calibrazione o da file) ─────────────────────
TRIM_SX = 1.0
TRIM_DX = 1.0

# ─── Config ───────────────────────────────────────────────────────────────────

def carica_config():
    global TRIM_SX, TRIM_DX
    if os.path.exists(CONFIG_FILE):
        try:
            cfg = json.load(open(CONFIG_FILE))
            TRIM_SX = cfg.get("trim_sx", 1.0)
            TRIM_DX = cfg.get("trim_dx", 1.0)
            print(f"[INFO] Calibrazione caricata: trim_sx={TRIM_SX:.3f}  trim_dx={TRIM_DX:.3f}")
            return
        except Exception as e:
            print(f"[WARN] Errore lettura config: {e}")
    print("[INFO] Nessuna calibrazione salvata — trim 1.0 / 1.0")

def salva_config():
    cfg = {"trim_sx": round(TRIM_SX, 3), "trim_dx": round(TRIM_DX, 3)}
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"\n  [SALVATO] {CONFIG_FILE}")
    print(f"  trim_sx = {cfg['trim_sx']}   trim_dx = {cfg['trim_dx']}")

# ─── Setup / Cleanup GPIO ─────────────────────────────────────────────────────

def setup():
    GPIO.setmode(GPIO.BCM)
    for pin in (AIN1, AIN2, PWMA, BIN1, BIN2, PWMB):
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    pwm_a = GPIO.PWM(PWMA, PWM_FREQ)
    pwm_b = GPIO.PWM(PWMB, PWM_FREQ)
    pwm_a.start(0)
    pwm_b.start(0)
    return pwm_a, pwm_b

def cleanup(pwm_a, pwm_b):
    _stop(pwm_a, pwm_b)
    pwm_a.stop()
    pwm_b.stop()
    GPIO.cleanup()

# ─── Motori ───────────────────────────────────────────────────────────────────

def _dc(speed, trim=1.0):
    return min(100, max(0, int(speed * trim * 100 // 255)))

def _stop(pwm_a, pwm_b):
    pwm_a.ChangeDutyCycle(0)
    pwm_b.ChangeDutyCycle(0)
    for pin in (AIN1, AIN2, BIN1, BIN2):
        GPIO.output(pin, GPIO.LOW)

def avanti(pwm_a, pwm_b, speed):
    GPIO.output(AIN1, GPIO.HIGH); GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(BIN1, GPIO.HIGH); GPIO.output(BIN2, GPIO.LOW)
    pwm_a.ChangeDutyCycle(_dc(speed, TRIM_SX))
    pwm_b.ChangeDutyCycle(_dc(speed, TRIM_DX))

def indietro(pwm_a, pwm_b, speed):
    GPIO.output(AIN1, GPIO.LOW);  GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.LOW);  GPIO.output(BIN2, GPIO.HIGH)
    pwm_a.ChangeDutyCycle(_dc(speed, TRIM_SX))
    pwm_b.ChangeDutyCycle(_dc(speed, TRIM_DX))

def sinistra(pwm_a, pwm_b, speed):
    GPIO.output(AIN1, GPIO.LOW);  GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.HIGH); GPIO.output(BIN2, GPIO.LOW)
    pwm_a.ChangeDutyCycle(_dc(speed, TRIM_SX))
    pwm_b.ChangeDutyCycle(_dc(speed, TRIM_DX))

def destra(pwm_a, pwm_b, speed):
    GPIO.output(AIN1, GPIO.HIGH); GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(BIN1, GPIO.LOW);  GPIO.output(BIN2, GPIO.HIGH)
    pwm_a.ChangeDutyCycle(_dc(speed, TRIM_SX))
    pwm_b.ChangeDutyCycle(_dc(speed, TRIM_DX))

def solo_sx(pwm_a, pwm_b, speed):
    GPIO.output(AIN1, GPIO.HIGH); GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(BIN1, GPIO.LOW);  GPIO.output(BIN2, GPIO.LOW)
    pwm_a.ChangeDutyCycle(_dc(speed, TRIM_SX))
    pwm_b.ChangeDutyCycle(0)

def solo_dx(pwm_a, pwm_b, speed):
    GPIO.output(AIN1, GPIO.LOW);  GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(BIN1, GPIO.HIGH); GPIO.output(BIN2, GPIO.LOW)
    pwm_a.ChangeDutyCycle(0)
    pwm_b.ChangeDutyCycle(_dc(speed, TRIM_DX))

# ─── Input tasto singolo ──────────────────────────────────────────────────────

def _tasto(prompt=""):
    if prompt:
        print(prompt, end="", flush=True)
    try:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch.lower()
    except Exception:
        return input().strip().lower()[:1]

# ═══════════════════════════════════════════════════════════════════════════════
# MODALITÀ 1 — TEST AUTOMATICO
# ═══════════════════════════════════════════════════════════════════════════════

def test_automatico(pwm_a, pwm_b, speed):
    passi = [
        ("AVANTI",               lambda: avanti(pwm_a, pwm_b, speed),   1.5),
        ("STOP",                 lambda: _stop(pwm_a, pwm_b),           0.5),
        ("INDIETRO",             lambda: indietro(pwm_a, pwm_b, speed), 1.5),
        ("STOP",                 lambda: _stop(pwm_a, pwm_b),           0.5),
        ("SINISTRA (rotazione)", lambda: sinistra(pwm_a, pwm_b, speed), 1.0),
        ("STOP",                 lambda: _stop(pwm_a, pwm_b),           0.5),
        ("DESTRA (rotazione)",   lambda: destra(pwm_a, pwm_b, speed),   1.0),
        ("STOP",                 lambda: _stop(pwm_a, pwm_b),           0.5),
        ("SOLO MOTORE SX",       lambda: solo_sx(pwm_a, pwm_b, speed),  1.0),
        ("STOP",                 lambda: _stop(pwm_a, pwm_b),           0.5),
        ("SOLO MOTORE DX",       lambda: solo_dx(pwm_a, pwm_b, speed),  1.0),
        ("STOP FINALE",          lambda: _stop(pwm_a, pwm_b),           0.3),
    ]
    print(f"\n{'═'*46}")
    print(f"  TEST AUTOMATICO  —  vel {speed}/255  ({_dc(speed)}% DC)")
    print(f"  trim_sx={TRIM_SX:.3f}   trim_dx={TRIM_DX:.3f}")
    print(f"{'═'*46}")
    for nome, fn, durata in passi:
        print(f"  ▶ {nome:<26} ({durata}s) ... ", end="", flush=True)
        fn()
        time.sleep(durata)
        print("OK")
    print(f"{'═'*46}")
    print("  Completato!\n")

# ═══════════════════════════════════════════════════════════════════════════════
# MODALITÀ 2 — TEST INTERATTIVO
# ═══════════════════════════════════════════════════════════════════════════════

def test_interattivo(pwm_a, pwm_b, speed):
    print(f"""
╔══════════════════════════════════════════╗
║        AlphaBot — Test Interattivo       ║
╠══════════════════════════════════════════╣
║  W      →  Avanti                       ║
║  S      →  Indietro                     ║
║  A      →  Sinistra (rotazione)         ║
║  D      →  Destra   (rotazione)         ║
║  SPAZIO →  Stop                         ║
║  1      →  Solo motore sinistro         ║
║  3      →  Solo motore destro           ║
║  T      →  Test automatico              ║
║  C      →  Vai alla calibrazione        ║
║  +/-    →  Aumenta / diminuisci vel.   ║
║  Q      →  Torna al menu principale     ║
╚══════════════════════════════════════════╝
  trim_sx={TRIM_SX:.3f}   trim_dx={TRIM_DX:.3f}   vel={speed}
""")

    cmd = "STOP"
    while True:
        print(f"\r  [{cmd:<20}]  vel={speed}  sx={TRIM_SX:.2f} dx={TRIM_DX:.2f}  (tasto) ",
              end="", flush=True)
        t = _tasto()

        if t == 'w':
            cmd = "AVANTI";    avanti(pwm_a, pwm_b, speed)
        elif t == 's':
            cmd = "INDIETRO";  indietro(pwm_a, pwm_b, speed)
        elif t == 'a':
            cmd = "SINISTRA";  sinistra(pwm_a, pwm_b, speed)
        elif t == 'd':
            cmd = "DESTRA";    destra(pwm_a, pwm_b, speed)
        elif t == ' ':
            cmd = "STOP";      _stop(pwm_a, pwm_b)
        elif t == '1':
            cmd = "SOLO SX";   solo_sx(pwm_a, pwm_b, speed)
        elif t == '3':
            cmd = "SOLO DX";   solo_dx(pwm_a, pwm_b, speed)
        elif t == 't':
            _stop(pwm_a, pwm_b)
            print()
            test_automatico(pwm_a, pwm_b, speed)
            cmd = "STOP"
        elif t == 'c':
            _stop(pwm_a, pwm_b)
            print()
            return 'calibra'   # segnala al chiamante di aprire calibrazione
        elif t == '+':
            speed = min(255, speed + 10)
            print(f"\n  ↑ vel → {speed}")
        elif t == '-':
            speed = max(40, speed - 10)
            print(f"\n  ↓ vel → {speed}")
        elif t == 'q':
            _stop(pwm_a, pwm_b)
            print()
            return 'menu'
    return 'menu'

# ═══════════════════════════════════════════════════════════════════════════════
# MODALITÀ 3 — CALIBRAZIONE
# ═══════════════════════════════════════════════════════════════════════════════

TRIM_STEP = 0.01

def calibrazione(pwm_a, pwm_b, speed):
    global TRIM_SX, TRIM_DX
    print(f"""
╔══════════════════════════════════════════════════╗
║          AlphaBot — Calibrazione Motori          ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  Metti il robot su una superficie dritta e       ║
║  liscia. Premi SPAZIO per farlo andare avanti    ║
║  2 secondi e osserva se curva.                   ║
║                                                  ║
║  Curva a DESTRA   → premi  ←  (A)               ║
║  Curva a SINISTRA → premi  →  (D)               ║
║                                                  ║
║  SPAZIO  →  Avanti 2s poi stop (osserva)         ║
║  A / D   →  Regola trim  (±{TRIM_STEP})                ║
║  R       →  Reset trim  1.0 / 1.0               ║
║  +/-     →  Cambia velocità di test              ║
║  S       →  Salva e torna al menu                ║
║  Q       →  Torna al menu SENZA salvare          ║
╚══════════════════════════════════════════════════╝
""")

    def barra(trim):
        filled = int(round(trim * 20))
        return "█" * filled + "░" * (20 - filled)

    def stampa():
        print(f"\r  SX [{barra(TRIM_SX)}] {TRIM_SX:.3f}   "
              f"DX [{barra(TRIM_DX)}] {TRIM_DX:.3f}   vel={speed}  ",
              end="", flush=True)

    stampa()

    while True:
        t = _tasto()

        if t == ' ':
            print(f"\n  ▶ AVANTI 2s...", end="", flush=True)
            avanti(pwm_a, pwm_b, speed)
            time.sleep(2.0)
            _stop(pwm_a, pwm_b)
            print("  STOP")

        elif t == 'a':
            # Curva destra → DX troppo veloce → riduci DX
            if TRIM_DX > 0.50:
                TRIM_DX = round(TRIM_DX - TRIM_STEP, 3)
                if TRIM_SX < 1.0:
                    TRIM_SX = 1.0
            print()

        elif t == 'd':
            # Curva sinistra → SX troppo veloce → riduci SX
            if TRIM_SX > 0.50:
                TRIM_SX = round(TRIM_SX - TRIM_STEP, 3)
                if TRIM_DX < 1.0:
                    TRIM_DX = 1.0
            print()

        elif t == 'r':
            TRIM_SX, TRIM_DX = 1.0, 1.0
            print("\n  Reset → 1.0 / 1.0")

        elif t == '+':
            speed = min(255, speed + 10)
            print(f"\n  ↑ vel → {speed}")

        elif t == '-':
            speed = max(60, speed - 10)
            print(f"\n  ↓ vel → {speed}")

        elif t == 's':
            _stop(pwm_a, pwm_b)
            salva_config()
            print("\n  Calibrazione salvata — ritorno al menu.")
            return 'menu'

        elif t == 'q':
            _stop(pwm_a, pwm_b)
            print("\n  Uscita senza salvare — ritorno al menu.")
            return 'menu'

        stampa()

# ═══════════════════════════════════════════════════════════════════════════════
# MENU PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════

def menu_principale(pwm_a, pwm_b, speed):
    while True:
        print(f"""
╔══════════════════════════════════════════╗
║         AlphaBot — Motor Tool            ║
╠══════════════════════════════════════════╣
║                                          ║
║   1  →  Test interattivo (W/A/S/D)      ║
║   2  →  Test automatico (sequenza)      ║
║   3  →  Calibrazione motori             ║
║   Q  →  Esci                            ║
║                                          ║
╠══════════════════════════════════════════╣
║  Modalità: {'Pi reale    ' if ON_PI else 'SIMULAZIONE'}                   ║
║  trim_sx={TRIM_SX:.3f}   trim_dx={TRIM_DX:.3f}              ║
║  Velocità: {speed}/255  ({_dc(speed)}% DC)               ║
╚══════════════════════════════════════════╝""")

        t = _tasto("  Scegli: ")
        print()

        if t == '1':
            result = test_interattivo(pwm_a, pwm_b, speed)
            if result == 'calibra':
                calibrazione(pwm_a, pwm_b, speed)

        elif t == '2':
            test_automatico(pwm_a, pwm_b, speed)

        elif t == '3':
            calibrazione(pwm_a, pwm_b, speed)

        elif t == 'q':
            _stop(pwm_a, pwm_b)
            print("  Uscita — motori fermi.\n")
            break

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="AlphaBot Motor Tool")
    parser.add_argument("--speed",   default=150, type=int,
                        help="Velocità di partenza 0-255 (default 150)")
    parser.add_argument("--test",    action="store_true", help="Vai diretto al test interattivo")
    parser.add_argument("--auto",    action="store_true", help="Esegui test automatico ed esci")
    parser.add_argument("--calibra", action="store_true", help="Vai diretto alla calibrazione")
    args = parser.parse_args()

    speed = max(40, min(255, args.speed))

    print(f"\n[INFO] Inizializzazione GPIO...")
    print(f"       SX: AIN1={AIN1} AIN2={AIN2} PWM={PWMA}")
    print(f"       DX: BIN1={BIN1} BIN2={BIN2} PWM={PWMB}")

    carica_config()
    pwm_a, pwm_b = setup()
    print(f"[INFO] GPIO pronto — {'Pi reale' if ON_PI else 'simulazione'}\n")

    try:
        if args.auto:
            test_automatico(pwm_a, pwm_b, speed)
        elif args.test:
            test_interattivo(pwm_a, pwm_b, speed)
        elif args.calibra:
            calibrazione(pwm_a, pwm_b, speed)
        else:
            menu_principale(pwm_a, pwm_b, speed)
    except KeyboardInterrupt:
        print("\n[INFO] Interrotto con Ctrl+C")
    finally:
        cleanup(pwm_a, pwm_b)
        print("[INFO] GPIO pulito. Uscita.")

if __name__ == "__main__":
    main()
