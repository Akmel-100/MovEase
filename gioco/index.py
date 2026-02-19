import pygame                          # Libreria per la grafica
import cv2                             # Libreria per la webcam
import numpy as np                     # Libreria per la manipolazione degli array (frame webcam)
from pygame import mixer               # Modulo di pygame per la gestione dell'audio
import sys                             # Libreria per uscire dal programma

# Inizializzazione
pygame.init()                          # Moduli Pygame
mixer.init()                           # Moduli audio

# Variabili globali
Logo_Immagine = None                   # Immagine del logo
Immagine_sfondo = None                 # Immagine di sfondo
started = False                        # Stato del gioco prima della partenza
Stato_schermo = "menu"                 # Stato dello schermo ("menu", "istruzioni" o "game")

# Pulsante GIOCA
button_x, button_y, button_w, button_h = 0, 0, 200, 60        # Posizione (x,y) e dimensioni (larghezza, altezza) del pulsante GIOCA

# Pulsante VOLUME
volume_button_x, volume_button_y, volume_button_w, volume_button_h = 0, 0, 200, 60  # Posizione e dimensioni del pulsante VOLUME
mostra_slider_volume = False           # True se lo slider del volume è visibile
volume_corrente = 0.5                  # Volume corrente (da 0.0 a 1.0)
slider_x, slider_y, slider_w, slider_h = 0, 0, 200, 10        # Posizione e dimensioni della barra dello slider
slider_dragging = False                # True se l'utente sta trascinando il cursore dello slider

# Pulsante ESCI
exit_button_x, exit_button_y, exit_button_w, exit_button_h = 0, 0, 200, 60          # Posizione e dimensioni del pulsante ESCI

# Pulsante INIZIA (schermata istruzioni, avvia la telecamera)
inizia_button_x, inizia_button_y, inizia_button_w, inizia_button_h = 0, 0, 220, 60  # Posizione e dimensioni del pulsante INIZIA

# Pulsante TORNA AL MENU (schermata istruzioni e schermata di gioco)
back_button_x, back_button_y, back_button_w, back_button_h = 0, 0, 250, 60          # Posizione e dimensioni del pulsante TORNA AL MENU

# Pulsante ESCI DAL GIOCO (schermata di gioco, accanto a TORNA AL MENU)
exit_game_button_x, exit_game_button_y, exit_game_button_w, exit_game_button_h = 0, 0, 200, 60  # Posizione e dimensioni

# Immagini delle direzioni (schermata istruzioni)
img_avanti   = None                    # Immagine direzione AVANTI
img_indietro = None                    # Immagine direzione INDIETRO
img_destra   = None                    # Immagine direzione DESTRA
img_sinistra = None                    # Immagine direzione SINISTRA
img_fermo    = None                    # Immagine direzione FERMO

# Musica
song1 = None                           # Primo file audio
song2 = None                           # Secondo file audio
current_song = 1                       # Traccia della canzone corrente

# Webcam
Attivazione_Camera = None              # Oggetto di cattura della webcam

# Schermo
schermo = None                         # Superficie principale di pygame (la finestra)
width, height = 0, 0                   # Larghezza e altezza dello schermo


def Carica_Elementi():
    global Logo_Immagine, Immagine_sfondo, song1, song2          # Dichiara le variabili globali da modificare
    global img_avanti, img_indietro, img_destra, img_sinistra, img_fermo

    Logo_Immagine   = pygame.image.load('gioco/logo.png')        # Carica immagine logo
    Immagine_sfondo = pygame.image.load('gioco/itis.png')        # Carica immagine sfondo

    song1 = 'gioco/Down_under.mp3'                               # Canzone 1
    song2 = 'gioco/wind.mp3'                                     # Canzone 2

    # Carica le immagini delle direzioni dalla cartella gioco/
    # Se un file non esiste viene lasciato a None e al suo posto apparirà un riquadro grigio
    for nome_var, percorso in [
        ('img_avanti',   'gioco/avanti.png'),                    # Percorso immagine AVANTI
        ('img_indietro', 'gioco/indietro.png'),                  # Percorso immagine INDIETRO
        ('img_destra',   'gioco/destra.png'),                    # Percorso immagine DESTRA
        ('img_sinistra', 'gioco/sinistra.png'),                  # Percorso immagine SINISTRA
        ('img_fermo',    'gioco/fermo.png'),                     # Percorso immagine FERMO
    ]:
        try:
            globals()[nome_var] = pygame.image.load(percorso)   # Carica l'immagine se il file esiste
        except Exception:
            globals()[nome_var] = None                           # Se il file manca, lascia None


