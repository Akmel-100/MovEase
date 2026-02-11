import pygame
import cv2
import numpy as np
from pygame import mixer
import sys

# Inizializzazione
pygame.init()
mixer.init()

# Variabili globali
video = None
capture = None
game_image = None
logo_image = None
started = False
screen_state = "video"

# Pulsante GIOCA
button_x, button_y, button_w, button_h = 0, 0, 200, 60

# Pulsante TORNA AL MENU
back_button_x, back_button_y, back_button_w, back_button_h = 0, 0, 250, 60

# Pulsante ESCI
exit_button_x, exit_button_y, exit_button_w, exit_button_h = 0, 0, 150, 50

# Musica
song1 = None
song2 = None
current_song = 1

# Video
video_cap = None
video_frame = None

# Schermo
screen = None
width, height = 0, 0

def load_assets():
    global game_image, logo_image, song1, song2, video_cap
    
    # Carica immagini
    game_image = pygame.image.load('gioco/itis.png')
    logo_image = pygame.image.load('gioco/logo.png')
    
    # Carica video
    video_cap = cv2.VideoCapture('gioco/video_menu.mp4')
    
    # Carica musica
    song1 = 'gioco/Down_under.mp3'
    song2 = 'gioco/wind.mp3'

def setup():
    global screen, width, height, button_x, button_y, back_button_x, back_button_y, exit_button_x, exit_button_y
    
    # Crea finestra a schermo intero
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Game")
    
    # Posizione pulsante GIOCA
    button_x = width // 2 - button_w // 2
    button_y = height // 2 + 100
    
    # Posizione pulsante TORNA AL MENU (in alto a sinistra)
    back_button_x = 20
    back_button_y = 20
    
    # Posizione pulsante ESCI (in alto a destra)
    exit_button_x = width - exit_button_w - 20
    exit_button_y = 20
    
    load_assets()

def get_video_frame():
    global video_frame
    
    if video_cap is not None and video_cap.isOpened():
        ret, frame = video_cap.read()
        if ret:
            # Converti da BGR (OpenCV) a RGB (Pygame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Ruota l'immagine (OpenCV la legge in modo diverso)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            video_frame = frame
        else:
            # Riavvia il video (loop)
            video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    return video_frame

def get_webcam_frame():
    if capture is not None:
        ret, frame = capture.read()
        if ret:
            # Specchia l'immagine orizzontalmente (effetto specchio)
            frame = cv2.flip(frame, 1)
            # Converti da BGR a RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Trasponi per pygame (scambia righe e colonne)
            frame = np.transpose(frame, (1, 0, 2))
            return pygame.surfarray.make_surface(frame)
    return None

def draw_logo():
    logo_w = min(600, width * 0.8)
    logo_h = logo_w * 0.75
    
    # Ridimensiona logo
    scaled_logo = pygame.transform.scale(logo_image, (int(logo_w), int(logo_h)))
    
    # Centra logo
    x = width // 2 - logo_w // 2
    y = height // 2 - 150 - logo_h // 2
    
    screen.blit(scaled_logo, (x, y))

