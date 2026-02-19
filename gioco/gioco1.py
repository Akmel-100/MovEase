import pygame                          # Libreria per la grafica e la gestione degli eventi
import random                          # Libreria per generare numeri e scelte casuali
import time                            # Libreria per gestire il tempo (timer di gioco)
import math                            # Libreria per calcoli matematici (distanze, seno per animazioni)
import cv2                             # Libreria per la gestione della webcam
import mediapipe as mp                 # Libreria Google per il riconoscimento delle mani

# -------------------------------
# Inizializzazione Pygame (FULLSCREEN)
# -------------------------------
pygame.init()                                                        # Inizializza tutti i moduli di pygame
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)          # Crea la finestra a schermo intero
WIDTH, HEIGHT = screen.get_size()                                    # Ottiene la risoluzione dello schermo
pygame.display.set_caption("Rehabilitation Game - MediaPipe")        # Imposta il titolo della finestra
font = pygame.font.SysFont("Segoe UI", 26)                           # Font standard per testi normali
large_font = pygame.font.SysFont("Segoe UI", 64, bold=True)          # Font grande per titoli
small_font = pygame.font.SysFont("Segoe UI", 20)                     # Font piccolo per testi secondari
clock = pygame.time.Clock()                                          # Oggetto per controllare i FPS

# -------------------------------
# Colori
# -------------------------------
WHITE = (255, 255, 255)                # Bianco
RED = (255, 80, 80)                    # Rosso (mano destra)
GREEN = (80, 200, 120)                 # Verde (feedback positivo)
BLUE = (80, 120, 255)                  # Blu (mano sinistra)
YELLOW = (255, 220, 80)                # Giallo (avvisi)
CYAN = (0, 255, 200)                   # Ciano (non utilizzato attivamente)
DARK_TEXT = (40, 40, 40)               # Grigio scuro per i testi

# -------------------------------
# Soglia chiusura mano e punteggio minimo
# -------------------------------
HAND_CLOSURE_THRESHOLD = 20            # Percentuale minima (0-100) per considerare la mano chiusa
MIN_SCORE_TO_PASS = 10                 # Punteggio minimo per superare la prova

# -------------------------------
# Funzioni utility
# -------------------------------
def random_color():
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))  # Genera un colore RGB casuale

def draw_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):                                                             # Itera su ogni riga verticale dello schermo
        ratio = y / HEIGHT                                                              # Calcola il rapporto di interpolazione (0.0 in alto, 1.0 in basso)
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)                 # Interpola il canale rosso
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)                 # Interpola il canale verde
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)                 # Interpola il canale blu
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))                       # Disegna una linea orizzontale del colore calcolato

# -------------------------------
# Funzioni Gesture MediaPipe
# -------------------------------
def calculate_hand_closure(landmarks):
    fingers_data = [
        (8, 5, 6),    # indice:  punta (8), nocca (5), articolazione media (6)
        (12, 9, 10),  # medio:   punta (12), nocca (9), articolazione media (10)
        (16, 13, 14), # anulare: punta (16), nocca (13), articolazione media (14)
        (20, 17, 18)  # mignolo: punta (20), nocca (17), articolazione media (18)
    ]
    total_closure = 0.0                                                    # Accumulatore della chiusura totale
    for tip_idx, mcp_idx, pip_idx in fingers_data:                        # Per ogni dito
        tip = landmarks[tip_idx]                                           # Punto della punta del dito
        mcp = landmarks[mcp_idx]                                           # Punto della nocca
        pip = landmarks[pip_idx]                                           # Punto dell'articolazione media (non usato nel calcolo)
        vertical_distance = tip.y - mcp.y                                  # Distanza verticale tra punta e nocca (positiva = dito abbassato)
        if vertical_distance > -0.05:                                      # Se il dito non è completamente esteso verso l'alto
            closure_amount = min(1.0, (vertical_distance + 0.05) / 0.15)  # Calcola quanto è chiuso il dito (0.0 = aperto, 1.0 = chiuso)
            total_closure += closure_amount                                # Aggiunge al totale
    avg_closure = (total_closure / 4.0) * 100                             # Media della chiusura delle 4 dita, convertita in percentuale
    if avg_closure < 30:                                                   # Se la chiusura è bassa
        avg_closure = avg_closure * 1.5                                    # Amplifica il valore per una maggiore sensibilità
    return min(100, int(avg_closure))                                      # Restituisce il valore finale tra 0 e 100

