import pygame                          # Libreria per la grafica
import cv2                             # Libreria per la webcam
import numpy as np                     # Libreria per la manipolazione degli array (frame webcam)
from pygame import mixer               # Modulo di pygame per la gestione dell'audio
import sys                             # Libreria per uscire dal programma

# Inizializzazione
pygame.init()                          # Moduli Pygame
mixer.init()                           # Moduli audio

# Variabili globali
Logo_Immagine = None                   # immagine del logo
Immagine_sfondo = None                 # immagine di sfondo
started = False                        # stato del gioco prima della partenza
Stato_schermo = "menu"                 # Stato dello schermo ("menu" o "game")

# Pulsante GIOCA
button_x, button_y, button_w, button_h = 0, 0, 200, 60        # Posizione (x,y) e dimensioni (larghezza, altezza) del pulsante GIOCA

# Pulsante TORNA AL MENU
back_button_x, back_button_y, back_button_w, back_button_h = 0, 0, 250, 60    # Posizione e dimensioni del pulsante TORNA AL MENU

# Pulsante ESCI
exit_button_x, exit_button_y, exit_button_w, exit_button_h = 0, 0, 150, 50   # Posizione e dimensioni del pulsante ESCI

# Musica
song1 = None                           # Primo file audio
song2 = None                           # Secondo file audio
current_song = 1                       # Traccia della canzone corrente

# Webcam
Attivazione_Camera = None              # Attivazione della video camera

# Schermo
schermo = None                          # Superficie principale di pygame (la finestra)
width, height = 0, 0                   # Larghezza e altezza dello schermo


def Carica_Elementi():
    global Logo_Immagine, Immagine_sfondo, song1, song2    # Dichiara le variabili globali da modificare
    
    Logo_Immagine = pygame.image.load('gioco/logo.png')    # Carica immagine logo
    Immagine_sfondo = pygame.image.load('gioco/itis.png')  # Carica immagine sfondo
    
    song1 = 'gioco/Down_under.mp3'                         # canzone 1
    song2 = 'gioco/wind.mp3'                               # canzone 2


def setup():
    global schermo, width, height, button_x, button_y, back_button_x, back_button_y, exit_button_x, exit_button_y 
    
    info = pygame.display.Info()                           # informazioni necessarie del display
    width, height = info.current_w, info.current_h        # Legge la risoluzione attuale dello schermo
    schermo = pygame.display.set_mode((width, height))     # Creazione finestra con grandezza del display
    pygame.display.set_caption("Game")                    # Imposta il titolo della finestra
    
    button_x = width // 2 - button_w // 2                 # Posizionamento pulsante al centro della pagina
    button_y = height // 2 + 100                          # Posizionamento pulsante leggermete piu in basso dello schermo
    
    back_button_x = 20                                    # Posizionamento pulsante TORNA AL MENU a sinistra
    back_button_y = 20                                    # Posizionamento pulsante TORNA AL MENU in alto
    
    exit_button_x = width - exit_button_w - 20            # Posizionamento pulsante ESCI a destra
    exit_button_y = 20                                    # Posizionamento pulsante ESCI in alto
    
    Carica_Elementi()                                         # Caricamento elementi dichiarati(immagini e musiche)


def get_webcam_frame():
    if Attivazione_Camera is not None:                    # Controllo webcame attiva
        ret, frame = Attivazione_Camera.read()            # Legge un frame dalla webcam (ret=True se ok)
        if ret:                                           # dice se il frame è letto correttamente
            frame = cv2.flip(frame, 1)                    # Specchia il frame orizzontalmente (effetto specchio)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Converte i colori da BGR a RGB 
            frame = np.transpose(frame, (1, 0, 2))        # Ruota gli assi per compatibilità con pygame
            return pygame.surfarray.make_surface(frame)   # Converte l'array numpy in una superficie pygame
    return None                                           # Restituisce None se la webcam non è attiva o c'è un errore


