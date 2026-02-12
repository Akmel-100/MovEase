import pygame
import random
import time
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gioco Riabilitativo - Sclerosi Multipla")

font = pygame.font.SysFont("Segoe UI", 26)
large_font = pygame.font.SysFont("Segoe UI", 64, bold=True)

clock = pygame.time.Clock()

# -------------------------------
# CARICA IMMAGINE BERSAGLIO
# -------------------------------
target_image_original = pygame.image.load("bersaglio.png").convert_alpha()

# -------------------------------
# COLORI
# -------------------------------
WHITE = (255, 255, 255)
RED = (255, 80, 80)
GREEN = (80, 200, 120)
DARK_TEXT = (40, 40, 40)

# -------------------------------
# SFONDO GRADIENTE
# -------------------------------
def draw_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

# -------------------------------
# VARIABILI DI GIOCO
# -------------------------------
score = 0
misses = 0
radius = 40
game_duration = 30

target_x = random.randint(radius, WIDTH - radius)
target_y = random.randint(radius, HEIGHT - radius)

flash_timer = 0
hit_effect_timer = 0

running = True
game_over = False

# -------------------------------
# ISTRUZIONI
# -------------------------------
show_instructions = True

while show_instructions:
    draw_gradient(screen, (240, 245, 255), (200, 220, 255))

    title = large_font.render("Istruzioni", True, (80, 140, 255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))

    instructions = [
        "Clicca l'immagine il più velocemente possibile.",
        "Ogni centro aumenta il punteggio.",
        "Se sbagli clic aumenta il numero di errori.",
        "L'immagine diventa più piccola col tempo.",
        "",
        "Durata: 30 secondi.",
        "",
        "Premi un tasto per iniziare."
    ]

    for i, line in enumerate(instructions):
        text = font.render(line, True, DARK_TEXT)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 180 + i * 35))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            show_instructions = False

# -------------------------------
# COUNTDOWN
# -------------------------------
for i in range(3, 0, -1):
    draw_gradient(screen, (240, 245, 255), (200, 220, 255))
    txt = large_font.render(str(i), True, RED)
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2,
                      HEIGHT//2 - txt.get_height()//2))
    pygame.display.flip()
    pygame.time.delay(1000)

start_time = time.time()

# -------------------------------
# CICLO PRINCIPALE
# -------------------------------
while running:
    draw_gradient(screen, (240, 245, 255), (200, 220, 255))

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
                hit_effect_timer = 8
                if radius > 20:
                    radius -= 1
            else:
                misses += 1
                flash_timer = 8

            target_x = random.randint(radius, WIDTH - radius)
            target_y = random.randint(radius, HEIGHT - radius)

    if remaining_time == 0 and not game_over:
        game_over = True

    if not game_over:

        # Animazione pulse
        pulse = 4 * math.sin(pygame.time.get_ticks() * 0.005)
        animated_radius = int(radius + pulse)

        # Ridimensiona immagine dinamicamente
        target_size = animated_radius * 2
        target_image = pygame.transform.smoothscale(
            target_image_original,
            (target_size, target_size)
        )

        rect = target_image.get_rect(center=(target_x, target_y))
        screen.blit(target_image, rect)

        # Effetto colpo riuscito
        if hit_effect_timer > 0:
            pygame.draw.circle(screen, GREEN,
                               (target_x, target_y),
                               animated_radius + 15, 4)
            hit_effect_timer -= 1

        # ---------------- HUD ----------------
        hud = pygame.Surface((240, 140), pygame.SRCALPHA)
        hud.fill((255, 255, 255, 190))
        screen.blit(hud, (15, 15))

        score_text = font.render(f"Punteggio: {score}", True, DARK_TEXT)
        miss_text = font.render(f"Errori: {misses}", True, DARK_TEXT)
        time_text = font.render(f"Tempo: {remaining_time}", True, DARK_TEXT)

        screen.blit(score_text, (30, 30))
        screen.blit(miss_text, (30, 65))
        screen.blit(time_text, (30, 100))

        # Barra tempo
        bar_width = 200
        progress = remaining_time / game_duration
        pygame.draw.rect(screen, (220, 220, 220),
                         (30, 135, bar_width, 10))
        pygame.draw.rect(screen, (80, 200, 120),
                         (30, 135, bar_width * progress, 10))

        # Flash errore
        if flash_timer > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(70)
            overlay.fill(RED)
            screen.blit(overlay, (0, 0))
            flash_timer -= 1

    else:
        draw_gradient(screen, (230, 240, 255), (200, 220, 255))

        panel = pygame.Surface((500, 300), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 220))
        screen.blit(panel, (WIDTH//2 - 250, HEIGHT//2 - 150))

        total_clicks = score + misses
        accuracy = int((score / total_clicks) * 100) if total_clicks > 0 else 0

        title = large_font.render("Stop", True, RED)
        score_text = font.render(f"Punteggio totale: {score}", True, DARK_TEXT)
        miss_text = font.render(f"Errori totali: {misses}", True, DARK_TEXT)
        acc_text = font.render(f"Precisione: {accuracy}%", True, DARK_TEXT)

        screen.blit(title, (WIDTH//2 - title.get_width()//2,
                            HEIGHT//2 - 120))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2,
                                 HEIGHT//2 - 20))
        screen.blit(miss_text, (WIDTH//2 - miss_text.get_width()//2,
                                HEIGHT//2 + 20))
        screen.blit(acc_text, (WIDTH//2 - acc_text.get_width()//2,
                               HEIGHT//2 + 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
