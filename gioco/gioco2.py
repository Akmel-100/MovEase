"""
Logical Reasoning Game
Designed for people with Multiple Sclerosis

Characteristics:
- simple and clear interface
- Focus on reasoning, not on physical speed or accuracy
- Positive and encouraging feedback

CONTROLS:
- Click to reply
- ESC = Exit the game
- M = Pause/resume music
- + = Increase volume
- - = Decrease volume
"""

import pygame                          # Libreria per la grafica e la gestione degli eventi
import random                          # Libreria per scegliere puzzle casuali
import time                            # Libreria per la gestione del tempo
from dataclasses import dataclass      # Decoratore per creare classi dati semplici
from typing import List                # Tipo per annotare liste nelle funzioni

@dataclass
class Puzzle:
    """Rappresenta un puzzle logico"""
    domanda: str                        # Testo della domanda da mostrare al giocatore
    opzioni: List[str]                  # Lista delle possibili risposte
    risposta_corretta: int              # Indice (0-3) della risposta corretta nella lista opzioni
    spiegazione: str                    # Spiegazione mostrata se la risposta è sbagliata

# -------------------------------
# Inizializzazione Pygame (FULLSCREEN)
# -------------------------------
pygame.init()                                                        # Inizializza tutti i moduli di pygame
pygame.mixer.init()                                                  # Inizializza il modulo audio per la musica

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)          # Crea la finestra a schermo intero
WIDTH, HEIGHT = screen.get_size()                                    # Ottiene la risoluzione attuale dello schermo
pygame.display.set_caption("Logical Reasoning Game")           # Imposta il titolo della finestra

try:
    nome_file_musica = "MI.mp3"                                      # Nome del file audio da caricare
    pygame.mixer.music.load(nome_file_musica)                        # Carica il file musicale nel mixer
    pygame.mixer.music.set_volume(0.3)                               # Imposta il volume al 30% (0.0 = muto, 1.0 = massimo)
    pygame.mixer.music.play(-1)                                      # Avvia la musica in loop infinito (-1 = ripeti sempre)
    
    print("=" * 60)
    print("SUCCESSFULLY UPLOADED MUSIC!")
    print(f"  File: {nome_file_musica}")
    print(f"  initial volume: 30%")
    print("=" * 60)
    print("\nMUSIC CONTROLS:")
    print("  M = Break/Resume music")
    print("  + = Increase volume")
    print("  - = Decrease volume")
    print("=" * 60)
    
except pygame.error as e:              # Se il file non esiste o non è leggibile
    print("=" * 60)
    print("⚠ ATTENZIONE: FILE MUSICALE NON TROVATO")
    print("=" * 60)
    print(f"Errore: {e}")
    print("\nIL GIOCO CONTINUERÀ SENZA MUSICA")
    print("\nPer aggiungere la musica:")
    print("1. Trova un file audio (.mp3, .ogg, .wav)")
    print("2. Rinominalo 'background_music.mp3'")
    print("3. Mettilo nella stessa cartella di questo script")
    print("4. Riavvia il gioco")
    print("=" * 60)

# Font di diverse dimensioni per i vari elementi dell'interfaccia
font_titolo = pygame.font.SysFont("Segoe UI", 48, bold=True)         # Font grande per i titoli
font_domanda = pygame.font.SysFont("Segoe UI", 32)                   # Font per il testo delle domande
font_opzioni = pygame.font.SysFont("Segoe UI", 28)                   # Font per il testo delle opzioni di risposta
font_punteggio = pygame.font.SysFont("Segoe UI", 30)                 # Font per il punteggio e contatori
font_spiegazione = pygame.font.SysFont("Segoe UI", 24)               # Font per le spiegazioni delle risposte errate
small_font = pygame.font.SysFont("Segoe UI", 20)                     # Font piccolo per testi secondari

clock = pygame.time.Clock()                                          # Oggetto per controllare i FPS

# -------------------------------
# Colori
# -------------------------------
WHITE = (255, 255, 255)                # Bianco
RED = (255, 80, 80)                    # Rosso (risposta sbagliata)
GREEN = (80, 200, 120)                 # Verde (risposta corretta)
BLUE = (80, 120, 255)                  # Blu (pulsanti normali)
YELLOW = (255, 220, 80)                # Giallo (avvisi)
DARK_TEXT = (40, 40, 40)               # Grigio scuro per i testi
LIGHT_BLUE = (240, 245, 255)           # Azzurro chiaro (sfondo in alto)
DARKER_BLUE = (200, 220, 255)          # Azzurro più scuro (sfondo in basso)

