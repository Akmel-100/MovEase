import pygame
import random
import time
import math
import cv2
import mediapipe as mp

# -------------------------------
# Inizializzazione Pygame (FULLSCREEN)
# -------------------------------
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Gioco Riabilitativo - MediaPipe")
font = pygame.font.SysFont("Segoe UI", 26)
large_font = pygame.font.SysFont("Segoe UI", 64, bold=True)
small_font = pygame.font.SysFont("Segoe UI", 20)
clock = pygame.time.Clock()

# -------------------------------
# Colori
# -------------------------------
WHITE = (255, 255, 255)
RED = (255, 80, 80)
GREEN = (80, 200, 120)
BLUE = (80, 120, 255)
YELLOW = (255, 220, 80)
CYAN = (0, 255, 200)
DARK_TEXT = (40, 40, 40)

# -------------------------------
# Soglia chiusura mano e punteggio minimo
# -------------------------------
HAND_CLOSURE_THRESHOLD = 20  # Percentuale minima per considerare la mano chiusa
MIN_SCORE_TO_PASS = 10  # Punteggio minimo per superare la prova

# -------------------------------
# Funzioni utility
# -------------------------------
def random_color():
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def draw_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

# -------------------------------
# Funzioni Gesture MediaPipe
# -------------------------------
def calculate_hand_closure(landmarks):
    fingers_data = [
        (8, 5, 6),   # indice
        (12, 9, 10), # medio
        (16, 13, 14),# anulare
        (20, 17, 18) # mignolo
    ]
    total_closure = 0.0
    for tip_idx, mcp_idx, pip_idx in fingers_data:
        tip = landmarks[tip_idx]
        mcp = landmarks[mcp_idx]
        pip = landmarks[pip_idx]
        vertical_distance = tip.y - mcp.y
        if vertical_distance > -0.05:
            closure_amount = min(1.0, (vertical_distance + 0.05) / 0.15)
            total_closure += closure_amount
    avg_closure = (total_closure / 4.0) * 100
    if avg_closure < 30:
        avg_closure = avg_closure * 1.5
    return min(100, int(avg_closure))

def is_hand_closed(landmarks, threshold=HAND_CLOSURE_THRESHOLD):
    closure = calculate_hand_closure(landmarks)
    return closure >= threshold

# -------------------------------
# Funzione per inizializzare il gioco
# -------------------------------
def init_game():
    global score, targets_hit_count, radius, target_x, target_y, target_hand, target_color
    global hit_effect_timer, target_visible, disappear_timer, game_over, hand_trails, start_time
    
    score = 0
    targets_hit_count = 0
    radius = 40
    
    target_x = random.randint(radius, WIDTH - radius)
    target_y = random.randint(radius, HEIGHT - radius)
    target_hand = random.choice(["Left", "Right"])
    target_color = BLUE if target_hand == "Left" else RED
    hit_effect_timer = 0
    target_visible = True
    disappear_timer = 0
    game_over = False
    hand_trails = {"Left": [], "Right": []}
    start_time = time.time()

# -------------------------------
# Variabili di gioco
# -------------------------------
game_duration = 60
running = True
init_game()

# -------------------------------
# MediaPipe setup
# -------------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)

# -------------------------------
# CONTROLLO WEBCAM CON DIAGNOSTICA
# -------------------------------
print("=" * 50)
print("DIAGNOSTICA WEBCAM")
print("=" * 50)

cap = cv2.VideoCapture(0)

# Verifica se la webcam si è aperta correttamente
if not cap.isOpened():
    print("ERRORE: Impossibile aprire la webcam!")
    print("Possibili cause:")
    print("- La webcam è usata da un altro programma")
    print("- Driver della webcam non funzionanti")
    print("- Permessi non concessi")
    print("\nProvo con webcam indice 1...")
    
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("ERRORE: Nessuna webcam disponibile!")
        pygame.quit()
        exit()

# Mostra informazioni webcam
print(f"✓ Webcam aperta correttamente")
print(f"  Larghezza: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
print(f"  Altezza: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
print(f"  FPS: {cap.get(cv2.CAP_PROP_FPS)}")

# Test di lettura frame
ret, test_frame = cap.read()
if not ret:
    print("ERRORE: Impossibile leggere dalla webcam!")
    print("La webcam è aperta ma non risponde.")
    cap.release()
    pygame.quit()
    exit()

print(f"✓ Frame di test letto correttamente: {test_frame.shape}")
print("=" * 50)
print()

# -------------------------------
# Schermata istruzioni
# -------------------------------
show_instructions = True
while show_instructions:
    draw_gradient(screen, (240, 245, 255), (200, 220, 255))
    title = large_font.render("Istruzioni", True, DARK_TEXT)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))
    instructions = [
        "Chiudi la mano sopra il bersaglio per colpirlo.",
        "Ogni mano colpisce solo i suoi cerchi.",
        "", 
        "Durata: 60 secondi.", 
        f"Punteggio minimo per superare: {MIN_SCORE_TO_PASS} punti",
        "Se non raggiungi il punteggio minimo, riprovi!",
        "",
        "Premi un tasto per iniziare."
    ]
    for i, line in enumerate(instructions):
        text = font.render(line, True, DARK_TEXT)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 170 + i * 35))
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            show_instructions = False

