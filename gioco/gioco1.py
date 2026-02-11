import pygame
import random
import time
import math

# Inizializzazione
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gioco Riabilitativo - Sclerosi Multipla")

font = pygame.font.SysFont("Arial", 30)
large_font = pygame.font.SysFont("Arial", 60)

# Colori
WHITE = (255, 255, 255)
BLUE = (100, 150, 255)
GREEN = (100, 255, 150)
RED = (255, 100, 100)
GRAY = (230, 230, 230)

clock = pygame.time.Clock()

# Variabili di gioco
score = 0
misses = 0
radius = 40
spawn_time = 1500  # millisecondi
game_duration = 60  # secondi

target_x = random.randint(radius, WIDTH - radius)
target_y = random.randint(radius, HEIGHT - radius)

running = True
game_over = False

# -------------------------------
# CONTO ALLA ROVESCIA INIZIALE
# -------------------------------
countdown = 3
for i in range(countdown, 0, -1):
    screen.fill(GRAY)
    countdown_text = large_font.render(str(i), True, RED)
    screen.blit(countdown_text, (WIDTH//2 - countdown_text.get_width()//2, HEIGHT//2 - countdown_text.get_height()//2))
    pygame.display.flip()
    time.sleep(1)  # 1 secondo per ogni numero

screen.fill(GRAY)
go_text = large_font.render("Via!", True, GREEN)
screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - go_text.get_height()//2))
pygame.display.flip()
time.sleep(1)

start_time = time.time()  # avvio timer gioco

# -------------------------------
# CICLO PRINCIPALE
# -------------------------------
while running:
    screen.fill(GRAY)

    current_time = time.time()
    elapsed_time = current_time - start_time
    remaining_time = max(0, int(game_duration - elapsed_time))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            distance = math.hypot(mouse_x - target_x, mouse_y - target_y)

            if distance <= radius:
                score += 1
                if spawn_time > 600:
                    spawn_time -= 50
                if radius > 20:
                    radius -= 1
            else:
                misses += 1

            target_x = random.randint(radius, WIDTH - radius)
            target_y = random.randint(radius, HEIGHT - radius)

    if remaining_time == 0 and not game_over:
        game_over = True

    if not game_over:
        # Disegno bersaglio
        pygame.draw.circle(screen, BLUE, (target_x, target_y), radius)

        # Testi
        score_text = font.render(f"Punteggio: {score}", True, (0, 0, 0))
        miss_text = font.render(f"Errori: {misses}", True, (0, 0, 0))
        time_text = font.render(f"Tempo: {remaining_time}", True, (0, 0, 0))

        screen.blit(score_text, (20, 20))
        screen.blit(miss_text, (20, 60))
        screen.blit(time_text, (20, 100))
    else:
        # Schermata fine gioco
        screen.fill(GRAY)
        game_over_text = large_font.render("Fine della sessione", True, RED)
        score_text = font.render(f"Punteggio totale: {score}", True, (0, 0, 0))
        miss_text = font.render(f"Totale errori: {misses}", True, (0, 0, 0))

        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(miss_text, (WIDTH//2 - miss_text.get_width()//2, HEIGHT//2 + 50))

    pygame.display.flip()
    clock.tick(60)

# Attendi 5 secondi sulla schermata finale prima di chiudere
time.sleep(1)
pygame.quit()