def setup():
    global schermo, width, height                                # Dichiara le variabili globali da modificare
    global button_x, button_y
    global volume_button_x, volume_button_y
    global exit_button_x, exit_button_y
    global slider_x, slider_y, slider_w
    global back_button_x, back_button_y
    global exit_game_button_x, exit_game_button_y
    global inizia_button_x, inizia_button_y

    info = pygame.display.Info()                                 # Ottiene le informazioni del display
    width, height = info.current_w, info.current_h              # Legge la risoluzione attuale dello schermo
    schermo = pygame.display.set_mode((width, height))           # Crea la finestra con la grandezza del display
    pygame.display.set_caption("Game")                          # Imposta il titolo della finestra

    # Pulsanti del menu allineati sulla stessa riga: VOLUME | GIOCA | ESCI
    gap     = 20                                                 # Spazio in pixel tra i pulsanti
    total_w = volume_button_w + gap + button_w + gap + exit_button_w  # Larghezza totale dei tre pulsanti con spazi
    sx      = width // 2 - total_w // 2                         # X di partenza per centrare il gruppo
    btn_y   = height // 2 + 100                                 # Y comune dei tre pulsanti (leggermente in basso)

    volume_button_x = sx                                        # Posiziona VOLUME come primo pulsante a sinistra
    volume_button_y = btn_y                                     # Stessa altezza degli altri pulsanti

    button_x = volume_button_x + volume_button_w + gap          # Posiziona GIOCA subito dopo VOLUME
    button_y = btn_y                                            # Stessa altezza degli altri pulsanti

    exit_button_x = button_x + button_w + gap                   # Posiziona ESCI subito dopo GIOCA
    exit_button_y = btn_y                                       # Stessa altezza degli altri pulsanti

    slider_x = volume_button_x                                  # Lo slider inizia allineato al pulsante VOLUME
    slider_y = volume_button_y - 40                             # Lo slider appare sopra il pulsante VOLUME
    slider_w = volume_button_w                                  # Lo slider è largo quanto il pulsante VOLUME

    back_button_x = 20                                          # Posiziona TORNA AL MENU a sinistra
    back_button_y = 20                                          # Posiziona TORNA AL MENU in alto

    inizia_button_x = width // 2 - inizia_button_w // 2        # Centra INIZIA orizzontalmente
    inizia_button_y = height - 110                              # Posiziona INIZIA in basso nella schermata

    exit_game_button_x = back_button_x + back_button_w + 20    # Posiziona ESCI DAL GIOCO accanto a TORNA AL MENU
    exit_game_button_y = 20                                     # Stesso livello verticale di TORNA AL MENU

    mixer.music.set_volume(volume_corrente)                     # Imposta il volume iniziale
    Carica_Elementi()                                           # Carica le risorse (immagini e musiche)


def get_webcam_frame():
    if Attivazione_Camera is not None:                          # Controlla se la webcam è attiva
        ret, frame = Attivazione_Camera.read()                  # Legge un frame dalla webcam (ret=True se ok)
        if ret:                                                 # Controlla se il frame è stato letto correttamente
            frame = cv2.flip(frame, 1)                          # Specchia il frame orizzontalmente (effetto specchio)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)      # Converte i colori da BGR a RGB
            frame = np.transpose(frame, (1, 0, 2))              # Ruota gli assi per compatibilità con pygame
            return pygame.surfarray.make_surface(frame)         # Converte l'array numpy in una superficie pygame
    return None                                                 # Restituisce None se la webcam non è attiva o c'è errore