# -------------------------------
# Variabili per gestire il restart
# -------------------------------
show_fail_screen = False
fail_screen_timer = 0

# -------------------------------
# Ciclo principale del gioco
# -------------------------------
frame_count = 0
failed_frames = 0

print("Inizio gioco...")
while running:
    # -------------------------------
    # Schermata di fallimento
    # -------------------------------
    if show_fail_screen:
        draw_gradient(screen, (255, 200, 200), (255, 150, 150))
        
        # Pannello centrale
        panel = pygame.Surface((700, 450), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 230))
        screen.blit(panel, (WIDTH // 2 - 350, HEIGHT // 2 - 225))
        
        # Titolo PROVA FALLITA
        fail_title = large_font.render("PROVA FALLITA!", True, RED)
        screen.blit(fail_title, (WIDTH // 2 - fail_title.get_width() // 2, HEIGHT // 2 - 150))
        
        # Punteggio ottenuto
        score_text = font.render(f"Punteggio ottenuto: {score}", True, DARK_TEXT)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 60))
        
        # Punteggio richiesto
        required_text = font.render(f"Punteggio richiesto: {MIN_SCORE_TO_PASS}", True, DARK_TEXT)
        screen.blit(required_text, (WIDTH // 2 - required_text.get_width() // 2, HEIGHT // 2 - 20))
        
        # Messaggio di riavvio
        retry_text = large_font.render("RIPROVA!", True, YELLOW)
        screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2 + 50))
        
        # Info countdown
        countdown_sec = max(0, 3 - (fail_screen_timer // 30))
        countdown_text = small_font.render(f"Riavvio tra {countdown_sec} secondi...", True, DARK_TEXT)
        screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 + 140))
        
        pygame.display.flip()
        fail_screen_timer += 1
        
        # Dopo 3 secondi (90 frame a 30 fps), riavvia il gioco
        if fail_screen_timer >= 90:
            show_fail_screen = False
            fail_screen_timer = 0
            init_game()
            
            # Countdown prima di ripartire
            for i in range(3, 0, -1):
                draw_gradient(screen, (240, 245, 255), (200, 220, 255))
                txt = large_font.render(str(i), True, RED)
                screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2))
                pygame.display.flip()
                pygame.time.delay(1000)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        
        clock.tick(30)
        continue
    
    # -------------------------------
    # Gioco normale
    # -------------------------------
    current_time = time.time()
    elapsed_time = current_time - start_time
    remaining_time = max(0, int(game_duration - elapsed_time))
    frame_count += 1

    ret, frame = cap.read()
    if not ret:
        failed_frames += 1
        print(f"Frame non letto! (Totale errori: {failed_frames})")
        
        # Se troppi frame falliti consecutivi, mostra errore
        if failed_frames > 30:
            print("ERRORE CRITICO: Troppi frame persi!")
            running = False
            break
        
        pygame.time.wait(100)
        continue
    
    # Reset contatore se il frame è stato letto correttamente
    failed_frames = 0

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    screen_frame = cv2.resize(frame, (WIDTH, HEIGHT))
    screen_frame = cv2.cvtColor(screen_frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(screen_frame.swapaxes(0, 1))
    screen.blit(frame_surface, (0, 0))

    hand_positions = {"Left": None, "Right": None}
    hand_closed_status = {"Left": False, "Right": False}

    if result.multi_hand_landmarks and result.multi_handedness:
        for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            hand_label = handedness.classification[0].label
            x = sum([lm.x for lm in hand_landmarks.landmark]) / len(hand_landmarks.landmark)
            y = sum([lm.y for lm in hand_landmarks.landmark]) / len(hand_landmarks.landmark)
            hand_center_pygame = (int(x * WIDTH), int(y * HEIGHT))
            hand_positions[hand_label] = hand_center_pygame

            hand_trails.setdefault(hand_label, []).append(hand_center_pygame)
            if len(hand_trails[hand_label]) > 20:
                hand_trails[hand_label].pop(0)

            closure_value = calculate_hand_closure(hand_landmarks.landmark)
            hand_closed_status[hand_label] = is_hand_closed(hand_landmarks.landmark, HAND_CLOSURE_THRESHOLD)

            color = BLUE if hand_label == "Left" else RED
            for lm in hand_landmarks.landmark:
                px, py = int(lm.x * WIDTH), int(lm.y * HEIGHT)
                pygame.draw.circle(screen, color, (px, py), 5)

            # Controllo bersaglio mano-specifico
            if hand_closed_status[hand_label] and target_visible and hand_label == target_hand:
                distance = math.hypot(hand_center_pygame[0] - target_x, hand_center_pygame[1] - target_y)
                if distance <= radius:
                    score += 1
                    targets_hit_count += 1
                    hit_effect_timer = 8
                    target_visible = False
                    disappear_timer = 30
                    if radius > 20:
                        radius -= 1

    # Disegna scia mano
    for label, trail in hand_trails.items():
        if len(trail) > 1:
            for i in range(len(trail)-1):
                start = trail[i]
                end = trail[i+1]
                thickness = int(2 + 4 * (i / len(trail)))
                trail_color = BLUE if label == "Left" else RED
                pygame.draw.line(screen, trail_color, start, end, thickness)

    # Bersaglio riappare mano-specifico
    if not target_visible:
        disappear_timer -= 1
        if disappear_timer <= 0:
            target_visible = True
            target_hand = random.choice(["Left", "Right"])
            target_color = BLUE if target_hand == "Left" else RED
            target_x = random.randint(radius, WIDTH - radius)
            target_y = random.randint(radius, HEIGHT - radius)

    # Controllo fine tempo
    if remaining_time == 0 and not game_over:
        game_over = True
        if score < MIN_SCORE_TO_PASS:
            print(f"\nProva fallita! Punteggio: {score}/{MIN_SCORE_TO_PASS}")
            show_fail_screen = True
        else:
            print(f"\nProva superata! Punteggio finale: {score}")

    # Disegna bersaglio
    if target_visible and not game_over:
        pulse = 4 * math.sin(pygame.time.get_ticks() * 0.005)
        animated_radius = int(radius + pulse)
        glow_color = tuple(min(255, c + 50) for c in target_color)
        pygame.draw.circle(screen, glow_color, (target_x, target_y), animated_radius + 12)
        pygame.draw.circle(screen, target_color, (target_x, target_y), animated_radius)
        pygame.draw.circle(screen, WHITE, (target_x, target_y), animated_radius, 3)
        if hit_effect_timer > 0:
            pygame.draw.circle(screen, GREEN, (target_x, target_y), animated_radius + 20, 4)
            hit_effect_timer -= 1

    # HUD
    hud = pygame.Surface((240, 180), pygame.SRCALPHA)
    hud.fill((255, 255, 255, 190))
    screen.blit(hud, (15, 15))
    
    # Colore del punteggio: verde se >= soglia, giallo se vicino, rosso se lontano
    if score >= MIN_SCORE_TO_PASS:
        score_color = GREEN
    elif score >= MIN_SCORE_TO_PASS - 3:
        score_color = YELLOW
    else:
        score_color = RED
    
    screen.blit(font.render(f"Punteggio: {score}/{MIN_SCORE_TO_PASS}", True, score_color), (30, 30))
    screen.blit(font.render(f"Tempo: {remaining_time}", True, DARK_TEXT), (30, 65))

    # Game over - SOLO SE SUPERATO
    if game_over and score >= MIN_SCORE_TO_PASS:
        # Overlay scuro
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Pannello più grande con bordi arrotondati
        panel_width = 700
        panel_height = 450
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (255, 255, 255, 240), (0, 0, panel_width, panel_height), border_radius=25)
        pygame.draw.rect(panel, (80, 200, 120, 200), (0, 0, panel_width, panel_height), 5, border_radius=25)
        screen.blit(panel, (WIDTH // 2 - panel_width // 2, HEIGHT // 2 - panel_height // 2))
        
        # Icona di successo
        success_font = pygame.font.SysFont("Segoe UI", 100, bold=True)
        checkmark = success_font.render("✓", True, GREEN)
        screen.blit(checkmark, (WIDTH // 2 - checkmark.get_width() // 2, HEIGHT // 2 - 180))
        
        # Titolo PROVA SUPERATA
        title_font = pygame.font.SysFont("Segoe UI", 60, bold=True)
        success_title = title_font.render("PROVA SUPERATA!", True, GREEN)
        screen.blit(success_title, (WIDTH // 2 - success_title.get_width() // 2, HEIGHT // 2 - 60))
        
        # Punteggio finale
        score_font = pygame.font.SysFont("Segoe UI", 80, bold=True)
        score_text = score_font.render(f"{score}", True, (50, 150, 80))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 30))
        
        points_label = font.render("PUNTI", True, (100, 100, 100))
        screen.blit(points_label, (WIDTH // 2 - points_label.get_width() // 2, HEIGHT // 2 + 120))
        
        # Istruzioni chiusura
        close_info = small_font.render("Premi ESC per chiudere", True, DARK_TEXT)
        screen.blit(close_info, (WIDTH // 2 - close_info.get_width() // 2, HEIGHT // 2 + 180))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    pygame.display.flip()
    clock.tick(30)

print("\nChiusura programma...")
cap.release()
pygame.quit()
print("Programma chiuso correttamente.")