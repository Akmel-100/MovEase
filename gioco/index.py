import pygame
import cv2
import numpy as np
from pygame import mixer
import sys

# Inizializzazione
pygame.init()
mixer.init()

# Variabili globali
game_image = None
logo_image = None
background_image = None  # Immagine di sfondo (al posto del video)
started = False
screen_state = "menu"

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

# Webcam
capture = None

# Schermo
screen = None
width, height = 0, 0

def load_assets():
    global game_image, logo_image, background_image, song1, song2
    
    # Carica immagini
    game_image = pygame.image.load('gioco/itis.png')
    logo_image = pygame.image.load('gioco/logo.png')
    background_image = pygame.image.load('gioco/itis.png')  # <-- Immagine di sfondo
    
    # Carica musica
    song1 = 'gioco/Down_under.mp3'
    song2 = 'gioco/wind.mp3'

def setup():
    global screen, width, height, button_x, button_y, back_button_x, back_button_y, exit_button_x, exit_button_y
    
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Game")
    
    button_x = width // 2 - button_w // 2
    button_y = height // 2 + 100
    
    back_button_x = 20
    back_button_y = 20
    
    exit_button_x = width - exit_button_w - 20
    exit_button_y = 20
    
    load_assets()

def get_webcam_frame():
    if capture is not None:
        ret, frame = capture.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.transpose(frame, (1, 0, 2))
            return pygame.surfarray.make_surface(frame)
    return None

def draw_background():
    """Disegna l'immagine di sfondo scalata per coprire tutto lo schermo"""
    if background_image:
        img_w, img_h = background_image.get_size()
        scale_ratio = max(width / img_w, height / img_h)
        w = int(img_w * scale_ratio)
        h = int(img_h * scale_ratio)
        scaled_bg = pygame.transform.scale(background_image, (w, h))
        x = (width - w) // 2
        y = (height - h) // 2
        screen.blit(scaled_bg, (x, y))

def draw_logo():
    logo_w = min(600, width * 0.8)
    logo_h = logo_w * 0.75
    scaled_logo = pygame.transform.scale(logo_image, (int(logo_w), int(logo_h)))
    x = width // 2 - logo_w // 2
    y = height // 2 - 150 - logo_h // 2
    screen.blit(scaled_logo, (x, y))

def draw_button():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hover = (button_x < mouse_x < button_x + button_w and 
                button_y < mouse_y < button_y + button_h)
    
    color = (80, 255, 130) if is_hover else (50, 200, 100)
    pygame.draw.rect(screen, color, (button_x, button_y, button_w, button_h), border_radius=20)
    if is_hover:
        pygame.draw.rect(screen, (255, 255, 255), (button_x, button_y, button_w, button_h), width=3, border_radius=20)
    
    font = pygame.font.Font(None, 36)
    text = font.render("GIOCA", True, (255, 255, 255))
    text_rect = text.get_rect(center=(button_x + button_w // 2, button_y + button_h // 2))
    screen.blit(text, text_rect)

def draw_back_button():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hover = (back_button_x < mouse_x < back_button_x + back_button_w and 
                back_button_y < mouse_y < back_button_y + back_button_h)
    
    color = (150, 150, 150) if is_hover else (100, 100, 100)
    pygame.draw.rect(screen, color, (back_button_x, back_button_y, back_button_w, back_button_h), border_radius=15)
    if is_hover:
        pygame.draw.rect(screen, (255, 255, 255), (back_button_x, back_button_y, back_button_w, back_button_h), width=3, border_radius=15)
    
    font = pygame.font.Font(None, 30)
    text = font.render("TORNA AL MENU", True, (255, 255, 255))
    text_rect = text.get_rect(center=(back_button_x + back_button_w // 2, back_button_y + back_button_h // 2))
    screen.blit(text, text_rect)

def draw_exit_button():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hover = (exit_button_x < mouse_x < exit_button_x + exit_button_w and 
                exit_button_y < mouse_y < exit_button_y + exit_button_h)
    
    color = (150, 150, 150) if is_hover else (100, 100, 100)
    pygame.draw.rect(screen, color, (exit_button_x, exit_button_y, exit_button_w, exit_button_h), border_radius=15)
    if is_hover:
        pygame.draw.rect(screen, (255, 255, 255), (exit_button_x, exit_button_y, exit_button_w, exit_button_h), width=3, border_radius=15)
    
    font = pygame.font.Font(None, 30)
    text = font.render("ESCI", True, (255, 255, 255))
    text_rect = text.get_rect(center=(exit_button_x + exit_button_w // 2, exit_button_y + exit_button_h // 2))
    screen.blit(text, text_rect)

def draw():
    screen.fill((0, 0, 0))
    
    if screen_state == "menu":
        if started:
            draw_background()  # Mostra immagine di sfondo
            draw_logo()
            draw_button()
            draw_exit_button()
        else:
            # Schermata iniziale con solo il testo
            font = pygame.font.Font(None, 36)
            text = font.render("Clicca per avviare il gioco", True, (255, 255, 255))
            text_rect = text.get_rect(center=(width // 2, height // 2))
            screen.blit(text, text_rect)
            draw_exit_button()
    
    elif screen_state == "game":
        frame = get_webcam_frame()
        if frame:
            capture_w, capture_h = frame.get_size()
            scale_ratio = min(width / capture_w, height / capture_h)
            w = int(capture_w * scale_ratio)
            h = int(capture_h * scale_ratio)
            scaled_frame = pygame.transform.scale(frame, (w, h))
            x = (width - w) // 2
            y = (height - h) // 2
            screen.blit(scaled_frame, (x, y))
        
        draw_back_button()
        draw_exit_button()
    
    pygame.display.flip()

def handle_music():
    global current_song
    
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
    global capture
    mixer.music.stop()
    if capture:
        capture.release()
    pygame.quit()
    sys.exit()

def mouse_pressed(pos):
    global started, screen_state, capture, current_song
    
    mouse_x, mouse_y = pos
    
    # Pulsante ESCI (sempre attivo)
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
    
    if screen_state == "game":
        # Pulsante TORNA AL MENU
        if (back_button_x < mouse_x < back_button_x + back_button_w and 
            back_button_y < mouse_y < back_button_y + back_button_h):
            screen_state = "menu"
            if capture:
                capture.release()
                capture = None
    
    elif screen_state == "menu":
        # Pulsante GIOCA
        if (button_x < mouse_x < button_x + button_w and 
            button_y < mouse_y < button_y + button_h):
            screen_state = "game"
            capture = cv2.VideoCapture(0)

def main():
    global width, height, button_x, button_y, back_button_x, back_button_y, exit_button_x, exit_button_y
    
    setup()
    clock = pygame.time.Clock()
    
    while True:
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
                if event.key == pygame.K_ESCAPE:
                    cleanup_and_exit()
        
        draw()
        handle_music()
        clock.tick(30)

if __name__ == "__main__":
    main()