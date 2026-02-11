import pygame
import cv2
import numpy as np
from pygame import mixer

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

# Pulsante
button_x, button_y, button_w, button_h = 0, 0, 200, 60

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
    game_image = pygame.image.load('itis.png')
    logo_image = pygame.image.load('logo.png')
    
    # Carica video
    video_cap = cv2.VideoCapture('video_menu.mp4')
    
    # Carica musica
    song1 = 'Down_under.mp3'
    song2 = 'wind.mp3'

def setup():
    global screen, width, height, button_x, button_y
    
    # Crea finestra a schermo intero
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Game")
    
    # Posizione pulsante
    button_x = width // 2 - button_w // 2
    button_y = height // 2 + 100
    
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
            # Converti da BGR a RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Ruota e specchia
            frame = np.rot90(frame)
            frame = np.fliplr(frame)
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
        else:
            # Testo iniziale
            font = pygame.font.Font(None, 36)
            text = font.render("Clicca per avviare il gioco", True, (255, 255, 255))
            text_rect = text.get_rect(center=(width // 2, height // 2))
            screen.blit(text, text_rect)
    
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

def mouse_pressed(pos):
    global started, screen_state, capture, current_song
    
    mouse_x, mouse_y = pos
    
    # Primo click - avvia
    if not started:
        started = True
        mixer.music.load(song1)
        mixer.music.play()
        current_song = 1
        return
    
    # Click sul pulsante GIOCA
    if (button_x < mouse_x < button_x + button_w and 
        button_y < mouse_y < button_y + button_h):
        screen_state = "game"
        
        # Ferma video
        if video_cap:
            video_cap.release()
        
        # Attiva webcam
        capture = cv2.VideoCapture(0)

def main():
    global width, height, button_x, button_y
    
    setup()
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed(event.pos)
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                button_x = width // 2 - button_w // 2
                button_y = height // 2 + 100
        
        draw()
        handle_music()
        clock.tick(30)  # 30 FPS
    
    # Cleanup
    if video_cap:
        video_cap.release()
    if capture:
        capture.release()
    
    pygame.quit()

if __name__ == "__main__":
    main()