1. Introduzione al progetto

L’idea iniziale di questo progetto nasce con l’obiettivo di realizzare un sistema di telepresenza per il nostro istituto tecnico, pensato specificamente per persone affette da sclerosi multipla.

La sclerosi multipla è una patologia che può causare:

difficoltà motorie

ridotta coordinazione

affaticamento

impossibilità a muoversi autonomamente

Per questo motivo il progetto è stato sviluppato per consentire a una persona affetta da sclerosi multipla di muoversi e osservare un ambiente reale a distanza, senza dover compiere spostamenti fisici.

2. Obiettivo della telepresenza

L’obiettivo principale del sistema di telepresenza è permettere all’utente di:

essere “presente” all’interno dell’istituto

esplorare ambienti reali tramite un robot

interagire in modo semplice e intuitivo

Il controllo del sistema è stato progettato per essere:

accessibile

poco faticoso

basato su movimenti naturali come:

gesti delle mani

movimenti della testa

3. Tecnologie utilizzate
3.1 Linguaggio di programmazione

Il progetto è stato sviluppato utilizzando il linguaggio di programmazione Python, scelto per:

la sua semplicità sintattica

l’ampia disponibilità di librerie

il largo utilizzo in ambito di robotica e visione artificiale

3.2 Robot AlphaBot

Per la realizzazione della telepresenza è stato utilizzato un robot AlphaBot, dotato di:

motori per il movimento

interfaccia di controllo via codice

telecamera collegata al sistema

Il robot permette di:

muoversi nello spazio reale

trasmettere immagini in tempo reale

eseguire comandi ricevuti dal programma Python

4. Codici e librerie di base

Per lo sviluppo del progetto:

sono stati utilizzati codici già esistenti, forniti da studenti di quinta dell’anno precedente

sono state scaricate e installate tutte le librerie presenti nella wiki ufficiale dell’AlphaBot

Questo ha permesso di:

partire da una base funzionante

ridurre il tempo di sviluppo

concentrarsi sull’interazione uomo–macchina

5. Controllo tramite gesti

Il controllo dell’AlphaBot e del gioco avviene tramite una telecamera, che rileva:

i movimenti delle mani

i gesti dell’utente

eventuali movimenti della testa

Questa modalità di controllo è particolarmente adatta a persone affette da sclerosi multipla, poiché:

non richiede l’uso di tastiera o joystick

riduce lo sforzo fisico

sfrutta movimenti naturali e intuitivi

6. Descrizione del gioco interattivo

Oltre al sistema di telepresenza è stato sviluppato un gioco interattivo, utilizzato sia come dimostrazione tecnica sia come attività ludica.

6.1 Obiettivo del gioco

Lo scopo del gioco è raccogliere delle palline che appaiono sullo schermo utilizzando esclusivamente i movimenti delle mani.

Non vengono utilizzati:

mouse

tastiera

controller tradizionali

6.2 Riconoscimento delle mani

Il sistema è in grado di distinguere:

mano destra, evidenziata in rosso

mano sinistra, evidenziata in blu

Sul display:

se appare una pallina rossa → deve essere presa con la mano destra

se appare una pallina blu → deve essere presa con la mano sinistra

Per prendere una pallina:

l’utente deve chiudere la mano sopra di essa

7. Librerie necessarie al funzionamento

Per il corretto funzionamento del progetto è necessario installare alcune librerie Python specifiche.

8. Installazione dell’ambiente di sviluppo
8.1 Installazione di Python

Scaricare Python dal sito ufficiale:
https://www.python.org

Durante l’installazione:

selezionare l’opzione “Add Python to PATH”

procedere con l’installazione standard

Verificare l’installazione aprendo il Prompt dei comandi e digitando:

python --version

Se viene visualizzata la versione di Python, l’installazione è corretta.

9. Installazione delle librerie tramite pip

Le librerie vengono installate utilizzando pip, il gestore di pacchetti di Python.

9.1 Installazione di MediaPipe

Il progetto richiede obbligatoriamente la versione 0.10.30 di MediaPipe, poiché altre versioni potrebbero non essere compatibili.

Comando da eseguire:

pip install mediapipe==0.10.30

MediaPipe viene utilizzata per:

il riconoscimento delle mani

il tracciamento dei movimenti

l’interpretazione dei gesti tramite telecamera

9.2 Installazione di Pygame

Pygame è la libreria utilizzata per la parte grafica del gioco.

Comando da eseguire:

pip install pygame

Pygame permette di:

creare la finestra di gioco

visualizzare palline e colori

gestire la grafica in tempo reale

9.3 Librerie dell’AlphaBot

Per l’AlphaBot è necessario:

scaricare le librerie dalla wiki ufficiale

copiare i file all’interno della cartella del progetto

verificare che siano correttamente importabili nel codice Python

Esempio di importazione:

import AlphaBot
10. Verifica del funzionamento

Dopo l’installazione delle librerie:

Collegare la telecamera

Avviare il programma Python

Controllare che:

la telecamera venga rilevata

le mani siano riconosciute

i colori rosso e blu siano visibili

il robot risponda ai comandi

11. Problemi comuni

Errore su MediaPipe
→ verificare che la versione installata sia la 0.10.30

ModuleNotFoundError
→ la libreria non è installata correttamente

Telecamera non rilevata
→ controllare connessione e permessi

12. Conclusione

Questo progetto dimostra come la tecnologia possa essere utilizzata per:

migliorare l’accessibilità

supportare persone affette da sclerosi multipla

creare sistemi di telepresenza inclusivi

Unendo robotica, programmazione Python e controllo tramite gesti, è stato realizzato un sistema funzionale, intuitivo e adatto a utenti con difficoltà motorie.
