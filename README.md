1. Obiettivo del progetto

Questo progetto ha come scopo la realizzazione di un sistema di telepresenza e di un gioco interattivo controllato tramite gesti, pensato per persone affette da sclerosi multipla — una condizione che può causare difficoltà motorie, riduzione della coordinazione e difficoltà negli spostamenti.

La telepresenza consente quindi a queste persone di “essere presenti” a distanza all’interno dell’istituto, muovendo un robot e osservando l’ambiente tramite video, senza necessità di spostarsi fisicamente.

2. Tecnologie e componenti principali
2.1 Linguaggio di programmazione

Il sistema è stato sviluppato in Python, un linguaggio di programmazione molto usato per robotica e visione artificiale grazie alla sua semplicità e alla disponibilità di molte librerie utili.

2.2 Robot AlphaBot

Il robot AlphaBot è una piattaforma mobile compatibile con:

Raspberry Pi

Arduino

Questo significa che può essere programmato e controllato tramite una board Raspberry Pi oppure una scheda Arduino, oppure entrambe in modalità integrata.

2.3 Funzionalità dell’AlphaBot

L’AlphaBot è progettato per essere facilmente estendibile con moduli aggiuntivi e offre:

Interfacce per Raspberry Pi e Arduino

Motori per movimento

Porta per sensori aggiuntivi (es. sensori di ostacolo o tracking)

Possibilità di controllo remoto via Wi-Fi, Bluetooth o Infrared

2.4 Moduli hardware integrati

La wiki ufficiale descrive le principali risorse hardware dell’AlphaBot:

Interfacce GPIO per Raspberry Pi/Arduino

Driver motori basato su chip L298P

Batteria e regolatore di tensione

Moduli per sensori (infrarossi, ultrasuoni, line tracking)

3. Descrizione del sistema di controllo e del gioco
3.1 Telepresenza tramite gesti

L’interazione tra l’utente e il robot avviene attraverso:

una telecamera collegata al sistema

il riconoscimento dei gesti delle mani tramite librerie software

Il robot si muove e interagisce in base ai movimenti riconosciuti, rendendo l’esperienza accessibile anche a chi non può utilizzare strumenti tradizionali come tastiere o joystick.

3.2 Gioco interattivo

Il gioco proposto nel progetto consiste nel raccogliere palline visualizzate a schermo:

La mano destra è evidenziata in rosso

La mano sinistra è evidenziata in blu

Il giocatore deve chiudere la mano sulla pallina corrispondente al colore

Questo sistema sfrutta tecniche di rilevamento delle mani e di gestione grafica con pygame, offrendo un’interazione naturale e intuitiva.

4. Ambiente di sviluppo e librerie richieste

Per far funzionare il progetto è necessario configurare l’ambiente Python e installare alcune librerie specifiche.

4.1 Installazione di Python

Scaricare Python da https://www.python.org

Durante l’installazione spuntare “Add Python to PATH”

Verificare l’installazione nel Prompt dei comandi con:

python --version

Se viene visualizzata la versione di Python, l’installazione è corretta.

4.2 Installazione delle librerie Python

Tutte le librerie possono essere installate tramite pip (strumento di gestione pacchetti di Python).

4.2.1 MediaPipe

MediaPipe è utilizzata per il riconoscimento delle mani e dei gesti. La versione richiesta è 0.10.30:

pip install mediapipe==0.10.30
4.2.2 Pygame

Pygame è la libreria grafica utilizzata per creare il gioco:

pip install pygame
4.2.3 Librerie per Raspberry Pi e AlphaBot

Se si utilizza Raspberry Pi come controller del robot, la documentazione ufficiale suggerisce di installare una serie di dipendenze di sistema che permettono di gestire:

GPIO (pin di input/output)

bus SPI / I2C per dispositivi esterni

comunicazioni seriali

Esempi di comandi da terminale (su Raspberry Pi):

sudo apt-get update
sudo apt-get install python-pip
sudo pip install RPi.GPIO
sudo pip install spidev
sudo apt-get install python-smbus
sudo apt-get install python-serial

⚠️ Su sistemi più recenti potrebbe essere necessario usare pip3 invece di pip se si utilizza Python3.

4.3 Download dei demo ufficiali AlphaBot

La wiki ufficiale fornisce anche esempi pronti all’uso. Per scaricarli, si possono utilizzare questi comandi nel terminale di Raspberry Pi:

sudo apt-get install p7zip
wget https://files.waveshare.com/upload/2/20/AlphaBot_Demo.7z
7zr x AlphaBot_Demo.7z -r -o./AlphaBot_Demo
sudo chmod 777 -R AlphaBot_Demo
cd AlphaBot_Demo/AlphaBot_Demo/RaspberryPi/AlphaBot/

Questi esempi consentono di testare direttamente funzioni come:

movimento dei motori

sensori di ostacolo

controllo infrarosso

controllo remoto via web

5. Configurazioni hardware aggiuntive (Raspberry Pi)

Se si utilizza Raspberry Pi, la wiki suggerisce di abilitare alcuni moduli di interfaccia tramite il tool raspi-config:

SPI interface

I2C interface

UART serial interface
Queste configurazioni permettono l’uso di periferiche esterne come moduli di comunicazione o sensori.

6. Verifica del sistema

Dopo l’installazione delle librerie e la configurazione, è consigliato eseguire una serie di test:

Avviare il programma Python

Controllare che la telecamera sia riconosciuta

Verificare che le mani vengano tracciate correttamente

Testare il movimento del robot (comandi base)

Eseguire il gioco grafico per controllare la raccolta delle palline

7. Possibili problemi comuni e soluzioni
7.1 Problema: MediaPipe non installata

– Assicurarsi di aver installato la versione 0.10.30.

7.2 Telecamera non rilevata

– Verificare permessi e connessione
– Controllare che non sia in uso da altri programmi

7.3 Errori su Raspberry Pi

– Alcune distribuzioni recenti non supportano librerie di sistema più vecchie
– In questi casi usare pip3 e verificare compatibilità delle dipendenze

8. Conclusione

Questo progetto combina robotica, visione artificiale e programmazione Python per creare un sistema utile e accessibile, in particolare per persone affette da sclerosi multipla. Il risultato è un ambiente sperimentale completo:

telepresenza robotica

gioco controllato tramite gesti

possibilità di espansione con sensori e moduli hardware
