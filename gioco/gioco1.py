import pygame
import random
import time
import math
import cv2
import numpy as np

pygame.init()

# -------------------------------
# DIMENSIONI FINESTRA
# -------------------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gioco Riabilitativo - Sclerosi Multipla")

font = pygame.font.SysFont("Segoe UI", 26)
large_font = pygame.font.SysFont("Segoe UI", 64, bold=True)
small_font = pygame.font.SysFont("Segoe UI", 20)
clock = pygame.time.Clock()

# -------------------------------
# COLORI
# -------------------------------
WHITE = (255, 255, 255)
RED = (255, 80, 80)
GREEN = (80, 200, 120)
BLUE = (80, 120, 255)
YELLOW = (255, 220, 80)
CYAN = (0, 255, 200)
DARK_TEXT = (40, 40, 40)

# -------------------------------
# VARIABILI CALIBRAZIONE
# -------------------------------
calibration_mode = True
calibration_samples = []
num_samples = 30
skin_lower = None
skin_upper = None

# -------------------------------
# FUNZIONI
# -------------------------------
def draw_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def random_color():
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def calibrate_skin_color(frame, x, y, size=20):
    """Campiona il colore della pelle in una regione"""
    roi = frame[max(0, y-size):min(frame.shape[0], y+size), 
                max(0, x-size):min(frame.shape[1], x+size)]
    
    if roi.size == 0:
        return None
    
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    return hsv_roi

def calculate_skin_range(samples):
    """Calcola il range HSV ottimale dai campioni"""
    if not samples:
        return None, None
    
    # Concatena tutti i campioni
    all_pixels = np.concatenate(samples, axis=0)
    all_pixels = all_pixels.reshape(-1, 3)
    
    # Calcola percentili per avere un range robusto
    h_min, s_min, v_min = np.percentile(all_pixels, 5, axis=0)
    h_max, s_max, v_max = np.percentile(all_pixels, 95, axis=0)
    
    # Espandi leggermente il range per essere più tolleranti
    h_min = max(0, h_min - 10)
    h_max = min(179, h_max + 10)
    s_min = max(0, s_min - 30)
    s_max = min(255, s_max + 30)
    v_min = max(0, v_min - 40)
    v_max = min(255, v_max + 40)
    
    lower = np.array([h_min, s_min, v_min], dtype=np.uint8)
    upper = np.array([h_max, s_max, v_max], dtype=np.uint8)
    
    return lower, upper