# -------------------------------
# Funzioni utility
# -------------------------------
def draw_gradient(surface, top_color, bottom_color):
    """Disegna un gradiente verticale"""
    for y in range(HEIGHT):                                                    # Itera su ogni riga dello schermo
        ratio = y / HEIGHT                                                     # Rapporto di interpolazione (0.0 in alto, 1.0 in basso)
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)        # Interpola il canale rosso
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)        # Interpola il canale verde
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)        # Interpola il canale blu
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))              # Disegna la riga con il colore calcolato

def draw_rounded_rect(surface, color, rect, radius=15):
    """Disegna un rettangolo con angoli arrotondati"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)              # Disegna il rettangolo con raggio degli angoli specificato

def draw_button(surface, text, rect, color, hover=False, text_color=WHITE):
    """Disegna un bottone con effetto hover"""
    if hover:                                                                  # Se il mouse è sopra il pulsante
        glow_rect = pygame.Rect(rect.x - 3, rect.y - 3, rect.width + 6, rect.height + 6)  # Rettangolo leggermente più grande per il bagliore
        draw_rounded_rect(surface, tuple(min(255, c + 30) for c in color), glow_rect, 20)  # Disegna il bagliore esterno con colore più chiaro
    
    draw_rounded_rect(surface, color, rect, 15)                               # Disegna il rettangolo principale del pulsante
    
    text_surf = font_opzioni.render(text, True, text_color)                   # Renderizza il testo del pulsante
    text_rect = text_surf.get_rect(center=rect.center)                        # Centra il testo nel rettangolo del pulsante
    surface.blit(text_surf, text_rect)                                        # Disegna il testo sul pulsante

def wrap_text(text, font, max_width):
    """Divide il testo in più righe se necessario"""
    words = text.split(' ')                                                    # Divide il testo in parole
    lines = []                                                                 # Lista delle righe risultanti
    current_line = []                                                          # Parole della riga corrente
    
    for word in words:                                                         # Per ogni parola nel testo
        test_line = ' '.join(current_line + [word])                           # Prova ad aggiungere la parola alla riga corrente
        if font.size(test_line)[0] <= max_width:                              # Se la riga non supera la larghezza massima
            current_line.append(word)                                         # Aggiunge la parola alla riga corrente
        else:                                                                  # Se la riga supererebbe la larghezza massima
            if current_line:                                                   # Se c'è già del testo nella riga corrente
                lines.append(' '.join(current_line))                          # Salva la riga corrente
            current_line = [word]                                             # Inizia una nuova riga con la parola corrente
    
    if current_line:                                                           # Se rimangono parole nell'ultima riga
        lines.append(' '.join(current_line))                                  # Aggiunge l'ultima riga
    
    return lines                                                               # Restituisce la lista di righe

# -------------------------------
# Classe principale del gioco
# -------------------------------
class GiocoRagionamento:
    def __init__(self):
        self.punteggio = 0                         # Punteggio totale del giocatore
        self.puzzle_completati = 0                 # Numero di puzzle affrontati (corretti + sbagliati)
        self.puzzle_corrente = None                # Puzzle attualmente visualizzato (oggetto Puzzle)
        self.puzzles = self.crea_puzzles()         # Lista di tutti i puzzle disponibili
        self.risposta_selezionata = None           # Indice della risposta cliccata (None = non ancora risposto)
        self.mostra_spiegazione = False            # True se deve mostrare la spiegazione (risposta sbagliata)
        self.timer_prossima = 0                    # Timestamp in ms in cui passare al prossimo puzzle
        self.game_state = "menu"                   # Stato attuale: "menu", "gioco" o "risultato"
        self.mouse_pos = (0, 0)                    # Posizione corrente del mouse (aggiornata nel loop)
        self.musica_attiva = True                  # Flag che indica se la musica è in riproduzione
        
    def crea_puzzles(self) -> List[Puzzle]:
        """Crea una collezione di puzzle di ragionamento logico"""
        return [
            # Sequenze numeriche
            Puzzle(
                "Complete the sequence: 2, 4, 8, 16, ?",
                ["24", "30", "32", "64"],
                2,                                 # Risposta corretta: indice 2 = "32"
                "Each number is double the previous one: 2×2=4, 4×2=8, 8×2=16, 16×2=32"
            ),
            Puzzle(
                "Complete the sequence: 3, 6, 9, 12, ?",
                ["14", "15", "16", "18"],
                1,                                 # Risposta corretta: indice 1 = "15"
                "Add 3 each time: 3+3=6, 6+3=9, 9+3=12, 12+3=15"
            ),
            Puzzle(
                "Complete the sequence: 100, 90, 80, 70, ?",
                ["65", "60", "55", "50"],
                1,                                 # Risposta corretta: indice 1 = "60"
                "Subtract 10 each time: 100-10=90, 90-10=80, 80-10=70, 70-10=60"
            ),
            
            # Logica deduttiva
            Puzzle(
                "Mark is taller than Luke. Luke is taller than Anna. Who is the shortest?",
                ["Marco", "Luca", "Anna", "impossible to say"],
                2,                                 # Risposta corretta: indice 2 = "Anna"
                "If Mark > Luke and Luke > Anna, then Anna is the lowest."
            ),
            Puzzle(
                "All cats have 4 legs. Fuffi is a cat. How many legs does Fuffi have?",
                ["2", "3", "4", "Depends"],
                2,                                 # Risposta corretta: indice 2 = "4"
                "If all cats have 4 legs and Fuffi is a cat, then Fuffi has 4 legs."
            ),
            Puzzle(
                "All fish live in water. Salmon is a fish. Where does salmon live?",
                ["On the earth", "In water", "On the trees", "In the desert"],
                1,                                 # Risposta corretta: indice 1 = "In acqua"
                "If all fish live in water and salmon is a fish, then salmon lives in water."
            ),
            
            # Categorizzazione
            Puzzle(
                "Which word does NOT belong to the group? Apple, Banana, Carrot, Orange",
                ["Apple", "Banana", "Carrot", "Orange"],
                2,                                 # Risposta corretta: indice 2 = "Carota"
                "Carrot is a vegetable, while the others are fruits."
            ),
            Puzzle(
                "Which number does NOT belong to the group? 2, 4, 6, 9, 8",
                ["2", "4", "9", "8"],
                2,                                 # Risposta corretta: indice 2 = "9"
                "9 is odd, while all others are even numbers."
            ),
            
            # Problemi logici
            Puzzle(
                "I have 5 apples. I give 2 to Mary and 1 to Paul. How many do I have left?",
                ["1", "2", "3", "4"],
                1,                                 # Risposta corretta: indice 1 = "2"
                "5 - 2 - 1 = 2 apples left."
            ),
            Puzzle(
                "A train leaves at 2:30 PM and arrives at 4:00 PM. How long is the trip?",
                ["1 hour", "1.5 hours", "2 hours", "2.5 hours"],
                1,                                 # Risposta corretta: indice 1 = "1 ora e 30 minuti"
                "From 2:30 PM to 4:00 PM, 1 hour and 30 minutes pass."
            ),
            
            # Analogie
            Puzzle(
                "Hot is to Cold as High is to?",
                ["Big", "Low", "Long", "Strong"],
                1,                                 # Risposta corretta: indice 1 = "Basso"
                "Hot and Cold are opposites, like High and Low."
            ),
            Puzzle(
                "Doctor is in Hospital as Teacher is in?",
                ["House", "School", "Office", "Shop"],
                1,                                 # Risposta corretta: indice 1 = "Scuola"
                "The doctor works in the hospital, the teacher works at school."
            ),
            
            # Pattern e relazioni
            Puzzle(
                "If A=1, B=2, C=3, how much is the sequence'CAB'?",
                ["4", "5", "6", "7"],
                2,                                 # Risposta corretta: indice 2 = "6"
                "C=3, A=1, B=2. then 3+1+2=6"
            ),
            Puzzle(
                "What's next day after Monday, Wednesday, Friday?",
                ["Saturday", "Sunday", "Thursday", "Tuesday"],
                1,                                 # Risposta corretta: indice 1 = "Domenica"
                "The pattern skips one day each time: Mon→Wed→Fri→Sun"
            ),
        ]
    
    def prossimo_puzzle(self):
        """Carica il prossimo puzzle"""
        if not self.puzzles:                                       # Se non ci sono più puzzle disponibili
            self.game_state = "risultato"                          # Passa alla schermata dei risultati finali
            return
        
        self.puzzle_corrente = random.choice(self.puzzles)         # Sceglie un puzzle casuale dalla lista
        self.puzzles.remove(self.puzzle_corrente)                  # Rimuove il puzzle scelto per non ripeterlo
        self.risposta_selezionata = None                           # Azzera la risposta selezionata
        self.mostra_spiegazione = False                            # Nasconde la spiegazione
        self.timer_prossima = 0                                    # Azzera il timer di avanzamento automatico
        self.game_state = "gioco"                                  # Imposta lo stato a "gioco"
    
    def verifica_risposta(self, indice):
        """Verifica la risposta selezionata"""
        self.risposta_selezionata = indice                         # Salva l'indice della risposta cliccata
        self.puzzle_completati += 1                                # Incrementa il contatore dei puzzle affrontati
        
        if indice == self.puzzle_corrente.risposta_corretta:       # Se la risposta è corretta
            self.punteggio += 10                                   # Aggiunge 10 punti al punteggio
            self.timer_prossima = pygame.time.get_ticks() + 800   # Passa al prossimo puzzle dopo 800ms
            self.mostra_spiegazione = False                        # Non mostrare la spiegazione
        else:                                                      # Se la risposta è sbagliata
            self.mostra_spiegazione = True                         # Mostra la spiegazione della risposta corretta
            self.timer_prossima = pygame.time.get_ticks() + 3000  # Aspetta 3 secondi prima di avanzare
    
    def toggle_musica(self):
        """Attiva/disattiva la musica di sottofondo (tasto M)"""
        try:
            if self.musica_attiva:                                 # Se la musica è in riproduzione
                pygame.mixer.music.pause()                         # Mette in pausa la musica
                self.musica_attiva = False                         # Aggiorna il flag
                print("🔇 Music on pause")
            else:                                                  # Se la musica è in pausa
                pygame.mixer.music.unpause()                       # Riprende la riproduzione
                self.musica_attiva = True                          # Aggiorna il flag
                print("🔊 Music resumed")
        except:
            print("No music loaded")                    # Messaggio se non c'è musica
    
    def cambia_volume(self, delta):
        """Cambia il volume della musica (tasti + e -)"""
        try:
            volume_attuale = pygame.mixer.music.get_volume()       # Ottiene il volume attuale (0.0-1.0)
            nuovo_volume = max(0.0, min(1.0, volume_attuale + delta))  # Calcola il nuovo volume tenendolo tra 0 e 1
            pygame.mixer.music.set_volume(nuovo_volume)            # Imposta il nuovo volume
            percentuale = int(nuovo_volume * 100)                  # Converte in percentuale per il log
            
            if nuovo_volume == 0:                                  # Sceglie l'icona in base al livello del volume
                icona = "🔇"                                       # Muto
            elif nuovo_volume < 0.3:
                icona = "🔉"                                       # Volume basso
            else:
                icona = "🔊"                                       # Volume alto
            
            print(f"{icona} Volume: {percentuale}%")
        except:
            print("No music loaded")
    
    def draw_menu(self):
        """Disegna il menu iniziale"""
        draw_gradient(screen, LIGHT_BLUE, DARKER_BLUE)             # Sfondo sfumato blu
        
        title = font_titolo.render("Logical Reasoning Game", True, DARK_TEXT)          # Renderizza il titolo
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))                          # Disegna il titolo centrato
        
        panel_width = 900
        panel_height = 500
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)                    # Crea il pannello semi-trasparente
        panel.fill((255, 255, 255, 230))                                                        # Riempie di bianco semi-trasparente
        screen.blit(panel, (WIDTH // 2 - panel_width // 2, HEIGHT // 2 - panel_height // 2 - 50))  # Disegna il pannello centrato
        
        instructions = [
            "Welcome to the Reasoning Game!",
            "",
            "• Read each question carefully",
            "• Click on the answer you think is correct",
            "• If you answer well, move on to the next question right away",
            "• If you are wrong, you will see the explanation before continuing",
            "",
            f"Total puzzles: {len(self.crea_puzzles())}",            # Mostra il numero totale di puzzle disponibili
            "",
            "Click to get started!"
        ]
        
        y_offset = HEIGHT // 2 - panel_height // 2 - 20             # Posizione Y iniziale del testo
        for i, line in enumerate(instructions):                      # Per ogni riga di istruzioni
            if line == "Welcome to the Reasoning Game!":        # Il titolo delle istruzioni usa un font e colore diverso
                text = font_domanda.render(line, True, BLUE)
            else:
                text = font_punteggio.render(line, True, DARK_TEXT)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset + i * 45))  # Disegna ogni riga centrata e spaziata
        
        controls = small_font.render("M=Music | +=Volume+ | -=Volume- | ESC=Exit", True, DARK_TEXT)  # Testo controlli
        screen.blit(controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT - 50))                  # Disegna in fondo allo schermo
    
    def draw_gioco(self):
        """Disegna la schermata di gioco"""
        draw_gradient(screen, LIGHT_BLUE, DARKER_BLUE)             # Sfondo sfumato blu
        
        # HUD con punteggio e contatore
        hud = pygame.Surface((300, 120), pygame.SRCALPHA)           # Crea il pannello HUD semi-trasparente
        hud.fill((255, 255, 255, 200))                              # Riempie di bianco semi-trasparente
        screen.blit(hud, (20, 20))                                  # Disegna l'HUD in alto a sinistra
        
        score_text = font_punteggio.render(f"Score: {self.punteggio}", True, GREEN)      # Testo punteggio in verde
        screen.blit(score_text, (40, 40))                                                    # Disegna il punteggio
        
        count_text = font_punteggio.render(f"complete: {self.puzzle_completati}", True, DARK_TEXT)  # Testo contatore
        screen.blit(count_text, (40, 80))                                                             # Disegna il contatore
        
        music_icon = "🔊" if self.musica_attiva else "🔇"           # Icona musica: altoparlante o muto
        music_text = small_font.render(f"{music_icon} M", True, DARK_TEXT)  # Testo icona musica con hint tasto M
        screen.blit(music_text, (WIDTH - 80, 20))                   # Disegna l'icona musica in alto a destra
        
        panel_width = min(1200, WIDTH - 100)                        # Larghezza del pannello domanda (max 1200px)
        panel_y = 180                                               # Posizione verticale del pannello domanda
        
        domanda_lines = wrap_text(self.puzzle_corrente.domanda, font_domanda, panel_width - 80)  # Divide la domanda in righe
        domanda_height = len(domanda_lines) * 50 + 60               # Calcola l'altezza del pannello in base alle righe
        
        domanda_panel = pygame.Surface((panel_width, domanda_height), pygame.SRCALPHA)  # Crea il pannello domanda
        domanda_panel.fill((255, 255, 255, 240))                    # Riempie di bianco quasi opaco
        screen.blit(domanda_panel, (WIDTH // 2 - panel_width // 2, panel_y))  # Disegna il pannello centrato
        
        y_text = panel_y + 30                                       # Posizione Y iniziale del testo della domanda
        for line in domanda_lines:                                  # Per ogni riga della domanda
            text = font_domanda.render(line, True, DARK_TEXT)       # Renderizza la riga
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_text))  # Disegna la riga centrata
            y_text += 50                                            # Sposta verso il basso per la riga successiva
        
        opzioni_y = panel_y + domanda_height + 40                   # Posizione Y dove iniziano i pulsanti delle opzioni
        button_width = 600                                          # Larghezza di ogni pulsante risposta
        button_height = 70                                          # Altezza di ogni pulsante risposta
        spacing = 20                                                # Spazio verticale tra i pulsanti
        
        for i, opzione in enumerate(self.puzzle_corrente.opzioni):  # Per ogni opzione di risposta
            button_x = WIDTH // 2 - button_width // 2              # Centra il pulsante orizzontalmente
            button_y = opzioni_y + i * (button_height + spacing)   # Posiziona il pulsante verticalmente
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)  # Crea il rettangolo del pulsante
            
            if self.risposta_selezionata is not None:               # Se il giocatore ha già risposto
                if i == self.puzzle_corrente.risposta_corretta:     # Se questo è il pulsante della risposta corretta
                    color = GREEN                                   # Colora di verde
                elif i == self.risposta_selezionata and i != self.puzzle_corrente.risposta_corretta:  # Se è la risposta sbagliata selezionata
                    color = RED                                     # Colora di rosso
                else:
                    color = (150, 150, 150)                         # Grigio per le opzioni non selezionate
            else:                                                   # Se il giocatore non ha ancora risposto
                color = BLUE                                        # Colore normale (blu)
                if button_rect.collidepoint(self.mouse_pos):        # Se il mouse è sopra il pulsante
                    color = (100, 140, 255)                         # Blu più chiaro (effetto hover)
            
            draw_button(screen, opzione, button_rect, color,        # Disegna il pulsante con il colore determinato
                       button_rect.collidepoint(self.mouse_pos) and self.risposta_selezionata is None)  # Hover solo se non ancora risposto
        
        if self.mostra_spiegazione:                                 # Se la risposta era sbagliata e va mostrata la spiegazione
            spieg_y = opzioni_y + 4 * (button_height + spacing) + 30  # Posizione Y del pannello spiegazione (sotto i 4 pulsanti)
            spieg_panel = pygame.Surface((panel_width, 150), pygame.SRCALPHA)  # Crea il pannello spiegazione
            spieg_panel.fill((255, 200, 200, 230))                  # Rosato semi-trasparente per indicare errore
            screen.blit(spieg_panel, (WIDTH // 2 - panel_width // 2, spieg_y))  # Disegna il pannello centrato
            
            wrong_text = font_opzioni.render("wrong answer", True, RED)  # Testo "risposta sbagliata" in rosso
            screen.blit(wrong_text, (WIDTH // 2 - wrong_text.get_width() // 2, spieg_y + 20))  # Disegna il testo centrato
            
            spieg_lines = wrap_text(self.puzzle_corrente.spiegazione, font_spiegazione, panel_width - 80)  # Divide la spiegazione in righe
            y_spieg = spieg_y + 70                                  # Posizione Y iniziale della spiegazione
            for line in spieg_lines:                                # Per ogni riga della spiegazione
                text = font_spiegazione.render(line, True, DARK_TEXT)  # Renderizza la riga
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_spieg))  # Disegna la riga centrata
                y_spieg += 35                                       # Sposta verso il basso per la riga successiva
    
    def draw_risultato(self):
        """Disegna la schermata finale"""
        draw_gradient(screen, (240, 255, 240), (200, 255, 200))    # Sfondo sfumato verde per il successo
        
        panel_width = 700
        panel_height = 450
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)  # Crea il pannello risultato
        pygame.draw.rect(panel, (255, 255, 255, 240), (0, 0, panel_width, panel_height), border_radius=25)   # Rettangolo bianco arrotondato
        pygame.draw.rect(panel, GREEN, (0, 0, panel_width, panel_height), 5, border_radius=25)               # Bordo verde
        screen.blit(panel, (WIDTH // 2 - panel_width // 2, HEIGHT // 2 - panel_height // 2))                 # Disegna il pannello centrato
        
        success_font = pygame.font.SysFont("Segoe UI", 100, bold=True)
        checkmark = success_font.render("✓", True, GREEN)          # Segno di spunta verde gigante
        screen.blit(checkmark, (WIDTH // 2 - checkmark.get_width() // 2, HEIGHT // 2 - 180))  # Disegna il segno centrato
        
        title_font = pygame.font.SysFont("Segoe UI", 60, bold=True)
        title = title_font.render("COMPLIMENTS!", True, GREEN)      # Titolo di completamento in verde
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))  # Disegna il titolo centrato
        
        score_font = pygame.font.SysFont("Segoe UI", 80, bold=True)
        score_text = score_font.render(f"{self.punteggio}", True, (50, 150, 80))  # Punteggio finale in grande
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 30))  # Disegna il punteggio centrato
        
        points_label = font_punteggio.render("POINT", True, (100, 100, 100))       # Etichetta "PUNTI" sotto il numero
        screen.blit(points_label, (WIDTH // 2 - points_label.get_width() // 2, HEIGHT // 2 + 120))
        
        completed_text = font_opzioni.render(f"Puzzles completed: {self.puzzle_completati}", True, DARK_TEXT)  # Numero puzzle completati
        screen.blit(completed_text, (WIDTH // 2 - completed_text.get_width() // 2, HEIGHT // 2 + 170))
        
        esc_info = small_font.render("ESC Presses to Close", True, DARK_TEXT)    # Istruzione per uscire
        screen.blit(esc_info, (WIDTH // 2 - esc_info.get_width() // 2, HEIGHT - 80))  # Disegna in fondo allo schermo
    
    def update(self):
        """Aggiorna lo stato del gioco"""
        if self.game_state == "gioco" and self.risposta_selezionata is not None:   # Se siamo in gioco e il giocatore ha risposto
            if pygame.time.get_ticks() >= self.timer_prossima:                     # Se è scaduto il timer di attesa
                self.prossimo_puzzle()                                             # Carica il prossimo puzzle
    
    def handle_click(self, pos):
        """Gestisce i click del mouse"""
        if self.game_state == "menu":                              # Se siamo nel menu
            self.prossimo_puzzle()                                 # Qualsiasi click avvia il gioco
        
        elif self.game_state == "gioco" and self.risposta_selezionata is None:  # Se siamo in gioco e non si è ancora risposto
            panel_width = min(1200, WIDTH - 100)                   # Larghezza del pannello (stessa di draw_gioco)
            domanda_lines = wrap_text(self.puzzle_corrente.domanda, font_domanda, panel_width - 80)  # Righe della domanda
            domanda_height = len(domanda_lines) * 50 + 60          # Altezza del pannello domanda
            
            opzioni_y = 180 + domanda_height + 40                  # Posizione Y dei pulsanti (deve coincidere con draw_gioco)
            button_width = 600
            button_height = 70
            spacing = 20
            
            for i in range(len(self.puzzle_corrente.opzioni)):     # Per ogni pulsante risposta
                button_x = WIDTH // 2 - button_width // 2         # Posizione X del pulsante
                button_y = opzioni_y + i * (button_height + spacing)  # Posizione Y del pulsante
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)  # Rettangolo del pulsante
                
                if button_rect.collidepoint(pos):                  # Se il click è dentro questo pulsante
                    self.verifica_risposta(i)                      # Verifica la risposta con l'indice del pulsante
                    break                                          # Esce dal ciclo (un solo click per volta)

# -------------------------------
# Main
# -------------------------------
def main():
    gioco = GiocoRagionamento()                                    # Crea l'istanza principale del gioco
    running = True                                                 # Flag per il loop principale
    
    print("\n" + "=" * 60)
    print("GAME STARTED!")
    print("=" * 60)
    
    while running:                                                 # Loop principale del gioco
        gioco.mouse_pos = pygame.mouse.get_pos()                   # Aggiorna la posizione del mouse ad ogni frame
        
        for event in pygame.event.get():                           # Controlla tutti gli eventi pygame
            if event.type == pygame.QUIT:                          # Se si chiude la finestra
                running = False
            
            if event.type == pygame.KEYDOWN:                       # Se si preme un tasto
                if event.key == pygame.K_ESCAPE:                   # ESC = esci dal gioco
                    running = False
                elif event.key == pygame.K_m:                      # M = attiva/disattiva musica
                    gioco.toggle_musica()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:  # + o = aumenta il volume
                    gioco.cambia_volume(0.1)
                elif event.key == pygame.K_MINUS:                  # - diminuisce il volume
                    gioco.cambia_volume(-0.1)
            
            if event.type == pygame.MOUSEBUTTONDOWN:               # Se si clicca con il mouse
                gioco.handle_click(event.pos)                      # Gestisce il click passando le coordinate
        
        gioco.update()                                             # Aggiorna la logica del gioco (timer avanzamento)
        
        if gioco.game_state == "menu":                             # Disegna la schermata corretta in base allo stato
            gioco.draw_menu()
        elif gioco.game_state == "gioco":
            gioco.draw_gioco()
        elif gioco.game_state == "risultato":
            gioco.draw_risultato()
        
        pygame.display.flip()                                      # Aggiorna lo schermo mostrando tutto ciò che è stato disegnato
        clock.tick(30)                                             # Limita il loop a 30 FPS
    
    pygame.mixer.music.stop()                                      # Ferma la musica
    pygame.quit()                                                  # Chiude pygame
    print("\nGame closed. Thanks for playing!")

if __name__ == "__main__":                                         # Esegue main() solo se il file viene avviato direttamente
    main()