def draw_background():
    if Immagine_sfondo:                                                          # Controlla che l'immagine sia caricata
        iw, ih  = Immagine_sfondo.get_size()                                     # Ottiene le dimensioni originali dell'immagine
        ratio   = max(width / iw, height / ih)                                   # Calcola il rapporto di scala per coprire tutto lo schermo
        w, h    = int(iw * ratio), int(ih * ratio)                               # Calcola le nuove dimensioni scalate
        scaled  = pygame.transform.scale(Immagine_sfondo, (w, h))               # Ridimensiona l'immagine
        schermo.blit(scaled, ((width - w) // 2, (height - h) // 2))             # Centra e disegna l'immagine sullo schermo


def draw_logo():
    logo_w = min(700, width * 0.8)                                               # Larghezza del logo (massimo 700px)
    logo_h = logo_w * 0.75                                                       # Altezza proporzionale (rapporto 4:3)
    scaled = pygame.transform.scale(Logo_Immagine, (int(logo_w), int(logo_h)))  # Ridimensiona il logo
    schermo.blit(scaled, (width // 2 - logo_w // 2, height // 2 - 150 - logo_h // 2))  # Centra e disegna il logo


def _draw_btn(rect, label, color_normal, color_hover, font_size=36):
    bx, by, bw, bh = rect                                       # Estrae le coordinate e dimensioni del pulsante
    mx, my = pygame.mouse.get_pos()                             # Ottiene la posizione attuale del mouse
    hover  = bx < mx < bx + bw and by < my < by + bh           # True se il mouse è sopra il pulsante
    pygame.draw.rect(schermo, color_hover if hover else color_normal, rect, border_radius=20)  # Disegna il rettangolo del pulsante
    if hover:                                                   # Se il mouse è sopra il pulsante
        pygame.draw.rect(schermo, (255, 255, 255), rect, width=3, border_radius=20)  # Aggiunge il bordo bianco
    font = pygame.font.Font(None, font_size)                    # Crea il font con la dimensione specificata
    text = font.render(label, True, (255, 255, 255))            # Renderizza il testo in bianco
    schermo.blit(text, text.get_rect(center=(bx + bw // 2, by + bh // 2)))  # Centra e disegna il testo nel pulsante


def draw_button():
    _draw_btn((button_x, button_y, button_w, button_h),
              "PLAY", (50, 200, 100), (80, 255, 130))          # Verde scuro normale, verde chiaro hover


def draw_volume_button():
    _draw_btn((volume_button_x, volume_button_y, volume_button_w, volume_button_h),
              "VOLUME", (60, 100, 200), (100, 150, 255))        # Blu scuro normale, blu chiaro hover
    if mostra_slider_volume:                                    # Se lo slider è visibile
        draw_volume_slider()                                    # Disegna anche la barra del volume


def draw_volume_slider():
    pygame.draw.rect(schermo, (80, 80, 80),
                     (slider_x, slider_y, slider_w, slider_h), border_radius=5)   # Disegna lo sfondo grigio della barra
    filled_w = int(slider_w * volume_corrente)                                     # Calcola la larghezza della parte riempita
    pygame.draw.rect(schermo, (100, 180, 255),
                     (slider_x, slider_y, filled_w, slider_h), border_radius=5)   # Disegna la parte riempita in blu
    cx = slider_x + filled_w                                   # Posizione X del cursore
    cy = slider_y + slider_h // 2                              # Posizione Y del cursore (centro della barra)
    pygame.draw.circle(schermo, (255, 255, 255), (cx, cy), 10) # Disegna il cursore bianco
    font  = pygame.font.Font(None, 28)                         # Crea il font per l'etichetta
    label = font.render(f"Volume: {int(volume_corrente * 100)}%", True, (255, 255, 255))  # Testo percentuale volume
    schermo.blit(label, (slider_x, slider_y - 25))             # Disegna l'etichetta sopra la barra


def draw_exit_button():
    _draw_btn((exit_button_x, exit_button_y, exit_button_w, exit_button_h),
              "EXIT", (100, 100, 100), (150, 150, 150), font_size=30)  # Grigio scuro normale, grigio chiaro hover


def draw_back_button():
    _draw_btn((back_button_x, back_button_y, back_button_w, back_button_h),
              "RETURN TO THE MENU", (100, 100, 100), (150, 150, 150), font_size=30)  # Grigio scuro normale, grigio chiaro hover


def draw_exit_game_button():
    _draw_btn((exit_game_button_x, exit_game_button_y, exit_game_button_w, exit_game_button_h),
              "EXIT THE GAME", (200, 60, 60), (255, 100, 100), font_size=30)  # Rosso scuro normale, rosso chiaro hover


def draw_inizia_button():
    _draw_btn((inizia_button_x, inizia_button_y, inizia_button_w, inizia_button_h),
              "START", (50, 200, 100), (80, 255, 130))         # Verde scuro normale, verde chiaro hover


def draw_istruzioni():
    draw_background()                                           # Disegna l'immagine di sfondo

    # ── Costanti di layout ────────────────────────────────────
    FONT_TESTO   = 40                                          # Dimensione font testo istruzioni
    FONT_TITOLO  = 80                                          # Dimensione font titolo ISTRUZIONI
    FONT_SUB     = 46                                          # Dimensione font sottotitolo direzioni
    FONT_LABEL   = 36                                          # Dimensione font etichette card
    INTERLINEA   = 50                                          # Spazio verticale tra le righe di testo
    IMG_SIZE     = 140                                         # Lato quadrato di ogni card immagine
    CARD_SPACING = 35                                          # Spazio orizzontale tra le card
    MARG         = 50                                          # Margine laterale del pannello

    # ── Righe di testo (spezzate per stare a font 40px) ──────
    righe_testo = [
        "Hello and welcome to ITIS Explorer!",              # Prima riga (in giallo)
        "Get ready for a unique immersive experience:",   # Riga 2
        "an interactive journey within our school,",  # Riga 3
        "where technology, learning and fun meet.",  # Riga 4
        "Drive the Alpha Bot along the way,",               # Riga 5
        "overcome challenges and complete missions",              # Riga 6
        "with the following commands:",                             # Riga 7
    ]

    # ── Calcolo altezze per dimensionare il pannello ─────────
    titolo_h    = 70                                           # Altezza riservata alla barra del titolo
    testo_h     = len(righe_testo) * INTERLINEA               # Altezza totale del blocco testo
    sub_h       = 55                                           # Altezza del sottotitolo direzioni
    card_h      = IMG_SIZE + 45                                # Altezza card + etichetta sotto
    padding_int = 20                                           # Padding interno tra sezioni

    pannello_x  = MARG                                        # X sinistra del pannello
    pannello_y  = 30                                           # Y superiore del pannello
    pannello_w  = width - MARG * 2                            # Larghezza del pannello
    pannello_h  = titolo_h + testo_h + sub_h + card_h + padding_int * 4  # Altezza totale pannello

    # ── Window effect: pannello semitrasparente ───────────────
    overlay = pygame.Surface((pannello_w, pannello_h), pygame.SRCALPHA)   # Superficie con canale alpha
    overlay.fill((255, 255, 255, 200))                                         
    schermo.blit(overlay, (pannello_x, pannello_y))                        # Disegna il pannello sullo sfondo

    # Bordo esterno verde arrotondato (uguale per tutto il pannello, titolo incluso)
    pygame.draw.rect(schermo, (50, 200, 100),
                     (pannello_x, pannello_y, pannello_w, pannello_h),
                     width=3, border_radius=22)                            # Bordo verde arrotondato

    # Barra titolo con stesso sfondo del pannello (overlay identico, senza colore diverso)
    barra_overlay = pygame.Surface((pannello_w - 6, titolo_h), pygame.SRCALPHA)  # Stessa superficie del pannello
    barra_overlay.fill((255, 255, 255, 100))                               # Stesso riempimento del pannello
    schermo.blit(barra_overlay, (pannello_x + 3, pannello_y + 3))         # Sovrapposta nella zona titolo

    pygame.draw.rect(schermo, (50, 200, 100),
                     (pannello_x + 3, pannello_y + 3, pannello_w - 6, titolo_h),
                     width=1, border_radius=20)                            # Bordo interno verde della barra titolo

    # Linea separatrice sotto la barra titolo
    sep_y = pannello_y + titolo_h + 3                                      # Y della linea separatrice
    pygame.draw.line(schermo, (50, 200, 100),
                     (pannello_x + 20, sep_y),
                     (pannello_x + pannello_w - 20, sep_y), 2)             # Linea orizzontale verde

    # ── Titolo "ISTRUZIONI" centrato nella barra ──────────────
    font_titolo = pygame.font.Font(None, FONT_TITOLO)          # Font grande per il titolo
    titolo      = font_titolo.render("INSTRUCTION", True, (50, 200, 100))   # Testo verde
    schermo.blit(titolo, titolo.get_rect(center=(width // 2, pannello_y + titolo_h // 2 + 3)))  # Centra nella barra

    # ── Testo delle istruzioni ───────────────────────────────
    font_testo = pygame.font.Font(None, FONT_TESTO)            # Font per il testo corpo
    testo_y    = pannello_y + titolo_h + padding_int + 10      # Y di partenza del testo (sotto la barra titolo)

    for i, riga in enumerate(righe_testo):                     # Scorre ogni riga
        colore = (50, 200, 100) if i == 0 else (0, 0, 0)      # Prima riga verde, le altre nere
        surf   = font_testo.render(riga, True, colore)         # Renderizza la riga
        schermo.blit(surf, surf.get_rect(center=(width // 2, testo_y + i * INTERLINEA)))  # Centra e disegna

    # ── Sottotitolo "Direzioni del robot:" ───────────────────
    font_sub  = pygame.font.Font(None, FONT_SUB)               # Font sottotitolo
    sub_y     = testo_y + len(righe_testo) * INTERLINEA + padding_int  # Y del sottotitolo
    sub       = font_sub.render("Robot directions:", True, (50, 200, 100))  # Testo verde
    schermo.blit(sub, sub.get_rect(center=(width // 2, sub_y)))  # Centra e disegna

    # ── 5 card immagine + etichetta ──────────────────────────
    direzioni = [
        ("FORWARD",   img_avanti),                              # Direzione avanti
        ("BACK", img_indietro),                            # Direzione indietro
        ("RIGHT",   img_destra),                              # Direzione destra
        ("LEFT", img_sinistra),                            # Direzione sinistra
        ("STOP",    img_fermo),                               # Fermo
    ]

    n        = len(direzioni)                                  # Numero di direzioni
    total_w  = n * IMG_SIZE + (n - 1) * CARD_SPACING          # Larghezza totale delle card
    card_x0  = width // 2 - total_w // 2                      # X di partenza per centrare le card
    card_top = sub_y + sub_h - 10                              # Y del bordo superiore delle card

    font_label = pygame.font.Font(None, FONT_LABEL)            # Font etichette direzioni

    for i, (nome, img) in enumerate(direzioni):                # Scorre ogni direzione
        cx = card_x0 + i * (IMG_SIZE + CARD_SPACING)          # Calcola la X della card corrente

        # Sfondo card con gradiente visivo (bordo + fill)
        pygame.draw.rect(schermo, (50, 200, 100),
                         (cx - 5, card_top - 5, IMG_SIZE + 10, IMG_SIZE + 10),
                         border_radius=14)                     # Bordo verde esterno
        pygame.draw.rect(schermo, (15, 15, 15),
                         (cx, card_top, IMG_SIZE, IMG_SIZE),
                         border_radius=10)                     # Sfondo molto scuro della card

        if img:                                                # Se l'immagine è caricata
            iw, ih  = img.get_size()                          # Dimensioni originali
            ratio   = min(IMG_SIZE / iw, IMG_SIZE / ih)       # Rapporto di scala
            scaled  = pygame.transform.scale(img, (int(iw * ratio), int(ih * ratio)))  # Ridimensiona
            off_x   = (IMG_SIZE - scaled.get_width())  // 2   # Offset X per centrare
            off_y   = (IMG_SIZE - scaled.get_height()) // 2   # Offset Y per centrare
            schermo.blit(scaled, (cx + off_x, card_top + off_y))  # Disegna l'immagine centrata
        else:                                                  # Immagine non ancora disponibile
            font_ph = pygame.font.Font(None, 26)              # Font placeholder
            ph      = font_ph.render("[ immagine ]", True, (130, 130, 130))  # Testo grigio
            schermo.blit(ph, ph.get_rect(center=(cx + IMG_SIZE // 2, card_top + IMG_SIZE // 2)))  # Centra

        # Etichetta direzione sotto la card con piccolo sfondo scuro per leggibilità
        label      = font_label.render(nome, True, (255, 255, 255))  # Testo bianco
        label_rect = label.get_rect(center=(cx + IMG_SIZE // 2, card_top + IMG_SIZE + 24))  # Posizione etichetta
        bg_rect    = label_rect.inflate(16, 8)                 # Rettangolo sfondo leggermente più grande del testo
        pygame.draw.rect(schermo, (0, 0, 0, 120), bg_rect, border_radius=8)  # Sfondo scuro sotto l'etichetta
        schermo.blit(label, label_rect)                        # Disegna l'etichetta

    draw_back_button()                                         # Disegna il pulsante TORNA AL MENU in alto a sinistra
    draw_inizia_button()                                       # Disegna il pulsante INIZIA centrato in basso


def draw():
    schermo.fill((0, 0, 0))                                    # Riempie lo schermo di nero (cancella il frame precedente)

    if Stato_schermo == "menu":                                # Se siamo nel menu
        if started:                                            # Se il gioco è già stato avviato con il primo click
            draw_background()                                  # Disegna l'immagine di sfondo
            draw_logo()                                        # Disegna il logo
            draw_volume_button()                               # Disegna il pulsante VOLUME
            draw_button()                                      # Disegna il pulsante GIOCA
            draw_exit_button()                                 # Disegna il pulsante ESCI
        else:                                                  # Se il gioco non è ancora stato avviato
            font = pygame.font.Font(None, 36)                  # Crea il font di dimensione 36
            text = font.render("Click to start the game", True, (255, 255, 255))  # Renderizza il testo iniziale
            text_rect = text.get_rect(center=(width // 2, height // 2))               # Centra il testo nello schermo
            schermo.blit(text, text_rect)                      # Disegna il testo sullo schermo

    elif Stato_schermo == "istruzioni":                        # Se siamo nella schermata istruzioni
        draw_istruzioni()                                      # Disegna tutta la schermata istruzioni

    elif Stato_schermo == "game":                              # Se siamo nella schermata di gioco
        frame = get_webcam_frame()                             # Ottiene il frame corrente dalla webcam
        if frame:                                              # Se il frame è valido
            cw, ch = frame.get_size()                          # Ottiene le dimensioni del frame webcam
            ratio  = min(width / cw, height / ch)              # Calcola il rapporto di scala per adattarlo allo schermo
            w, h   = int(cw * ratio), int(ch * ratio)          # Calcola le nuove dimensioni del frame
            scaled = pygame.transform.scale(frame, (w, h))     # Ridimensiona il frame
            schermo.blit(scaled, ((width - w) // 2, (height - h) // 2))  # Centra e disegna il frame sullo schermo

        draw_back_button()                                     # Disegna il pulsante TORNA AL MENU
        draw_exit_game_button()                                # Disegna il pulsante ESCI DAL GIOCO

    pygame.display.flip()                                      # Aggiorna lo schermo mostrando tutto ciò che è stato disegnato


def handle_music():
    global current_song                                        # Dichiara la variabile globale da modificare

    if not started:                                            # Se siamo sulla schermata nera, nessuna musica
        return

    if Stato_schermo in ("menu", "istruzioni"):                # La musica suona nel menu e nella schermata istruzioni
        if not mixer.music.get_busy():                         # Se la musica non sta suonando
            if current_song == 1:
                mixer.music.load(song1)                        # Carica la prima canzone
                mixer.music.play()                             # Avvia la riproduzione
                mixer.music.set_volume(volume_corrente)        # Applica il volume corrente
                current_song = 2                               # La prossima sarà la seconda
            else:
                mixer.music.load(song2)                        # Carica la seconda canzone
                mixer.music.play()                             # Avvia la riproduzione
                mixer.music.set_volume(volume_corrente)        # Applica il volume corrente
                current_song = 1                               # La prossima sarà la prima
    elif Stato_schermo == "game":                              # Nel gioco la musica viene fermata
        if mixer.music.get_busy():                             # Se la musica sta suonando
            mixer.music.stop()                                 # Fermala


def cleanup_and_exit():
    global Attivazione_Camera                                  # Dichiara la variabile globale da modificare
    mixer.music.stop()                                         # Ferma la riproduzione musicale
    if Attivazione_Camera:                                     # Se la webcam è attiva
        Attivazione_Camera.release()                           # Rilascia la webcam liberando le risorse
    pygame.quit()                                              # Chiude pygame
    sys.exit()                                                 # Termina il programma


def mouse_pressed(pos):
    global started, Stato_schermo, Attivazione_Camera, current_song  # Dichiara le variabili globali da modificare
    global mostra_slider_volume, volume_corrente

    mouse_x, mouse_y = pos                                     # Estrae le coordinate x e y del click

    if not started:                                            # Se è il primo click (gioco non ancora avviato)
        started = True                                         # Segna il gioco come avviato
        return                                                 # Esce dalla funzione senza controllare altri pulsanti

    if Stato_schermo == "game":                                # Se siamo nella schermata di gioco
        if (back_button_x < mouse_x < back_button_x + back_button_w and    # Controlla click su TORNA AL MENU
                back_button_y < mouse_y < back_button_y + back_button_h):
            Stato_schermo = "menu"                             # Torna al menu
            if Attivazione_Camera:                             # Se la webcam è attiva
                Attivazione_Camera.release()                   # Rilascia la webcam
                Attivazione_Camera = None                      # Reimposta la variabile a None

        elif (exit_game_button_x < mouse_x < exit_game_button_x + exit_game_button_w and  # Controlla click su ESCI DAL GIOCO
              exit_game_button_y < mouse_y < exit_game_button_y + exit_game_button_h):
            cleanup_and_exit()                                 # Chiude il programma

    elif Stato_schermo == "istruzioni":                        # Se siamo nella schermata istruzioni
        if (back_button_x < mouse_x < back_button_x + back_button_w and    # Controlla click su TORNA AL MENU
                back_button_y < mouse_y < back_button_y + back_button_h):
            Stato_schermo = "menu"                             # Torna al menu principale

        elif (inizia_button_x < mouse_x < inizia_button_x + inizia_button_w and  # Controlla click su INIZIA
              inizia_button_y < mouse_y < inizia_button_y + inizia_button_h):
            Stato_schermo      = "game"                        # Passa alla schermata di gioco
            Attivazione_Camera = cv2.VideoCapture(0)           # Apre la webcam (0 = webcam predefinita)

    elif Stato_schermo == "menu":                              # Se siamo nel menu principale
        if (exit_button_x < mouse_x < exit_button_x + exit_button_w and    # Controlla click su ESCI
                exit_button_y < mouse_y < exit_button_y + exit_button_h):
            cleanup_and_exit()                                 # Chiude il programma

        elif (button_x < mouse_x < button_x + button_w and   # Controlla click su GIOCA
              button_y < mouse_y < button_y + button_h):
            Stato_schermo        = "istruzioni"                # Va alla schermata istruzioni (prima del gioco)
            mostra_slider_volume = False                       # Nasconde lo slider del volume

        elif (volume_button_x < mouse_x < volume_button_x + volume_button_w and  # Controlla click su VOLUME
              volume_button_y < mouse_y < volume_button_y + volume_button_h):
            mostra_slider_volume = not mostra_slider_volume    # Alterna la visibilità dello slider

        elif mostra_slider_volume and (slider_x <= mouse_x <= slider_x + slider_w and  # Controlla click sulla barra
                                       slider_y - 15 <= mouse_y <= slider_y + slider_h + 15):
            volume_corrente = max(0.0, min(1.0, (mouse_x - slider_x) / slider_w))  # Calcola il nuovo volume
            mixer.music.set_volume(volume_corrente)            # Applica il nuovo volume


def mouse_motion(pos):
    global volume_corrente                                     # Dichiara la variabile globale da modificare
    if slider_dragging and mostra_slider_volume and Stato_schermo == "menu":  # Se il cursore è in dragging
        mouse_x, _ = pos                                       # Legge solo la coordinata X del mouse
        volume_corrente = max(0.0, min(1.0, (mouse_x - slider_x) / slider_w))  # Calcola il volume in base alla posizione
        mixer.music.set_volume(volume_corrente)                # Aggiorna il volume in tempo reale


def mouse_button_down(pos):
    global slider_dragging                                     # Dichiara la variabile globale da modificare
    mouse_x, mouse_y = pos                                     # Estrae le coordinate del click
    if mostra_slider_volume and Stato_schermo == "menu":       # Se lo slider è visibile e siamo nel menu
        cx = slider_x + int(slider_w * volume_corrente)        # Posizione X del cursore sullo slider
        cy = slider_y + slider_h // 2                          # Posizione Y del cursore sullo slider
        if abs(mouse_x - cx) <= 15 and abs(mouse_y - cy) <= 15:  # Se il click è vicino al cursore
            slider_dragging = True                             # Attiva il dragging del cursore


def mouse_button_up():
    global slider_dragging                                     # Dichiara la variabile globale da modificare
    slider_dragging = False                                    # Disattiva il dragging quando si rilascia il mouse


def main():
    global width, height                                       # Dichiara le variabili globali da modificare

    setup()                                                    # Inizializza lo schermo e carica le risorse
    clock = pygame.time.Clock()                                # Crea un oggetto clock per controllare i FPS

    while True:                                                # Loop principale del gioco (gira all'infinito)
        for event in pygame.event.get():                       # Controlla tutti gli eventi pygame in coda
            if event.type == pygame.QUIT:                      # Se l'utente chiude la finestra
                cleanup_and_exit()                             # Chiude il programma
            elif event.type == pygame.MOUSEBUTTONDOWN:         # Se l'utente clicca con il mouse
                mouse_button_down(event.pos)                   # Controlla se inizia il dragging dello slider
                mouse_pressed(event.pos)                       # Gestisce il click passando la posizione
            elif event.type == pygame.MOUSEBUTTONUP:           # Se l'utente rilascia il mouse
                mouse_button_up()                              # Disattiva il dragging
            elif event.type == pygame.MOUSEMOTION:             # Se il mouse si muove
                mouse_motion(event.pos)                        # Aggiorna il volume se in dragging
            elif event.type == pygame.KEYDOWN:                 # Se l'utente preme un tasto
                if event.key == pygame.K_ESCAPE:               # Se il tasto è ESC
                    cleanup_and_exit()                         # Chiude il programma

        draw()                                                 # Disegna tutti gli elementi sullo schermo
        handle_music()                                         # Controlla e gestisce la riproduzione musicale
        clock.tick(30)                                         # Limita il loop a 30 FPS


if __name__ == "__main__":                                     # Controlla che il file venga eseguito direttamente
    main()                                                     # Avvia il programma