def detect_hand_with_contours(frame, skin_lower, skin_upper):
    """Rileva la mano usando contorni con range di colore calibrato"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Usa il range calibrato
    mask = cv2.inRange(hsv, skin_lower, skin_upper)
    
    # Applica operazioni morfologiche per ridurre il rumore
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.GaussianBlur(mask, (7, 7), 0)
    
    # Trova contorni
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, None, None, None, None
    
    # Filtra contorni per forma e dimensione
    valid_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 3000 or area > 150000:  # Dimensione ragionevole per una mano
            continue
        
        # Verifica che sia abbastanza compatto (non allungato come un braccio)
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
        circularity = 4 * math.pi * area / (perimeter * perimeter)
        
        # La mano dovrebbe avere una circolarità ragionevole
        if circularity > 0.2:
            valid_contours.append(cnt)
    
    if not valid_contours:
        return None, None, None, None, None
    
    # Prendi il contorno più grande tra quelli validi
    hand_contour = max(valid_contours, key=cv2.contourArea)
    area = cv2.contourArea(hand_contour)
    
    # Calcola il centro della mano
    M = cv2.moments(hand_contour)
    if M["m00"] == 0:
        return None, None, None, None, None
    
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    
    # Calcola il convex hull e i difetti di convessità
    hull = cv2.convexHull(hand_contour, returnPoints=False)
    
    # Trova i difetti (spazi tra le dita)
    defects = None
    if len(hull) > 3:
        try:
            defects = cv2.convexityDefects(hand_contour, hull)
        except:
            pass
    
    # Conta le dita approssimative usando i difetti
    finger_count = 0
    finger_tips = []
    
    if defects is not None:
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(hand_contour[s][0])
            end = tuple(hand_contour[e][0])
            far = tuple(hand_contour[f][0])
            
            # Calcola le lunghezze dei lati del triangolo
            a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
            
            # Calcola l'angolo usando la legge del coseno
            if b * c != 0:
                angle = math.acos(max(-1, min(1, (b**2 + c**2 - a**2) / (2 * b * c))))
                
                # Se l'angolo è minore di 90 gradi, conta come un dito
                if angle <= math.pi / 2:
                    finger_count += 1
                    finger_tips.append(far)
    
    # Trova i punti più alti (punte delle dita superiori)
    hull_points = cv2.convexHull(hand_contour, returnPoints=True)
    extreme_points = []
    
    # Trova il punto più alto
    topmost = tuple(hull_points[hull_points[:, :, 1].argmin()][0])
    extreme_points.append(topmost)
    
    # Determina se la mano è chiusa o aperta
    hull_area = cv2.contourArea(cv2.convexHull(hand_contour))
    solidity = float(area) / hull_area if hull_area > 0 else 0
    
    # Se la solidità è alta (>0.8), la mano è più chiusa
    is_closed = solidity > 0.8 or finger_count < 2
    
    return hand_contour, (cx, cy), is_closed, hull_points, extreme_points

# -------------------------------
# VARIABILI DI GIOCO
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

# Trail della mano (scia di movimento)
hand_trail = []
max_trail_length = 20

# -------------------------------
# CAMERA
# -------------------------------
cap = cv2.VideoCapture(0)

# -------------------------------
# CALIBRAZIONE
# -------------------------------
calibration_done = False
while not calibration_done:
    ret, frame = cap.read()
    if not ret:
        continue
    
    frame = cv2.flip(frame, 1)
    frame_height, frame_width = frame.shape[:2]
    
    # Converti per Pygame
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
    frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    screen.blit(frame_surface, (0, 0))
    
    # Overlay scuro per istruzioni
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    # Quadrato di calibrazione al centro
    cal_size = 100
    cal_x = WIDTH // 2 - cal_size // 2
    cal_y = HEIGHT // 2 - cal_size // 2
    
    # Disegna il quadrato
    pygame.draw.rect(screen, GREEN, (cal_x, cal_y, cal_size, cal_size), 4)
    
    # Istruzioni
    title = large_font.render("Calibrazione", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    
    instruction1 = font.render("Posiziona la mano nel quadrato verde", True, WHITE)
    screen.blit(instruction1, (WIDTH // 2 - instruction1.get_width() // 2, 150))
    
    instruction2 = font.render("Premi SPAZIO per calibrare", True, YELLOW)
    screen.blit(instruction2, (WIDTH // 2 - instruction2.get_width() // 2, HEIGHT - 100))
    
    # Mostra progresso
    progress_text = small_font.render(f"Campioni: {len(calibration_samples)}/{num_samples}", True, WHITE)
    screen.blit(progress_text, (WIDTH // 2 - progress_text.get_width() // 2, HEIGHT - 50))
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Campiona il colore della pelle
                # Converti coordinate Pygame -> OpenCV
                frame_cal_x = int((cal_x + cal_size // 2) * frame_width / WIDTH)
                frame_cal_y = int((cal_y + cal_size // 2) * frame_height / HEIGHT)
                
                sample = calibrate_skin_color(frame, frame_cal_y, frame_cal_x, size=30)
                if sample is not None:
                    calibration_samples.append(sample)
                
                # Se abbiamo abbastanza campioni, calcola il range
                if len(calibration_samples) >= num_samples:
                    skin_lower, skin_upper = calculate_skin_range(calibration_samples)
                    if skin_lower is not None:
                        calibration_done = True

# -------------------------------
# SCHERMATA ISTRUZIONI
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
        "",
        "Durata: 60 secondi.",
        "",
        "Premi un tasto per iniziare."
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
# COUNTDOWN
# -------------------------------
for i in range(3, 0, -1):
    draw_gradient(screen, (240, 245, 255), (200, 220, 255))
    txt = large_font.render(str(i), True, RED)
    screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(1000)

start_time = time.time()

# -------------------------------
# CICLO PRINCIPALE
# -------------------------------
while running:
    current_time = time.time()
    elapsed_time = current_time - start_time
    remaining_time = max(0, int(game_duration - elapsed_time))

    ret, frame = cap.read()
    if not ret:
        continue
    
    frame = cv2.flip(frame, 1)
    frame_height, frame_width = frame.shape[:2]
    
    # Rileva la mano con calibrazione
    contour, center, is_closed, hull_points, extreme_points = detect_hand_with_contours(frame, skin_lower, skin_upper)
    
    # Converti frame per Pygame
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
    frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    screen.blit(frame_surface, (0, 0))

    # Eventi Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Variabili per visualizzazione
    hand_center_pygame = None
    
    # Se la mano è rilevata, disegna i dettagli
    if contour is not None and center is not None:
        # Scala le coordinate al sistema Pygame
        scale_x = WIDTH / frame_width
        scale_y = HEIGHT / frame_height
        
        # Centro della mano
        hand_x = int(center[0] * scale_x)
        hand_y = int(center[1] * scale_y)
        hand_center_pygame = (hand_x, hand_y)
        
        # Aggiungi alla scia
        hand_trail.append(hand_center_pygame)
        if len(hand_trail) > max_trail_length:
            hand_trail.pop(0)
        
        # Disegna il contorno della mano (linea che segue il profilo)
        scaled_contour = []
        for point in contour:
            px = int(point[0][0] * scale_x)
            py = int(point[0][1] * scale_y)
            scaled_contour.append((px, py))
        
        if len(scaled_contour) > 2:
            pygame.draw.lines(screen, BLUE, True, scaled_contour, 3)
        
        # Disegna il convex hull
        if hull_points is not None and len(hull_points) > 2:
            scaled_hull = []
            for point in hull_points:
                px = int(point[0][0] * scale_x)
                py = int(point[0][1] * scale_y)
                scaled_hull.append((px, py))
            pygame.draw.lines(screen, GREEN, True, scaled_hull, 2)
        
        # Disegna i punti estremi (punte delle dita)
        if extreme_points:
            for point in extreme_points:
                px = int(point[0] * scale_x)
                py = int(point[1] * scale_y)
                pygame.draw.circle(screen, YELLOW, (px, py), 10)
                pygame.draw.circle(screen, WHITE, (px, py), 10, 2)
        
        # Disegna il centro della mano
        pygame.draw.circle(screen, RED, hand_center_pygame, 12)
        pygame.draw.circle(screen, WHITE, hand_center_pygame, 12, 3)
        
        # Disegna pallini lungo il contorno
        sample_rate = max(1, len(scaled_contour) // 15)
        for i in range(0, len(scaled_contour), sample_rate):
            point = scaled_contour[i]
            pygame.draw.circle(screen, CYAN, point, 5)
    
    # Disegna la scia di movimento
    if len(hand_trail) > 1:
        for i in range(len(hand_trail) - 1):
            alpha_ratio = i / len(hand_trail)
            thickness = int(2 + 4 * alpha_ratio)
            
            start_point = hand_trail[i]
            end_point = hand_trail[i + 1]
            
            color_intensity = int(255 * alpha_ratio)
            trail_color = (0, color_intensity, 255 - color_intensity)
            
            pygame.draw.line(screen, trail_color, start_point, end_point, thickness)

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

    # Gestisci riapparizione del bersaglio
    if not target_visible:
        disappear_timer -= 1
        if disappear_timer <= 0:
            target_visible = True
            target_color = random_color()
            target_x = random.randint(radius, WIDTH - radius)
            target_y = random.randint(radius, HEIGHT - radius)

    # Aggiorna game_over se tempo finito
    if remaining_time == 0 and not game_over:
        game_over = True

    # Disegna bersaglio solo se visibile
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

    # Indicatore mano chiusa
    if is_closed:
        indicator = font.render("MANO CHIUSA", True, RED)
        screen.blit(indicator, (WIDTH - 220, 30))

    # Game Over
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