def draw_background(): #funzione per fissare e mettere bene lo sfondo
    if Immagine_sfondo:                                                        # Controlla che l'immagine sia caricata
        img_w, img_h = Immagine_sfondo.get_size()                              # Ottiene le dimensioni originali dell'immagine
        scale_ratio = max(width / img_w, height / img_h)                      # Calcola il rapporto di scala per coprire tutto lo schermo
        w = int(img_w * scale_ratio)                                           # Calcola la nuova larghezza scalata
        h = int(img_h * scale_ratio)                                           # Calcola la nuova altezza scalata
        scaled_bg = pygame.transform.scale(Immagine_sfondo, (w, h))           # Ridimensiona l'immagine
        x = (width - w) // 2                                                  # Centra l'immagine orizzontalmente
        y = (height - h) // 2                                                  # Centra l'immagine verticalmente
        schermo.blit(scaled_bg, (x, y))                                        # Disegna l'immagine sullo schermo


def draw_logo():
    logo_w = min(700, width * 0.8)                                             # Larghezza del logo
    logo_h = logo_w * 0.75                                                     # Altezza proporzionale alla larghezza (rapporto 4:3)
    scaled_logo = pygame.transform.scale(Logo_Immagine, (int(logo_w), int(logo_h)))  # Ridimensiona il logo
    x = width // 2 - logo_w // 2                                              # Centra il logo orizzontalmente
    y = height // 2 - 150 - logo_h // 2                                       # Posiziona il logo nella metà alta dello schermo
    schermo.blit(scaled_logo, (x, y))                                          # posiziona il logo sullo schermo