def is_hand_closed(landmarks, threshold=HAND_CLOSURE_THRESHOLD):
    closure = calculate_hand_closure(landmarks)                            # Calcola la percentuale di chiusura
    return closure >= threshold                                            # Restituisce True se supera la soglia

# -------------------------------
# Funzione per generare posizione bersaglio in base alla mano
# I pallini BLU (mano sinistra) appaiono nella metà SINISTRA dello schermo
# I pallini ROSSI (mano destra) appaiono nella metà DESTRA dello schermo
# -------------------------------
def new_target_position(hand_label, r):
    if hand_label == "Left":                                               # Se il bersaglio è per la mano sinistra
        x = random.randint(r, WIDTH // 2 - r)                             # Posizione X nella metà sinistra dello schermo
    else:                                                                  # Se il bersaglio è per la mano destra
        x = random.randint(WIDTH // 2 + r, WIDTH - r)                     # Posizione X nella metà destra dello schermo
    y = random.randint(r, HEIGHT - r)                                      # Posizione Y casuale su tutta l'altezza
    return x, y                                                            # Restituisce le coordinate del bersaglio

# -------------------------------
# Funzione per inizializzare il gioco
# -------------------------------
def init_game():
    global score, targets_hit_count, radius, target_x, target_y, target_hand, target_color
    global hit_effect_timer, target_visible, disappear_timer, game_over, hand_trails, start_time
    
    score = 0                                              # Azzera il punteggio
    targets_hit_count = 0                                  # Azzera il contatore dei bersagli colpiti
    radius = 40                                            # Imposta il raggio iniziale del bersaglio
    
    target_hand = random.choice(["Left", "Right"])         # Sceglie casualmente quale mano deve colpire il primo bersaglio
    target_x, target_y = new_target_position(target_hand, radius)  # Genera la posizione del primo bersaglio
    target_color = BLUE if target_hand == "Left" else RED  # Blu per sinistra, rosso per destra
    hit_effect_timer = 0                                   # Timer per l'effetto visivo al colpo (0 = nessun effetto)
    target_visible = True                                  # Il bersaglio è visibile all'inizio
    disappear_timer = 0                                    # Timer per il ritardo prima che appaia il prossimo bersaglio
    game_over = False                                      # Il gioco non è terminato
    hand_trails = {"Left": [], "Right": []}                # Scie delle mani (non disegnate ma mantenute)
    start_time = time.time()                               # Registra il momento di inizio della partita

# -------------------------------
# Variabili di gioco
# -------------------------------
game_duration = 60                     # Durata della partita in secondi
running = True                         # Controlla il loop principale del gioco
init_game()                            # Inizializza tutte le variabili di gioco

# -------------------------------
# MediaPipe setup
# -------------------------------
mp_hands = mp.solutions.hands                              # Carica il modulo di rilevamento mani di MediaPipe
hands = mp_hands.Hands(static_image_mode=False,           # Modalità video (non immagini statiche)
                       max_num_hands=2,                    # Rileva fino a 2 mani contemporaneamente
                       min_detection_confidence=0.5,       # Confidenza minima per rilevare una mano (0-1)
                       min_tracking_confidence=0.5)        # Confidenza minima per tracciare una mano già rilevata (0-1)

# -------------------------------
# CONTROLLO WEBCAM CON DIAGNOSTICA
# -------------------------------
print("=" * 50)
print("WEBCAM DIAGNOSTICS")
print("=" * 50)

cap = cv2.VideoCapture(0)              # Tenta di aprire la webcam predefinita (indice 0)

if not cap.isOpened():                 # Se la webcam non si è aperta
    print("ERRORE: Impossibile aprire la webcam!")
    print("Possibili cause:")
    print("- La webcam è usata da un altro programma")
    print("- Driver della webcam non funzionanti")
    print("- Permessi non concessi")
    print("\nProvo con webcam indice 1...")
    
    cap = cv2.VideoCapture(1)          # Prova con la seconda webcam (indice 1)
    if not cap.isOpened():             # Se anche questa non funziona
        print("ERRORE: Nessuna webcam disponibile!")
        pygame.quit()                  # Chiude pygame
        exit()                         # Termina il programma

print(f"✓ Webcam aperta correttamente")
print(f"  Larghezza: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")   # Stampa la larghezza del frame webcam
print(f"  Altezza: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")    # Stampa l'altezza del frame webcam
print(f"  FPS: {cap.get(cv2.CAP_PROP_FPS)}")                 # Stampa gli FPS della webcam

ret, test_frame = cap.read()           # Legge un frame di test dalla webcam
if not ret:                            # Se la lettura è fallita
    print("ERRORE: Impossibile leggere dalla webcam!")
    cap.release()                      # Rilascia la webcam
    pygame.quit()                      # Chiude pygame
    exit()                             # Termina il programma

print(f"Frame di test letto correttamente: {test_frame.shape}")   # Stampa le dimensioni del frame (altezza, larghezza, canali)
print("=" * 50)
print()

# -------------------------------
# Schermata istruzioni
# -------------------------------
show_instructions = True                                               # Flag per mostrare le istruzioni
while show_instructions:                                               # Loop finché le istruzioni sono visibili
    draw_gradient(screen, (240, 245, 255), (200, 220, 255))            # Disegna lo sfondo sfumato
    title = large_font.render("Instructions", True, DARK_TEXT)           # Renderizza il titolo
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))     # Disegna il titolo centrato
    instructions = [
        "Close your hand over the target to hit it.",
        "LEFT Hand (BLUE) → hit LEFT of screen",
        "RIGHT Hand (RED) → hit to the RIGHT of the screen",
        "", 
        "Duration: 60 seconds.", 
        f"Minimum score to exceed: {MIN_SCORE_TO_PASS} point",
        "If you don't reach the minimum score, try again!",
        "",
        "Press a key to get started."
    ]
    for i, line in enumerate(instructions):                            # Per ogni riga di testo
        text = font.render(line, True, DARK_TEXT)                      # Renderizza la riga
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 170 + i * 35))  # La disegna centrata, spaziata verticalmente
    pygame.display.flip()                                              # Aggiorna lo schermo
    for event in pygame.event.get():                                   # Controlla gli eventi
        if event.type == pygame.QUIT:                                  # Se si chiude la finestra
            cap.release()                                              # Rilascia la webcam
            pygame.quit()                                              # Chiude pygame
            exit()                                                     # Termina il programma
        if event.type == pygame.KEYDOWN:                               # Se si preme un tasto qualsiasi
            show_instructions = False                                  # Esce dal loop delle istruzioni
            start_time = time.time()                                   # Il timer parte solo ora, quando l'utente è pronto

