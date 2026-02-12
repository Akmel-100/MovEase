import pygame
import random
import time
import math
import cv2
import mediapipe as mp

# -------------------------------
# Inizializzazione Pygame
# -------------------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
def is_hand_closed(landmarks):
    # Usa i landmarks per determinare se la mano è chiusa
    index_tip = landmarks[8]
    index_mcp = landmarks[5]
    middle_tip = landmarks[12]
    middle_mcp = landmarks[9]
    ring_tip = landmarks[16]
    ring_mcp = landmarks[13]
    pinky_tip = landmarks[20]
    pinky_mcp = landmarks[17]

    # Se tutte le dita chiuse (tipy > mcp y), mano chiusa
    closed = (index_tip.y > index_mcp.y and middle_tip.y > middle_mcp.y and
              ring_tip.y > ring_mcp.y and pinky_tip.y > pinky_mcp.y)
    return closed

# -------------------------------
# Variabili di gioco
# -------------------------------
score = 0
radius = 40
game_duration = 60

target_x = random.randint(radius, WIDTH - radius)
target_y = random.randint(radius, HEIGHT - radius)
target_color = random_color()
hit_effect_timer = 0
target_visible = True
disappear_timer = 0
running = True
game_over = False
hand_trail = []
max_trail_length = 20

# -------------------------------
# MediaPipe HandLandmarker setup
# -------------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

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
        "Il gioco traccia i movimenti della tua mano.",
        "Ogni centro aumenta il punteggio.",
        "Il bersaglio diventa più piccolo col tempo.",
        "", "Durata: 60 secondi.", "", "Premi un tasto per iniziare."
    ]
    for i, line in enumerate(instructions):
        text = font.render(line, True, DARK_TEXT)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 180 + i * 35))
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); exit()
        if event.type == pygame.KEYDOWN:
            show_instructions = False

# -------------------------------
# Countdown
# -------------------------------
for i in range(3, 0, -1):
    draw_gradient(screen, (240, 245, 255), (200, 220, 255))
    txt = large_font.render(str(i), True, RED)
    screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(1000)

start_time = time.time()

# -------------------------------
# Ciclo principale
# -------------------------------
while running:
    current_time = time.time()
    elapsed_time = current_time - start_time
    remaining_time = max(0, int(game_duration - elapsed_time))

    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    screen_frame = cv2.resize(frame, (WIDTH, HEIGHT))
    screen_frame = cv2.cvtColor(screen_frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(screen_frame.swapaxes(0, 1))
    screen.blit(frame_surface, (0, 0))

    hand_center_pygame = None

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Calcola centro mano come media dei landmarks
            x = sum([lm.x for lm in hand_landmarks.landmark]) / len(hand_landmarks.landmark)
            y = sum([lm.y for lm in hand_landmarks.landmark]) / len(hand_landmarks.landmark)
            hand_center_pygame = (int(x * WIDTH), int(y * HEIGHT))

            hand_trail.append(hand_center_pygame)
            if len(hand_trail) > max_trail_length:
                hand_trail.pop(0)

            # Disegna landmarks
            for lm in hand_landmarks.landmark:
                px, py = int(lm.x * WIDTH), int(lm.y * HEIGHT)
                pygame.draw.circle(screen, CYAN, (px, py), 5)

            # Determina se mano chiusa
            is_closed = is_hand_closed(hand_landmarks.landmark)

    else:
        is_closed = False

    # Disegna scia mano
    if len(hand_trail) > 1:
        for i in range(len(hand_trail)-1):
            start = hand_trail[i]
            end = hand_trail[i+1]
            alpha_ratio = i / len(hand_trail)
            thickness = int(2 + 4 * alpha_ratio)
            color_intensity = int(255 * alpha_ratio)
            trail_color = (0, color_intensity, 255 - color_intensity)
            pygame.draw.line(screen, trail_color, start, end, thickness)

    # Controlla mano chiusa sopra bersaglio
    if is_closed and target_visible and hand_center_pygame:
        distance = math.hypot(hand_center_pygame[0] - target_x, hand_center_pygame[1] - target_y)
        if distance <= radius:
            score += 1
            hit_effect_timer = 8
            target_visible = False
            disappear_timer = 30
            if radius > 20:
                radius -= 1
            hand_trail.clear()

    # Gestisci riapparizione bersaglio
    if not target_visible:
        disappear_timer -= 1
        if disappear_timer <= 0:
            target_visible = True
            target_color = random_color()
            target_x = random.randint(radius, WIDTH - radius)
            target_y = random.randint(radius, HEIGHT - radius)

    # Game over
    if remaining_time == 0 and not game_over:
        game_over = True

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
    hud = pygame.Surface((240, 140), pygame.SRCALPHA)
    hud.fill((255, 255, 255, 190))
    screen.blit(hud, (15, 15))
    screen.blit(font.render(f"Punteggio: {score}", True, DARK_TEXT), (30, 30))
    screen.blit(font.render(f"Tempo: {remaining_time}", True, DARK_TEXT), (30, 100))

    if is_closed:
        indicator = font.render("MANO CHIUSA", True, RED)
        screen.blit(indicator, (WIDTH - 220, 30))

    if game_over:
        panel = pygame.Surface((500, 300), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 220))
        screen.blit(panel, (WIDTH // 2 - 250, HEIGHT // 2 - 150))
        screen.blit(large_font.render(f"Score: {score}", True, GREEN), (WIDTH // 2 - 100, HEIGHT // 2 - 20))
        screen.blit(large_font.render("Fine Gioco", True, RED), (WIDTH // 2 - 150, HEIGHT // 2 - 80))

    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.quit()
