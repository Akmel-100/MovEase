"""
Gioco di Ragionamento Logico
Progettato per persone con Sclerosi Multipla

Caratteristiche:
- Interfaccia semplice e chiara
- Velocità personalizzabile
- Focus sul ragionamento, non sulla velocità o precisione fisica
- Feedback positivo e incoraggiante
"""

import tkinter as tk
from tkinter import messagebox, font
import random
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Puzzle:
    """Rappresenta un puzzle logico"""
    domanda: str
    opzioni: List[str]
    risposta_corretta: int
    spiegazione: str

class GiocoRagionamento:
    def __init__(self, root):
        self.root = root
        self.root.title("Gioco di Ragionamento Logico")
        self.root.geometry("800x600")
        self.root.configure(bg="#E8F4F8")
        
        # Configurazione
        self.punteggio = 0
        self.puzzle_completati = 0
        self.puzzle_corrente = None
        
        # Font grandi e leggibili
        self.font_titolo = font.Font(family="Arial", size=18, weight="bold")
        self.font_testo = font.Font(family="Arial", size=14)
        self.font_bottone = font.Font(family="Arial", size=13)
        
        # Puzzles di ragionamento logico
        self.puzzles = self.crea_puzzles()
        
        self.crea_interfaccia()
    
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
                "Se piove, porto l'ombrello. Oggi porto l'ombrello. Quindi:",
                ["Piove sicuramente", "Potrebbe piovere", "Non piove", "È nevicato"],
                1,
                "Portare l'ombrello non significa necessariamente che piova - potrei portarlo per precauzione."
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
    
    def crea_interfaccia(self):
        """Crea l'interfaccia grafica principale"""
        # Frame principale
        self.frame_principale = tk.Frame(self.root, bg="#E8F4F8")
        self.frame_principale.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Titolo
        self.label_titolo = tk.Label(
            self.frame_principale,
            text="🧠 Gioco di Ragionamento Logico",
            font=self.font_titolo,
            bg="#E8F4F8",
            fg="#2C3E50"
        )
        self.label_titolo.pack(pady=(0, 20))
        
        # Punteggio
        self.label_punteggio = tk.Label(
            self.frame_principale,
            text="Punteggio: 0 | Completati: 0",
            font=self.font_testo,
            bg="#E8F4F8",
            fg="#34495E"
        )
        self.label_punteggio.pack(pady=(0, 30))
        
        # Frame per la domanda
        self.frame_domanda = tk.Frame(self.frame_principale, bg="#FFFFFF", relief="raised", bd=2)
        self.frame_domanda.pack(fill="both", expand=True, pady=(0, 20))
        
        self.label_domanda = tk.Label(
            self.frame_domanda,
            text="",
            font=self.font_testo,
            bg="#FFFFFF",
            fg="#2C3E50",
            wraplength=700,
            justify="center",
            pady=30
        )
        self.label_domanda.pack()
        
        # Frame per i bottoni delle opzioni
        self.frame_opzioni = tk.Frame(self.frame_principale, bg="#E8F4F8")
        self.frame_opzioni.pack(pady=(0, 20))
        
        self.bottoni_opzioni = []
        for i in range(4):
            btn = tk.Button(
                self.frame_opzioni,
                text="",
                font=self.font_bottone,
                bg="#3498DB",
                fg="white",
                activebackground="#2980B9",
                width=30,
                height=2,
                cursor="hand2",
                command=lambda idx=i: self.verifica_risposta(idx)
            )
            btn.pack(pady=8)
            self.bottoni_opzioni.append(btn)
        
        # Bottone per iniziare/prossimo
        self.bottone_azione = tk.Button(
            self.frame_principale,
            text="Inizia Gioco",
            font=self.font_bottone,
            bg="#27AE60",
            fg="white",
            activebackground="#229954",
            width=20,
            height=2,
            cursor="hand2",
            command=self.prossimo_puzzle
        )
        self.bottone_azione.pack(pady=10)
        
        # Nascondi opzioni all'inizio
        self.frame_opzioni.pack_forget()
    
    def prossimo_puzzle(self):
        """Carica il prossimo puzzle"""
        if not self.puzzles:
            messagebox.showinfo(
                "Complimenti!",
                f"Hai completato tutti i puzzle!\n\n"
                f"Punteggio finale: {self.punteggio}\n"
                f"Puzzle completati: {self.puzzle_completati}"
            )
            self.resetta_gioco()
            return
        
        # Seleziona puzzle casuale
        self.puzzle_corrente = random.choice(self.puzzles)
        self.puzzles.remove(self.puzzle_corrente)
        
        # Mostra domanda
        self.label_domanda.config(text=self.puzzle_corrente.domanda)
        
        # Mostra opzioni
        for i, (btn, opzione) in enumerate(zip(self.bottoni_opzioni, self.puzzle_corrente.opzioni)):
            btn.config(
                text=opzione,
                bg="#3498DB",
                state="normal"
            )
        
        # Mostra frame opzioni e nascondi bottone azione
        self.frame_opzioni.pack(pady=(0, 20))
        self.bottone_azione.pack_forget()
    
    def verifica_risposta(self, indice_selezionato):
        """Verifica se la risposta è corretta"""
        # Disabilita tutti i bottoni
        for btn in self.bottoni_opzioni:
            btn.config(state="disabled")
        
        # Colora la risposta corretta e quella selezionata
        self.bottoni_opzioni[self.puzzle_corrente.risposta_corretta].config(bg="#27AE60")
        
        if indice_selezionato == self.puzzle_corrente.risposta_corretta:
            self.bottoni_opzioni[indice_selezionato].config(bg="#27AE60")
            self.punteggio += 10
            messaggio = "✓ Corretto! " + self.puzzle_corrente.spiegazione
            colore = "#27AE60"
        else:
            self.bottoni_opzioni[indice_selezionato].config(bg="#E74C3C")
            messaggio = "✗ Sbagliato. " + self.puzzle_corrente.spiegazione
            colore = "#E74C3C"
        
        self.puzzle_completati += 1
        
        # Aggiorna punteggio
        self.label_punteggio.config(
            text=f"Punteggio: {self.punteggio} | Completati: {self.puzzle_completati}"
        )
        
        # Mostra spiegazione
        self.label_domanda.config(text=messaggio, fg=colore)
        
        # Mostra bottone per continuare
        self.bottone_azione.config(text="Prossima Domanda")
        self.bottone_azione.pack(pady=10)
    
    def resetta_gioco(self):
        """Resetta il gioco"""
        self.punteggio = 0
        self.puzzle_completati = 0
        self.puzzles = self.crea_puzzles()
        
        self.label_punteggio.config(text="Punteggio: 0 | Completati: 0")
        self.label_domanda.config(text="", fg="#2C3E50")
        
        self.frame_opzioni.pack_forget()
        self.bottone_azione.config(text="Inizia Nuovo Gioco")
        self.bottone_azione.pack(pady=10)

def main():
    root = tk.Tk()
    app = GiocoRagionamento(root)
    root.mainloop()

if __name__ == "__main__":
    main()