"""
Gioco di Ragionamento Logico
Progettato per persone con Sclerosi Multipla

Caratteristiche:
- Interfaccia semplice e chiara
- Musica di sottofondo rilassante
- Focus sul ragionamento, non sulla velocità o precisione fisica
- Feedback positivo e incoraggiante

CONTROLLI:
- Clicca per rispondere
- ESC = Esci dal gioco
- M = Metti in pausa/riprendi la musica
- + = Aumenta volume
- - = Diminuisci volume
"""

import pygame
import random
import time
from dataclasses import dataclass
from typing import List

@dataclass
class Puzzle:
    """Rappresenta un puzzle logico"""
    domanda: str
    opzioni: List[str]
    risposta_corretta: int
    spiegazione: str

# -------------------------------
# Inizializzazione Pygame (FULLSCREEN)
# -------------------------------
pygame.init()

# Inizializza il mixer audio per la musica
pygame.mixer.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Gioco di Ragionamento Logico")

try:
    # 🎵 CAMBIA IL NOME DEL FILE QUI SE NECESSARIO
    nome_file_musica = "MI.mp3"
    
    # Carica la musica di sottofondo
    pygame.mixer.music.load(nome_file_musica)
    
    # Imposta il volume iniziale (da 0.0 a 1.0)
    # 0.3 = 30% del volume (moderato e non invadente)
    pygame.mixer.music.set_volume(0.3)
    
    # Avvia la musica in loop infinito (-1 = loop continuo)
    pygame.mixer.music.play(-1)
    
    print("=" * 60)
    print("✓ MUSICA CARICATA CON SUCCESSO!")
    print(f"  File: {nome_file_musica}")
    print(f"  Volume iniziale: 30%")
    print("=" * 60)
    print("\nCONTROLLI MUSICA:")
    print("  M = Pausa/Riprendi musica")
    print("  + = Aumenta volume")
    print("  - = Diminuisci volume")
    print("=" * 60)
    
except pygame.error as e:
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

# Font
font_titolo = pygame.font.SysFont("Segoe UI", 48, bold=True)
font_domanda = pygame.font.SysFont("Segoe UI", 32)
font_opzioni = pygame.font.SysFont("Segoe UI", 28)
font_punteggio = pygame.font.SysFont("Segoe UI", 30)
font_spiegazione = pygame.font.SysFont("Segoe UI", 24)
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
DARK_TEXT = (40, 40, 40)
LIGHT_BLUE = (240, 245, 255)
DARKER_BLUE = (200, 220, 255)

# -------------------------------
# Funzioni utility
# -------------------------------
def draw_gradient(surface, top_color, bottom_color):
    """Disegna un gradiente verticale"""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def draw_rounded_rect(surface, color, rect, radius=15):
    """Disegna un rettangolo con angoli arrotondati"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_button(surface, text, rect, color, hover=False, text_color=WHITE):
    """Disegna un bottone con effetto hover"""
    if hover:
        # Effetto glow
        glow_rect = pygame.Rect(rect.x - 3, rect.y - 3, rect.width + 6, rect.height + 6)
        draw_rounded_rect(surface, tuple(min(255, c + 30) for c in color), glow_rect, 20)
    
    draw_rounded_rect(surface, color, rect, 15)
    
    # Testo centrato
    text_surf = font_opzioni.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

def wrap_text(text, font, max_width):
    """Divide il testo in più righe se necessario"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