def draw_button():
    mouse_x, mouse_y = pygame.mouse.get_pos()                                  # posizione del mouse
    is_sopra = (button_x < mouse_x < button_x + button_w and                  # Controlla se il mouse è sopra il pulsante
                button_y < mouse_y < button_y + button_h)            
    
    color = (80, 255, 130) if is_sopra else (50, 200, 100)                     # Verde chiaro se hover, verde scuro altrimenti
    pygame.draw.rect(schermo, color, (button_x, button_y, button_w, button_h), border_radius=20)   # Disegna il rettangolo del pulsante
    if is_sopra:                                                               # Se il mouse è sopra il pulsante
        pygame.draw.rect(schermo, (255, 255, 255), (button_x, button_y, button_w, button_h), width=3, border_radius=20)  # Aggiunge il bordo bianco
    
    font = pygame.font.Font(None, 36)                                          # Crea il font
    text = font.render("GIOCA", True, (255, 255, 255))                         # Mette la scritta GIOCA in bianco
    text_rect = text.get_rect(center=(button_x + button_w // 2, button_y + button_h // 2))  # Centra il testo nel pulsante
    schermo.blit(text, text_rect)                                               # Disegna il testo sullo schermo


def draw_back_button():
    mouse_x, mouse_y = pygame.mouse.get_pos()                                  # Posizione mouse
    is_sopra = (back_button_x < mouse_x < back_button_x + back_button_w and   # Controlla mouse sopra pulsante
                back_button_y < mouse_y < back_button_y + back_button_h)     
    
    color = (150, 150, 150) if is_sopra else (100, 100, 100)                   # Grigio chiaro se hover, grigio scuro altrimenti
    pygame.draw.rect(schermo, color, (back_button_x, back_button_y, back_button_w, back_button_h), border_radius=15)  # Disegna il rettangolo del pulsante
    if is_sopra:                                                               # Se il mouse è sopra il pulsante
        pygame.draw.rect(schermo, (255, 255, 255), (back_button_x, back_button_y, back_button_w, back_button_h), width=3, border_radius=15)  # Aggiunge il bordo bianco
    
    font = pygame.font.Font(None, 30)                                          # Crea il font di dimensione 30
    text = font.render("TORNA AL MENU", True, (255, 255, 255))                 # Renderizza il testo in bianco
    text_rect = text.get_rect(center=(back_button_x + back_button_w // 2, back_button_y + back_button_h // 2))  # Centra il testo nel pulsante
    schermo.blit(text, text_rect)                                               # Disegna il testo sullo schermo


def draw_exit_button():
    mouse_x, mouse_y = pygame.mouse.get_pos()                                  # Ottiene la posizione attuale del mouse
    is_sopra = (exit_button_x < mouse_x < exit_button_x + exit_button_w and   # Controlla se il mouse è sopra il pulsante
                exit_button_y < mouse_y < exit_button_y + exit_button_h)      # (sia in orizzontale che in verticale)
    
    color = (150, 150, 150) if is_sopra else (100, 100, 100)                   # Grigio chiaro se hover, grigio scuro altrimenti
    pygame.draw.rect(schermo, color, (exit_button_x, exit_button_y, exit_button_w, exit_button_h), border_radius=15)  # Disegna il rettangolo del pulsante
    if is_sopra:                                                               # Se il mouse è sopra il pulsante
        pygame.draw.rect(schermo, (255, 255, 255), (exit_button_x, exit_button_y, exit_button_w, exit_button_h), width=3, border_radius=15)  # Aggiunge il bordo bianco
    
    font = pygame.font.Font(None, 30)                                          # Crea il font di dimensione 30
    text = font.render("ESCI", True, (255, 255, 255))                          # Renderizza il testo "ESCI" in bianco
    text_rect = text.get_rect(center=(exit_button_x + exit_button_w // 2, exit_button_y + exit_button_h // 2))  # Centra il testo nel pulsante
    schermo.blit(text, text_rect)                                               # Disegna il testo sullo schermo


def draw():
    schermo.fill((0, 0, 0))                                # Riempie lo schermo di nero (cancella il frame precedente)
    
    if Stato_schermo == "menu":                           # Se siamo nel menu
        if started:                                       # Se il gioco è già stato avviato con il primo click
            draw_background()                             # Disegna l'immagine di sfondo
            draw_logo()                                   # Disegna il logo
            draw_button()                                 # Disegna il pulsante GIOCA
            draw_exit_button()                            # Disegna il pulsante ESCI
        else:                                             # Se il gioco non è ancora stato avviato
            font = pygame.font.Font(None, 36)             # Crea il font di dimensione 36
            text = font.render("Clicca per avviare il gioco", True, (255, 255, 255))  # Renderizza il testo iniziale
            text_rect = text.get_rect(center=(width // 2, height // 2))               # Centra il testo nello schermo
            schermo.blit(text, text_rect)                  # Disegna il testo sullo schermo
            draw_exit_button()                            # Disegna il pulsante ESCI
    
    elif Stato_schermo == "game":                         # Se siamo nella schermata di gioco
        frame = get_webcam_frame()                        # Ottiene il frame corrente dalla webcam
        if frame:                                         # Se il frame è valido
            capture_w, capture_h = frame.get_size()       # Ottiene le dimensioni del frame webcam
            scale_ratio = min(width / capture_w, height / capture_h)  # Calcola il rapporto di scala per adattarlo allo schermo
            w = int(capture_w * scale_ratio)              # Calcola la nuova larghezza del frame
            h = int(capture_h * scale_ratio)              # Calcola la nuova altezza del frame
            scaled_frame = pygame.transform.scale(frame, (w, h))  # Ridimensiona il frame
            x = (width - w) // 2                         # Centra il frame orizzontalmente
            y = (height - h) // 2                        # Centra il frame verticalmente
            schermo.blit(scaled_frame, (x, y))            # Disegna il frame della webcam sullo schermo
        
        draw_back_button()                                # Disegna il pulsante TORNA AL MENU
        draw_exit_button()                                # Disegna il pulsante ESCI
    
    pygame.display.flip()                                 # Aggiorna lo schermo mostrando tutto ciò che è stato disegnato


def handle_music():
    global current_song                                   # Dichiara la variabile globale da modificare
    
    if not started:                                       # Se siamo sulla schermata nera, nessuna musica
        return
    
    if Stato_schermo == "menu":                           # La musica suona solo nel menu principale
        if not mixer.music.get_busy():                    # Se la musica non sta suonando
            if current_song == 1:
                mixer.music.load(song1)                   # Carica la prima canzone
                mixer.music.play()                        # Avvia la riproduzione
                current_song = 2                          # La prossima sarà la seconda
            else:
                mixer.music.load(song2)                   # Carica la seconda canzone
                mixer.music.play()                        # Avvia la riproduzione
                current_song = 1                          # La prossima sarà la prima
    elif Stato_schermo == "game":                         # Nel gioco la musica viene fermata
        if mixer.music.get_busy():                        # Se la musica sta suonando
            mixer.music.stop()                            # Fermala


def cleanup_and_exit():
    global Attivazione_Camera                             # Dichiara la variabile globale da modificare
    mixer.music.stop()                                    # Ferma la riproduzione musicale
    if Attivazione_Camera:                                # Se la webcam è attiva
        Attivazione_Camera.release()                      # Rilascia la webcam liberando le risorse
    pygame.quit()                                         # Chiude pygame
    sys.exit()                                            # Termina il programma


def mouse_pressed(pos):
    global started, Stato_schermo, Attivazione_Camera, current_song  # Dichiara le variabili globali da modificare
    
    mouse_x, mouse_y = pos                                # Estrae le coordinate x e y del click
    
    # Pulsante ESCI (sempre attivo)
    if (exit_button_x < mouse_x < exit_button_x + exit_button_w and   # Controlla se il click è dentro il pulsante ESCI
        exit_button_y < mouse_y < exit_button_y + exit_button_h):      # (sia in orizzontale che in verticale)
        cleanup_and_exit()                                # Chiude il programma
    
    if not started:                                       # Se è il primo click (gioco non ancora avviato)
        started = True                                    # Segna il gioco come avviato
        return                                            # Esce dalla funzione senza controllare altri pulsanti
    
    if Stato_schermo == "game":                           # Se siamo nella schermata di gioco
        if (back_button_x < mouse_x < back_button_x + back_button_w and   # Controlla se il click è dentro il pulsante TORNA AL MENU
            back_button_y < mouse_y < back_button_y + back_button_h):     # (sia in orizzontale che in verticale)
            Stato_schermo = "menu"                        # Torna al menu
            if Attivazione_Camera:                        # Se la webcam è attiva
                Attivazione_Camera.release()              # Rilascia la webcam
                Attivazione_Camera = None                 # Reimposta la variabile a None
    
    elif Stato_schermo == "menu":                         # Se siamo nel menu
        if (button_x < mouse_x < button_x + button_w and   # Controlla se il click è dentro il pulsante GIOCA
            button_y < mouse_y < button_y + button_h):      # (sia in orizzontale che in verticale)
            Stato_schermo = "game"                        # Passa alla schermata di gioco
            Attivazione_Camera = cv2.VideoCapture(0)      # Apre la webcam (0 = webcam predefinita)


def main():
    global width, height, button_x, button_y, back_button_x, back_button_y, exit_button_x, exit_button_y  # Dichiara le variabili globali da modificare
    
    setup()                                               # Inizializza lo schermo e carica le risorse
    clock = pygame.time.Clock()                           # Crea un oggetto clock per controllare i FPS
    
    while True:                                           # Loop principale del gioco (gira all'infinito)
        for event in pygame.event.get():                  # Controlla tutti gli eventi pygame in coda
            if event.type == pygame.QUIT:                 # Se l'utente chiude la finestra
                cleanup_and_exit()                        # Chiude il programma
            elif event.type == pygame.MOUSEBUTTONDOWN:    # Se l'utente clicca con il mouse
                mouse_pressed(event.pos)                  # Gestisce il click passando la posizione
            elif event.type == pygame.KEYDOWN:            # Se l'utente preme un tasto
                if event.key == pygame.K_ESCAPE:          # Se il tasto è ESC
                    cleanup_and_exit()                    # Chiude il programma
        
        draw()                                            # Disegna tutti gli elementi sullo schermo
        handle_music()                                    # Controlla e gestisce la riproduzione musicale
        clock.tick(30)                                    # Limita il loop a 30 FPS

if __name__ == "__main__":                                # Controlla che il file venga eseguito direttamente
    main()                                                # Avvia il programma