def draw_button():
    global button_x, button_y, button_w, button_h
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hover = (button_x < mouse_x < button_x + button_w and 
                button_y < mouse_y < button_y + button_h)
    
    # Colore pulsante
    if is_hover:
        color = (80, 255, 130)
        border_color = (255, 255, 255)
        border_width = 3
    else:
        color = (50, 200, 100)
        border_color = None
        border_width = 0
    
    # Disegna pulsante
    pygame.draw.rect(screen, color, (button_x, button_y, button_w, button_h), 
                     border_radius=20)
    
    if is_hover and border_color:
        pygame.draw.rect(screen, border_color, 
                        (button_x, button_y, button_w, button_h), 
                        width=border_width, border_radius=20)
    
    # Testo
    font = pygame.font.Font(None, 36)
    text = font.render("GIOCA", True, (255, 255, 255))
    text_rect = text.get_rect(center=(button_x + button_w // 2, 
                                      button_y + button_h // 2))
    screen.blit(text, text_rect)

def draw_back_button():
    global back_button_x, back_button_y, back_button_w, back_button_h
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hover = (back_button_x < mouse_x < back_button_x + back_button_w and 
                back_button_y < mouse_y < back_button_y + back_button_h)
    
    # Colore pulsante (grigio come il pulsante ESCI)
    if is_hover:
        color = (150, 150, 150)
        border_color = (255, 255, 255)
        border_width = 3
    else:
        color = (100, 100, 100)
        border_color = None
        border_width = 0
    
    # Disegna pulsante
    pygame.draw.rect(screen, color, (back_button_x, back_button_y, back_button_w, back_button_h), 
                     border_radius=15)
    
    if is_hover and border_color:
        pygame.draw.rect(screen, border_color, 
                        (back_button_x, back_button_y, back_button_w, back_button_h), 
                        width=border_width, border_radius=15)
    
    # Testo
    font = pygame.font.Font(None, 30)
    text = font.render("TORNA AL MENU", True, (255, 255, 255))
    text_rect = text.get_rect(center=(back_button_x + back_button_w // 2, 
                                      back_button_y + back_button_h // 2))
    screen.blit(text, text_rect)

def draw_exit_button():
    global exit_button_x, exit_button_y, exit_button_w, exit_button_h
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hover = (exit_button_x < mouse_x < exit_button_x + exit_button_w and 
                exit_button_y < mouse_y < exit_button_y + exit_button_h)
    
    # Colore pulsante
    if is_hover:
        color = (150, 150, 150)
        border_color = (255, 255, 255)
        border_width = 3
    else:
        color = (100, 100, 100)
        border_color = None
        border_width = 0
    
    # Disegna pulsante
    pygame.draw.rect(screen, color, (exit_button_x, exit_button_y, exit_button_w, exit_button_h), 
                     border_radius=15)
    
    if is_hover and border_color:
        pygame.draw.rect(screen, border_color, 
                        (exit_button_x, exit_button_y, exit_button_w, exit_button_h), 
                        width=border_width, border_radius=15)
    
    # Testo
    font = pygame.font.Font(None, 30)
    text = font.render("ESCI", True, (255, 255, 255))
    text_rect = text.get_rect(center=(exit_button_x + exit_button_w // 2, 
                                      exit_button_y + exit_button_h // 2))
    screen.blit(text, text_rect)

def draw():
    global video_frame
    
    screen.fill((0, 0, 0))
    
    if screen_state == "video":
        if started:
            # Mostra video
            frame = get_video_frame()
            if frame:
                # Scala video per adattarlo allo schermo
                video_w, video_h = frame.get_size()
                scale_ratio = min(width / video_w, height / video_h)
                w = int(video_w * scale_ratio)
                h = int(video_h * scale_ratio)
                
                scaled_frame = pygame.transform.scale(frame, (w, h))
                x = (width - w) // 2
                y = (height - h) // 2
                screen.blit(scaled_frame, (x, y))
            
            draw_logo()
            draw_button()
            draw_exit_button()  # Pulsante ESCI nel menu principale
        else:
            # Testo iniziale
            font = pygame.font.Font(None, 36)
            text = font.render("Clicca per avviare il gioco", True, (255, 255, 255))
            text_rect = text.get_rect(center=(width // 2, height // 2))
            screen.blit(text, text_rect)
            draw_exit_button()  # Pulsante ESCI anche nella schermata iniziale
    
    elif screen_state == "game":
        # Mostra webcam
        frame = get_webcam_frame()
        if frame:
            # Scala webcam per adattarla allo schermo
            capture_w, capture_h = frame.get_size()
            scale_ratio = min(width / capture_w, height / capture_h)
            w = int(capture_w * scale_ratio)
            h = int(capture_h * scale_ratio)
            
            scaled_frame = pygame.transform.scale(frame, (w, h))
            x = (width - w) // 2
            y = (height - h) // 2
            screen.blit(scaled_frame, (x, y))
        
        # Disegna pulsanti nella schermata di gioco
        draw_back_button()  # Pulsante TORNA AL MENU
        draw_exit_button()  # Pulsante ESCI anche qui
    
    pygame.display.flip()

def handle_music():
    global current_song
    
    # Controlla se la musica è finita e passa alla successiva
    if not mixer.music.get_busy():
        if current_song == 1:
            mixer.music.load(song2)
            mixer.music.play()
            current_song = 2
        else:
            mixer.music.load(song1)
            mixer.music.play()
            current_song = 1

def cleanup_and_exit():
    """Pulisce le risorse e chiude il gioco"""
    global video_cap, capture
    
    # Ferma la musica
    mixer.music.stop()
    
    # Rilascia video
    if video_cap:
        video_cap.release()
    
    # Rilascia webcam
    if capture:
        capture.release()
    
    # Chiude pygame
    pygame.quit()
    
    # Esce dal programma
    sys.exit()

def mouse_pressed(pos):
    global started, screen_state, capture, current_song, video_cap
    
    mouse_x, mouse_y = pos
    
    # Click sul pulsante ESCI (disponibile SEMPRE, in tutte le schermate)
    if (exit_button_x < mouse_x < exit_button_x + exit_button_w and 
        exit_button_y < mouse_y < exit_button_y + exit_button_h):
        cleanup_and_exit()
    
    # Primo click - avvia
    if not started:
        started = True
        mixer.music.load(song1)
        mixer.music.play()
        current_song = 1
        return
    
    # Se siamo nella schermata di gioco
    if screen_state == "game":
        # Click sul pulsante TORNA AL MENU
        if (back_button_x < mouse_x < back_button_x + back_button_w and 
            back_button_y < mouse_y < back_button_y + back_button_h):
            screen_state = "video"
            
            # Ferma e rilascia webcam
            if capture:
                capture.release()
                capture = None
            
            # Riavvia il video
            if video_cap is None or not video_cap.isOpened():
                video_cap = cv2.VideoCapture('gioco/video_menu.mp4')
    
    # Se siamo nella schermata video
    elif screen_state == "video":
        # Click sul pulsante GIOCA
        if (button_x < mouse_x < button_x + button_w and 
            button_y < mouse_y < button_y + button_h):
            screen_state = "game"
            
            # Ferma video
            if video_cap:
                video_cap.release()
                video_cap = None
            
            # Attiva webcam
            capture = cv2.VideoCapture(0)

def main():
    global width, height, button_x, button_y, back_button_x, back_button_y, exit_button_x, exit_button_y
    
    setup()
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanup_and_exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed(event.pos)
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                button_x = width // 2 - button_w // 2
                button_y = height // 2 + 100
                back_button_x = 20
                back_button_y = 20
                exit_button_x = width - exit_button_w - 20
                exit_button_y = 20
            elif event.type == pygame.KEYDOWN:
                # Permetti di uscire anche con ESC
                if event.key == pygame.K_ESCAPE:
                    cleanup_and_exit()
        
        draw()
        handle_music()
        clock.tick(30)  # 30 FPS
    
    cleanup_and_exit()

if __name__ == "__main__":
    main()