# -------------------------------
# Classe principale del gioco
# -------------------------------
class GiocoRagionamento:
    def __init__(self):
        self.punteggio = 0
        self.puzzle_completati = 0
        self.puzzle_corrente = None
        self.puzzles = self.crea_puzzles()
        self.risposta_selezionata = None
        self.mostra_spiegazione = False
        self.timer_prossima = 0
        self.game_state = "menu"  # menu, gioco, risultato
        self.mouse_pos = (0, 0)
        
        # Controllo musica
        self.musica_attiva = True
        
    def crea_puzzles(self) -> List[Puzzle]:
        """Crea una collezione di puzzle di ragionamento logico"""
        return [
            # Sequenze numeriche
            Puzzle(
                "Completa la sequenza: 2, 4, 8, 16, ?",
                ["24", "30", "32", "64"],
                2,
                "Ogni numero è il doppio del precedente: 2×2=4, 4×2=8, 8×2=16, 16×2=32"
            ),
            Puzzle(
                "Completa la sequenza: 3, 6, 9, 12, ?",
                ["14", "15", "16", "18"],
                1,
                "Si aggiunge 3 ogni volta: 3+3=6, 6+3=9, 9+3=12, 12+3=15"
            ),
            Puzzle(
                "Completa la sequenza: 100, 90, 80, 70, ?",
                ["65", "60", "55", "50"],
                1,
                "Si sottrae 10 ogni volta: 100-10=90, 90-10=80, 80-10=70, 70-10=60"
            ),
            
            # Logica deduttiva
            Puzzle(
                "Marco è più alto di Luca. Luca è più alto di Anna. Chi è il più basso?",
                ["Marco", "Luca", "Anna", "Impossibile dirlo"],
                2,
                "Se Marco > Luca e Luca > Anna, allora Anna è la più bassa."
            ),
            Puzzle(
                "Tutti i gatti hanno 4 zampe. Fuffi è un gatto. Quante zampe ha Fuffi?",
                ["2", "3", "4", "Dipende"],
                2,
                "Se tutti i gatti hanno 4 zampe e Fuffi è un gatto, allora Fuffi ha 4 zampe."
            ),
            Puzzle(
                "Tutti i pesci vivono in acqua. Il salmone è un pesce. Dove vive il salmone?",
                ["Sulla terra", "In acqua", "Sugli alberi", "Nel deserto"],
                1,
                "Se tutti i pesci vivono in acqua e il salmone è un pesce, allora il salmone vive in acqua."
            ),
            
            # Categorizzazione
            Puzzle(
                "Quale parola NON appartiene al gruppo? Mela, Banana, Carota, Arancia",
                ["Mela", "Banana", "Carota", "Arancia"],
                2,
                "Carota è una verdura, mentre gli altri sono frutti."
            ),
            Puzzle(
                "Quale numero NON appartiene al gruppo? 2, 4, 6, 9, 8",
                ["2", "4", "9", "8"],
                2,
                "Il 9 è dispari, mentre tutti gli altri sono numeri pari."
            ),
            
            # Problemi logici
            Puzzle(
                "Ho 5 mele. Ne regalo 2 a Maria e 1 a Paolo. Quante me ne rimangono?",
                ["1", "2", "3", "4"],
                1,
                "5 - 2 - 1 = 2 mele rimaste."
            ),
            Puzzle(
                "Un treno parte alle 14:30 e arriva alle 16:00. Quanto dura il viaggio?",
                ["1 ora", "1 ora e 30 minuti", "2 ore", "2 ore e 30 minuti"],
                1,
                "Dalle 14:30 alle 16:00 passano 1 ora e 30 minuti."
            ),
            
            # Analogie
            Puzzle(
                "Caldo sta a Freddo come Alto sta a ?",
                ["Grande", "Basso", "Lungo", "Forte"],
                1,
                "Caldo e Freddo sono opposti, come Alto e Basso."
            ),
            Puzzle(
                "Dottore sta a Ospedale come Insegnante sta a ?",
                ["Casa", "Scuola", "Ufficio", "Negozio"],
                1,
                "Il dottore lavora in ospedale, l'insegnante lavora a scuola."
            ),
            
            # Pattern e relazioni
            Puzzle(
                "Se A=1, B=2, C=3, quanto vale la parola 'CAB'?",
                ["4", "5", "6", "7"],
                2,
                "C=3, A=1, B=2. Quindi 3+1+2=6"
            ),
            Puzzle(
                "Qual è il prossimo giorno dopo Lunedì, Mercoledì, Venerdì?",
                ["Sabato", "Domenica", "Giovedì", "Martedì"],
                1,
                "Il pattern salta un giorno ogni volta: Lun→Mer→Ven→Dom"
            ),
        ]
    
    def prossimo_puzzle(self):
        """Carica il prossimo puzzle"""
        if not self.puzzles:
            self.game_state = "risultato"
            return
        
        self.puzzle_corrente = random.choice(self.puzzles)
        self.puzzles.remove(self.puzzle_corrente)
        self.risposta_selezionata = None
        self.mostra_spiegazione = False
        self.timer_prossima = 0
        self.game_state = "gioco"
    
    def verifica_risposta(self, indice):
        """Verifica la risposta selezionata"""
        self.risposta_selezionata = indice
        self.puzzle_completati += 1
        
        if indice == self.puzzle_corrente.risposta_corretta:
            self.punteggio += 10
            # Passa automaticamente dopo 800ms
            self.timer_prossima = pygame.time.get_ticks() + 800
            self.mostra_spiegazione = False
        else:
            # Mostra spiegazione per 3 secondi
            self.mostra_spiegazione = True
            self.timer_prossima = pygame.time.get_ticks() + 3000
    
    def toggle_musica(self):
        """Attiva/disattiva la musica di sottofondo (tasto M)"""
        try:
            if self.musica_attiva:
                pygame.mixer.music.pause()
                self.musica_attiva = False
                print("🔇 Musica in pausa")
            else:
                pygame.mixer.music.unpause()
                self.musica_attiva = True
                print("🔊 Musica ripresa")
        except:
            print("⚠ Nessuna musica caricata")
    
    def cambia_volume(self, delta):
        """Cambia il volume della musica (tasti + e -)"""
        try:
            volume_attuale = pygame.mixer.music.get_volume()
            nuovo_volume = max(0.0, min(1.0, volume_attuale + delta))
            pygame.mixer.music.set_volume(nuovo_volume)
            percentuale = int(nuovo_volume * 100)
            
            # Icona volume basata sul livello
            if nuovo_volume == 0:
                icona = "🔇"
            elif nuovo_volume < 0.3:
                icona = "🔉"
            else:
                icona = "🔊"
            
            print(f"{icona} Volume: {percentuale}%")
        except:
            print("⚠ Nessuna musica caricata")
    
    def draw_menu(self):
        """Disegna il menu iniziale"""
        draw_gradient(screen, LIGHT_BLUE, DARKER_BLUE)
        
        # Titolo
        title = font_titolo.render("🧠 Gioco di Ragionamento Logico", True, DARK_TEXT)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        
        # Pannello istruzioni
        panel_width = 900
        panel_height = 500
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 230))
        screen.blit(panel, (WIDTH // 2 - panel_width // 2, HEIGHT // 2 - panel_height // 2 - 50))
        
        # Istruzioni
        instructions = [
            "Benvenuto al Gioco di Ragionamento!",
            "",
            "• Leggi attentamente ogni domanda",
            "• Clicca sulla risposta che ritieni corretta",
            "• Se rispondi bene, passi subito alla prossima domanda",
            "• Se sbagli, vedrai la spiegazione prima di continuare",
            "",
            f"Totale puzzle: {len(self.crea_puzzles())}",
            "",
            "Clicca per iniziare!"
        ]
        
        y_offset = HEIGHT // 2 - panel_height // 2 - 20
        for i, line in enumerate(instructions):
            if line == "Benvenuto al Gioco di Ragionamento!":
                text = font_domanda.render(line, True, BLUE)
            else:
                text = font_punteggio.render(line, True, DARK_TEXT)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset + i * 45))
        
        # Info controlli
        controls = small_font.render("M=Musica | +=Volume+ | -=Volume- | ESC=Esci", True, DARK_TEXT)
        screen.blit(controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT - 50))
    
    def draw_gioco(self):
        """Disegna la schermata di gioco"""
        draw_gradient(screen, LIGHT_BLUE, DARKER_BLUE)
        
        # HUD Punteggio
        hud = pygame.Surface((300, 120), pygame.SRCALPHA)
        hud.fill((255, 255, 255, 200))
        screen.blit(hud, (20, 20))
        
        score_text = font_punteggio.render(f"Punteggio: {self.punteggio}", True, GREEN)
        screen.blit(score_text, (40, 40))
        
        count_text = font_punteggio.render(f"Completati: {self.puzzle_completati}", True, DARK_TEXT)
        screen.blit(count_text, (40, 80))
        
        # Indicatore musica nell'angolo
        music_icon = "🔊" if self.musica_attiva else "🔇"
        music_text = small_font.render(f"{music_icon} M", True, DARK_TEXT)
        screen.blit(music_text, (WIDTH - 80, 20))
        
        # Pannello domanda
        panel_width = min(1200, WIDTH - 100)
        panel_y = 180
        
        # Domanda
        domanda_lines = wrap_text(self.puzzle_corrente.domanda, font_domanda, panel_width - 80)
        domanda_height = len(domanda_lines) * 50 + 60
        
        domanda_panel = pygame.Surface((panel_width, domanda_height), pygame.SRCALPHA)
        domanda_panel.fill((255, 255, 255, 240))
        screen.blit(domanda_panel, (WIDTH // 2 - panel_width // 2, panel_y))
        
        y_text = panel_y + 30
        for line in domanda_lines:
            text = font_domanda.render(line, True, DARK_TEXT)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_text))
            y_text += 50
        
        # Opzioni
        opzioni_y = panel_y + domanda_height + 40
        button_width = 600
        button_height = 70
        spacing = 20
        
        for i, opzione in enumerate(self.puzzle_corrente.opzioni):
            button_x = WIDTH // 2 - button_width // 2
            button_y = opzioni_y + i * (button_height + spacing)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Determina colore
            if self.risposta_selezionata is not None:
                if i == self.puzzle_corrente.risposta_corretta:
                    color = GREEN
                elif i == self.risposta_selezionata and i != self.puzzle_corrente.risposta_corretta:
                    color = RED
                else:
                    color = (150, 150, 150)
            else:
                color = BLUE
                # Hover effect
                if button_rect.collidepoint(self.mouse_pos):
                    color = (100, 140, 255)
            
            draw_button(screen, opzione, button_rect, color, 
                       button_rect.collidepoint(self.mouse_pos) and self.risposta_selezionata is None)
        
        # Spiegazione se sbagliato
        if self.mostra_spiegazione:
            spieg_y = opzioni_y + 4 * (button_height + spacing) + 30
            spieg_panel = pygame.Surface((panel_width, 150), pygame.SRCALPHA)
            spieg_panel.fill((255, 200, 200, 230))
            screen.blit(spieg_panel, (WIDTH // 2 - panel_width // 2, spieg_y))
            
            wrong_text = font_opzioni.render("✗ Risposta Sbagliata", True, RED)
            screen.blit(wrong_text, (WIDTH // 2 - wrong_text.get_width() // 2, spieg_y + 20))
            
            spieg_lines = wrap_text(self.puzzle_corrente.spiegazione, font_spiegazione, panel_width - 80)
            y_spieg = spieg_y + 70
            for line in spieg_lines:
                text = font_spiegazione.render(line, True, DARK_TEXT)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_spieg))
                y_spieg += 35
    
    def draw_risultato(self):
        """Disegna la schermata finale"""
        draw_gradient(screen, (240, 255, 240), (200, 255, 200))
        
        # Pannello risultato
        panel_width = 700
        panel_height = 450
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (255, 255, 255, 240), (0, 0, panel_width, panel_height), border_radius=25)
        pygame.draw.rect(panel, GREEN, (0, 0, panel_width, panel_height), 5, border_radius=25)
        screen.blit(panel, (WIDTH // 2 - panel_width // 2, HEIGHT // 2 - panel_height // 2))
        
        # Icona successo
        success_font = pygame.font.SysFont("Segoe UI", 100, bold=True)
        checkmark = success_font.render("✓", True, GREEN)
        screen.blit(checkmark, (WIDTH // 2 - checkmark.get_width() // 2, HEIGHT // 2 - 180))
        
        # Titolo
        title_font = pygame.font.SysFont("Segoe UI", 60, bold=True)
        title = title_font.render("COMPLIMENTI!", True, GREEN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))
        
        # Punteggio
        score_font = pygame.font.SysFont("Segoe UI", 80, bold=True)
        score_text = score_font.render(f"{self.punteggio}", True, (50, 150, 80))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 30))
        
        points_label = font_punteggio.render("PUNTI", True, (100, 100, 100))
        screen.blit(points_label, (WIDTH // 2 - points_label.get_width() // 2, HEIGHT // 2 + 120))
        
        # Info completamento
        completed_text = font_opzioni.render(f"Puzzle completati: {self.puzzle_completati}", True, DARK_TEXT)
        screen.blit(completed_text, (WIDTH // 2 - completed_text.get_width() // 2, HEIGHT // 2 + 170))
        
        # Istruzioni
        esc_info = small_font.render("Premi ESC per chiudere", True, DARK_TEXT)
        screen.blit(esc_info, (WIDTH // 2 - esc_info.get_width() // 2, HEIGHT - 80))
    
    def update(self):
        """Aggiorna lo stato del gioco"""
        if self.game_state == "gioco" and self.risposta_selezionata is not None:
            if pygame.time.get_ticks() >= self.timer_prossima:
                self.prossimo_puzzle()
    
    def handle_click(self, pos):
        """Gestisce i click del mouse"""
        if self.game_state == "menu":
            self.prossimo_puzzle()
        
        elif self.game_state == "gioco" and self.risposta_selezionata is None:
            # Controlla click sui bottoni delle opzioni
            panel_width = min(1200, WIDTH - 100)
            domanda_lines = wrap_text(self.puzzle_corrente.domanda, font_domanda, panel_width - 80)
            domanda_height = len(domanda_lines) * 50 + 60
            
            opzioni_y = 180 + domanda_height + 40
            button_width = 600
            button_height = 70
            spacing = 20
            
            for i in range(len(self.puzzle_corrente.opzioni)):
                button_x = WIDTH // 2 - button_width // 2
                button_y = opzioni_y + i * (button_height + spacing)
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                
                if button_rect.collidepoint(pos):
                    self.verifica_risposta(i)
                    break

# -------------------------------
# Main
# -------------------------------
def main():
    gioco = GiocoRagionamento()
    running = True
    
    print("\n" + "=" * 60)
    print("GIOCO AVVIATO!")
    print("=" * 60)
    
    while running:
        gioco.mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                # ESC = Esci
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # M = Toggle musica
                elif event.key == pygame.K_m:
                    gioco.toggle_musica()
                
                # + o = = Aumenta volume
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    gioco.cambia_volume(0.1)
                
                # - = Diminuisci volume
                elif event.key == pygame.K_MINUS:
                    gioco.cambia_volume(-0.1)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                gioco.handle_click(event.pos)
        
        # Update
        gioco.update()
        
        # Draw
        if gioco.game_state == "menu":
            gioco.draw_menu()
        elif gioco.game_state == "gioco":
            gioco.draw_gioco()
        elif gioco.game_state == "risultato":
            gioco.draw_risultato()
        
        pygame.display.flip()
        clock.tick(30)
    
    # Chiusura
    pygame.mixer.music.stop()
    pygame.quit()
    print("\nGioco chiuso. Grazie per aver giocato! 🎮")

if __name__ == "__main__":
    main()