# -------------------------------
# Variabili per gestire il restart
# -------------------------------
show_fail_screen = False               # Flag per mostrare la schermata di fallimento
fail_screen_timer = 0                  # Contatore di frame per il timer della schermata di fallimento

# -------------------------------
# Ciclo principale del gioco
# -------------------------------
frame_count = 0                        # Contatore dei frame elaborati
failed_frames = 0                      # Contatore dei frame webcam non letti correttamente

print("Start of game...")
while running:                         # Loop principale (gira finché running è True)
    
    # -------------------------------
    # Schermata di fallimento
    # -------------------------------
    if show_fail_screen:                                               # Se si deve mostrare la schermata di fallimento
        draw_gradient(screen, (255, 200, 200), (255, 150, 150))        # Sfondo rosato per il fallimento
        
        panel = pygame.Surface((700, 450), pygame.SRCALPHA)            # Crea un pannello semi-trasparente
        panel.fill((255, 255, 255, 230))                               # Riempie il pannello di bianco semi-trasparente
        screen.blit(panel, (WIDTH // 2 - 350, HEIGHT // 2 - 225))     # Disegna il pannello centrato
        
        fail_title = large_font.render("FAILED TEST!", True, RED)    # Renderizza il titolo di fallimento
        screen.blit(fail_title, (WIDTH // 2 - fail_title.get_width() // 2, HEIGHT // 2 - 150))  # Disegna il titolo centrato
        
        score_text = font.render(f"Score obtained: {score}", True, DARK_TEXT)               # Mostra il punteggio ottenuto
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 60))
        
        required_text = font.render(f"Required score: {MIN_SCORE_TO_PASS}", True, DARK_TEXT)  # Mostra il punteggio richiesto
        screen.blit(required_text, (WIDTH // 2 - required_text.get_width() // 2, HEIGHT // 2 - 20))
        
        retry_text = large_font.render("TRY AGAIN!", True, YELLOW)       # Messaggio di riprova in giallo
        screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2 + 50))
        
        countdown_sec = max(0, 3 - (fail_screen_timer // 30))          # Calcola i secondi rimanenti (30 frame = 1 secondo a 30 FPS)
        countdown_text = small_font.render(f"Restart in {countdown_sec} second...", True, DARK_TEXT)  # Testo countdown
        screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 + 140))
        
        pygame.display.flip()                                          # Aggiorna lo schermo
        fail_screen_timer += 1                                         # Incrementa il timer
        
        if fail_screen_timer >= 90:                                    # Dopo 90 frame (3 secondi a 30 FPS)
            show_fail_screen = False                                   # Nasconde la schermata di fallimento
            fail_screen_timer = 0                                      # Azzera il timer
            init_game()                                                # Reinizializza il gioco
            
            for i in range(3, 0, -1):                                  # Countdown 3, 2, 1
                draw_gradient(screen, (240, 245, 255), (200, 220, 255))  # Sfondo del countdown
                txt = large_font.render(str(i), True, RED)             # Renderizza il numero
                screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2))  # Disegna centrato
                pygame.display.flip()                                  # Aggiorna lo schermo
                pygame.time.delay(1000)                                # Aspetta 1 secondo
            start_time = time.time()                                   # Il timer riparte solo dopo il countdown
        
        for event in pygame.event.get():                               # Controlla gli eventi durante la schermata di fallimento
            if event.type == pygame.QUIT:                              # Se si chiude la finestra
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # Se si preme ESC
                running = False
        
        clock.tick(30)                                                 # Limita a 30 FPS
        continue                                                       # Salta il resto del loop e ricomincia dall'inizio
    
    # -------------------------------
    # Gioco normale
    # -------------------------------
    current_time = time.time()                                         # Tempo corrente in secondi
    elapsed_time = current_time - start_time                           # Tempo trascorso dall'inizio della partita
    remaining_time = max(0, int(game_duration - elapsed_time))         # Tempo rimanente (non va sotto 0)
    frame_count += 1                                                   # Incrementa il contatore dei frame

    ret, frame = cap.read()                                            # Legge un frame dalla webcam
    if not ret:                                                        # Se la lettura è fallita
        failed_frames += 1                                             # Incrementa il contatore degli errori
        print(f"Unread frame! (Total errors: {failed_frames})")
        
        if failed_frames > 30:                                         # Se ci sono troppi errori consecutivi
            print("CRITICAL ERROR: Too many frames lost!")
            running = False                                            # Ferma il gioco
            break
        
        pygame.time.wait(100)                                          # Aspetta 100ms prima di riprovare
        continue                                                       # Salta questo frame
    
    failed_frames = 0                                                  # Azzera il contatore degli errori (frame letto con successo)

    frame = cv2.flip(frame, 1)                                         # Specchia il frame orizzontalmente (effetto specchio)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)                 # Converte da BGR (OpenCV) a RGB (MediaPipe)
    result = hands.process(rgb_frame)                                  # Elabora il frame con MediaPipe per rilevare le mani

    screen_frame = cv2.resize(frame, (WIDTH, HEIGHT))                  # Ridimensiona il frame alle dimensioni dello schermo
    screen_frame = cv2.cvtColor(screen_frame, cv2.COLOR_BGR2RGB)       # Converte i colori per pygame
    frame_surface = pygame.surfarray.make_surface(screen_frame.swapaxes(0, 1))  # Converte l'array numpy in superficie pygame
    screen.blit(frame_surface, (0, 0))                                 # Disegna il frame della webcam come sfondo

    hand_positions = {"Left": None, "Right": None}                    # Dizionario per le posizioni delle mani (None = non rilevata)
    hand_closed_status = {"Left": False, "Right": False}              # Dizionario per lo stato di chiusura delle mani

    if result.multi_hand_landmarks and result.multi_handedness:        # Se MediaPipe ha rilevato almeno una mano
        for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):  # Per ogni mano rilevata
            hand_label = handedness.classification[0].label            # Ottiene l'etichetta ("Left" o "Right")
            x = sum([lm.x for lm in hand_landmarks.landmark]) / len(hand_landmarks.landmark)  # Calcola la X media della mano (0-1)
            y = sum([lm.y for lm in hand_landmarks.landmark]) / len(hand_landmarks.landmark)  # Calcola la Y media della mano (0-1)
            hand_center_pygame = (int(x * WIDTH), int(y * HEIGHT))    # Converte le coordinate normalizzate in pixel
            hand_positions[hand_label] = hand_center_pygame            # Salva la posizione della mano

            hand_trails.setdefault(hand_label, []).append(hand_center_pygame)  # Aggiunge la posizione alla scia della mano
            if len(hand_trails[hand_label]) > 20:                      # Se la scia supera 20 punti
                hand_trails[hand_label].pop(0)                         # Rimuove il punto più vecchio

            closure_value = calculate_hand_closure(hand_landmarks.landmark)  # Calcola la percentuale di chiusura (non usata direttamente)
            hand_closed_status[hand_label] = is_hand_closed(hand_landmarks.landmark, HAND_CLOSURE_THRESHOLD)  # True se la mano è chiusa

            color = BLUE if hand_label == "Left" else RED              # Blu per la mano sinistra, rosso per la destra
            for lm in hand_landmarks.landmark:                         # Per ogni punto della mano (21 totali)
                px, py = int(lm.x * WIDTH), int(lm.y * HEIGHT)        # Converte le coordinate in pixel
                pygame.draw.circle(screen, color, (px, py), 5)        # Disegna un cerchio colorato su ogni punto

            # Controllo bersaglio mano-specifico
            if hand_closed_status[hand_label] and target_visible and hand_label == target_hand:  # Se la mano corretta è chiusa e il bersaglio è visibile
                distance = math.hypot(hand_center_pygame[0] - target_x, hand_center_pygame[1] - target_y)  # Calcola la distanza tra centro della mano e bersaglio
                if distance <= radius:                                 # Se la mano è dentro il bersaglio
                    score += 1                                         # Incrementa il punteggio
                    targets_hit_count += 1                             # Incrementa il contatore dei bersagli colpiti
                    hit_effect_timer = 8                               # Attiva l'effetto visivo per 8 frame
                    target_visible = False                             # Nasconde il bersaglio
                    disappear_timer = 30                               # Aspetta 30 frame prima di far apparire il prossimo
                    if radius > 20:                                    # Se il raggio è maggiore di 20
                        radius -= 1                                    # Riduce leggermente il bersaglio (aumenta la difficoltà)

    # Scia RIMOSSA — il trail non viene più disegnato

    if not target_visible:                                             # Se il bersaglio non è visibile
        disappear_timer -= 1                                           # Decrementa il timer
        if disappear_timer <= 0:                                       # Quando il timer arriva a zero
            target_visible = True                                      # Rende il bersaglio visibile
            target_hand = random.choice(["Left", "Right"])             # Sceglie casualmente la prossima mano
            target_color = BLUE if target_hand == "Left" else RED      # Imposta il colore del bersaglio
            target_x, target_y = new_target_position(target_hand, radius)  # Genera la nuova posizione

    if remaining_time == 0 and not game_over:                          # Se il tempo è scaduto e il gioco non è ancora terminato
        game_over = True                                               # Segna il gioco come terminato
        if score < MIN_SCORE_TO_PASS:                                  # Se il punteggio è insufficiente
            print(f"\nTrial failed! Score: {score}/{MIN_SCORE_TO_PASS}")
            show_fail_screen = True                                    # Mostra la schermata di fallimento
        else:                                                          # Se il punteggio è sufficiente
            print(f"\nTest passed! Final score: {score}")

    if target_visible and not game_over:                               # Se il bersaglio è visibile e il gioco è in corso
        pulse = 4 * math.sin(pygame.time.get_ticks() * 0.005)         # Calcola una variazione sinusoidale per l'animazione pulsante
        animated_radius = int(radius + pulse)                          # Applica la pulsazione al raggio
        glow_color = tuple(min(255, c + 50) for c in target_color)    # Colore più chiaro per il bagliore esterno
        pygame.draw.circle(screen, glow_color, (target_x, target_y), animated_radius + 12)  # Disegna il bagliore esterno
        pygame.draw.circle(screen, target_color, (target_x, target_y), animated_radius)     # Disegna il bersaglio principale
        pygame.draw.circle(screen, WHITE, (target_x, target_y), animated_radius, 3)         # Disegna il bordo bianco
        if hit_effect_timer > 0:                                       # Se l'effetto colpo è attivo
            pygame.draw.circle(screen, GREEN, (target_x, target_y), animated_radius + 20, 4)  # Disegna l'anello verde del colpo
            hit_effect_timer -= 1                                      # Decrementa il timer dell'effetto

    # HUD (Head-Up Display - pannello informazioni)
    hud = pygame.Surface((240, 180), pygame.SRCALPHA)                  # Crea una superficie semi-trasparente per l'HUD
    hud.fill((255, 255, 255, 190))                                     # Riempie l'HUD di bianco semi-trasparente
    screen.blit(hud, (15, 15))                                         # Disegna l'HUD in alto a sinistra
    
    if score >= MIN_SCORE_TO_PASS:                                     # Se il punteggio ha superato il minimo
        score_color = GREEN                                            # Testo verde
    elif score >= MIN_SCORE_TO_PASS - 3:                               # Se mancano 3 punti al minimo
        score_color = YELLOW                                           # Testo giallo (avviso)
    else:                                                              # Se il punteggio è basso
        score_color = RED                                              # Testo rosso
    
    screen.blit(font.render(f"Score: {score}/{MIN_SCORE_TO_PASS}", True, score_color), (30, 30))  # Mostra punteggio con colore dinamico
    screen.blit(font.render(f"Time: {remaining_time}", True, DARK_TEXT), (30, 65))                   # Mostra il tempo rimanente

    if game_over and score >= MIN_SCORE_TO_PASS:                       # Se il gioco è terminato con successo
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)     # Crea un overlay scuro su tutto lo schermo
        overlay.fill((0, 0, 0, 150))                                   # Riempie di nero semi-trasparente
        screen.blit(overlay, (0, 0))                                   # Disegna l'overlay
        
        panel_width = 700
        panel_height = 450
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)  # Crea il pannello del risultato
        pygame.draw.rect(panel, (255, 255, 255, 240), (0, 0, panel_width, panel_height), border_radius=25)   # Rettangolo bianco arrotondato
        pygame.draw.rect(panel, (80, 200, 120, 200), (0, 0, panel_width, panel_height), 5, border_radius=25)  # Bordo verde
        screen.blit(panel, (WIDTH // 2 - panel_width // 2, HEIGHT // 2 - panel_height // 2))                 # Disegna il pannello centrato
        
        success_font = pygame.font.SysFont("Segoe UI", 100, bold=True)
        checkmark = success_font.render("✓", True, GREEN)              # Renderizza il segno di spunta verde
        screen.blit(checkmark, (WIDTH // 2 - checkmark.get_width() // 2, HEIGHT // 2 - 180))  # Disegna il segno di spunta
        
        title_font = pygame.font.SysFont("Segoe UI", 60, bold=True)
        success_title = title_font.render("TEST PASSED!", True, GREEN)  # Titolo di successo
        screen.blit(success_title, (WIDTH // 2 - success_title.get_width() // 2, HEIGHT // 2 - 60))
        
        score_font = pygame.font.SysFont("Segoe UI", 80, bold=True)
        score_text = score_font.render(f"{score}", True, (50, 150, 80))    # Punteggio finale in grande
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 30))
        
        points_label = font.render("POINT", True, (100, 100, 100))         # Etichetta "PUNTI" sotto il numero
        screen.blit(points_label, (WIDTH // 2 - points_label.get_width() // 2, HEIGHT // 2 + 120))
        
        close_info = small_font.render("ESC Presses to Close", True, DARK_TEXT)  # Istruzione per chiudere
        screen.blit(close_info, (WIDTH // 2 - close_info.get_width() // 2, HEIGHT // 2 + 180))

    for event in pygame.event.get():                                   # Controlla gli eventi pygame
        if event.type == pygame.QUIT:                                  # Se si chiude la finestra
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # Se si preme ESC
            running = False

    pygame.display.flip()                                              # Aggiorna lo schermo
    clock.tick(30)                                                     # Limita il loop a 30 FPS

print("\nProgram closure...")
cap.release()                          # Rilascia la webcam liberando le risorse
pygame.quit()                          # Chiude pygame
print("Program closed properly.")