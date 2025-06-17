import pygame
import math
import random

# Inicjalizacja
pygame.init()
background = pygame.image.load("img/czestochowa_02.png")#.convert()
motocykl_img_raw = pygame.image.load("img/player_templ.png")
motocykl_img_raw = pygame.transform.rotate(motocykl_img_raw, 0)
motocykl_img = scaled_img = pygame.transform.smoothscale(motocykl_img_raw, (25, 25))
WIDTH, HEIGHT = 1600, 1050
FPS = 120
#screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
trail_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA) #rysowanie śladów
fade_surface = pygame.Surface(trail_surface.get_size(), pygame.SRCALPHA)
fade_surface.fill((0, 0, 0, 10))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Console", 24)

start_delay = random.randint(3000, 10000)  # losowo 3–10 sek. w milisekundach
start_time = pygame.time.get_ticks()
tape_visible = True
green_light_time = None
green_light_visible = False

# Kolory
screen_colors = [
    ("Red", (255, 0, 0)),
    ("Blue", (0, 0, 255)),
    ("White", (255, 250, 250)),
    ("Yellow", (255, 215, 0)),
]
BG_COLOR = (30, 30, 30)
RED_BIKE_COLOR = 'RED_BIKE_COLOR', (255, 0, 0)
BLUE_BIKE_COLOR = 'BLUE_BIKE_COLOR', (0, 0, 255)
YELLOW_BIKE_COLOR = 'YELLOW_BIKE_COLOR', (255, 215, 0)
WHITE_BIKE_COLOR = 'WHITE_BIKE_COLOR', (255, 250, 250)

STEERING = {
    "RED_BIKE_COLOR": [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP],
    "BLUE_BIKE_COLOR": [pygame.K_a, pygame.K_d, pygame.K_w],
    "YELLOW_BIKE_COLOR": [pygame.K_j, pygame.K_l, pygame.K_i],
    "WHITE_BIKE_COLOR": [pygame.K_b, pygame.K_m, pygame.K_h]
}

# Parametry fizyczne
ACCELERATION = 0.22        # przyspieszenie
FRICTION = 0.979       # tarcie + opór
ROTATION_SPEED = 1.7         # kąt w stopniach na klatkę

# Klasa motocykla
class Motorcycle:


    def __init__(self, x, y, color=RED_BIKE_COLOR):
        self.pos = pygame.math.Vector2(x, y)          # Pozycja
        self.vel = pygame.math.Vector2(0, 0)          # Prędkość
        self.angle = 0    # Kąt (w stopniach)
        self.color = color[1]
        self.steering = STEERING[color[0]]
        self.trail = []
        self.reaction_time = None
        self.has_reacted = False
        self.false_start = False
        self.disqualified = False
        self.is_accelerating = False

    def handle_key_press(self, key, current_time, green_light_time):
        if self.reaction_time is None and key == self.steering[2]:
            if green_light_time is None or current_time < green_light_time:
                # Wciśnięto gaz PRZED zielonym światłem – falstart
                self.false_start = True
                self.disqualified = True
                print(f"Zawodnik {self.color} zdyskwalifikowany za falstart!")
                print("❌ FALSTART!")
            else:
                # Normalna reakcja po zielonym świetle
                self.reaction_time = current_time - green_light_time
                self.has_reacted = True



    def update(self, keys):
        # Obrót (lewo/prawo)
        if self.disqualified:
            return

        if keys[self.steering[0]]:
            self.angle += ROTATION_SPEED
        if keys[self.steering[1]]:
            self.angle -= ROTATION_SPEED

        # Przyspieszanie
        if keys[self.steering[2]]:
            direction = pygame.math.Vector2(1, 0).rotate(-self.angle)  # Kierunek jazdy
            self.vel += direction * ACCELERATION
            self.is_accelerating = True
        else:
            self.is_accelerating = False

        # Opór powietrza (zmniejsza prędkość)
        self.vel *= FRICTION

        # Aktualizacja pozycji
        self.pos += self.vel

        # Opcjonalnie: zawijanie ekranu
        if self.pos.x > WIDTH: self.pos.x = 0#WIDTH
        if self.pos.x < 0: self.pos.x = WIDTH#0
        if self.pos.y > HEIGHT: self.pos.y = 0#HEIGHT
        if self.pos.y < 0: self.pos.y = HEIGHT#0


    def draw(self, screen):

        if self.disqualified:
            return
        # Rysujemy motocykl jako trójkąt w kierunku jazdy
        direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
        perp = direction.rotate(90)

        p1 = self.pos + direction * 15
        p2 = self.pos - direction * 10 + perp * 8
        p3 = self.pos - direction * 10 - perp * 8

        #pygame.draw.polygon(screen, self.color, [p1, p2, p3])
        rotated_img = pygame.transform.rotate(motocykl_img, self.angle)
        rect = rotated_img.get_rect(center=[self.pos.x, self.pos.y])

        screen.blit(rotated_img, rect.topleft)

        if self.is_accelerating:
            pygame.draw.polygon(screen, (0, 0, 0), [p1, p2, p3], width=2)


moto = [Motorcycle(WIDTH // 2, HEIGHT // 2 + 30),
        Motorcycle(WIDTH // 2, HEIGHT // 2 + 55, BLUE_BIKE_COLOR),
        Motorcycle(WIDTH // 2, HEIGHT // 2 + 80, WHITE_BIKE_COLOR),
        Motorcycle(WIDTH // 2, HEIGHT // 2 + 105, YELLOW_BIKE_COLOR)
        ]

pixel_color = background.get_at((int(moto[1].pos.x), int(moto[1].pos.y))) # sprawdzenie nawierzchni
if pixel_color == (128, 53, 14, 255):  # np. żużel - sienna
    skid_color = (64, 27, 7) # black bean
elif pixel_color == (100, 70, 30, 255):  # np. żużel
    skid_color = (30, 20, 10)
else:
    skid_color = (0, 0, 0)

# Pętla gry
running = True
counter = 0
gas = 0
frame_counter = 60
while running:
    #screen.fill(BG_COLOR)
    current_time = pygame.time.get_ticks()
    if not green_light_visible and current_time - start_time >= start_delay:
        green_light_visible = True
        green_light_time = current_time
        tape_visible = False  # taśma znika
        print(f"green light time: {green_light_time}")

    # Wydarzenia
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            pressed_key = event.key
            if event.key == pygame.K_ESCAPE:
                running = False

            for m in moto:
                if pressed_key == m.steering[2]:  # [2] to przypisany klawisz przyspieszenia
                    m.handle_key_press(pressed_key, current_time=current_time, green_light_time=green_light_time if green_light_visible else None)

    frame_counter += 1
    if frame_counter % 30 == 0:
        for player in moto:
            player.trail.append(player.pos.copy())

    for player in moto:
        for p in player.trail:
            pygame.draw.ellipse(trail_surface, skid_color, (player.pos.x, player.pos.y, 4, 4))  # mały czarny kwadrat

    screen.blit(background, (0, 0))
    screen.blit(trail_surface, (0, 0))
    if counter % 60 == 0:
        trail_surface.blit(fade_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    #current_time = pygame.time.get_ticks()
    # Czy minął czas startu?
    #if tape_visible and current_time - start_time >= start_delay:
    #    tape_visible = False
    #    green_light_visible = True

    # Wyświetl taśmę startową (gruba biała linia)
    if tape_visible:
        pygame.draw.line(screen, (255, 255, 255), (700, 400), (700, 500), 10)

    # Zielone światło po starcie
    if green_light_visible:
        pygame.draw.circle(screen, (0, 255, 0), (500, 300), 20)
        # Oblicz czas od zapalenia zielonego światła
        elapsed_ms = pygame.time.get_ticks() - start_time - start_delay
        elapsed_sec = elapsed_ms / 1000.0

        # Zaokrągl do dwóch miejsc
        timer_text = font.render(f"{elapsed_sec:.1f} s", True, (255, 255, 255))

        # Wyśrodkuj na ekranie
        text_rect = timer_text.get_rect(center=(screen.get_width() // 2 - 100, screen.get_height() // 2 -100))

        # Narysuj na ekranie
        screen.blit(timer_text, text_rect)

    else:
        pygame.draw.circle(screen, (255, 0, 0), (500, 300), 20)

    keys = pygame.key.get_pressed()
    for player in moto:
        player.update(keys)
        player.draw(screen)

    for idx, (name, screen_color) in enumerate(screen_colors):
        speed = moto[idx].vel.length() * 8.5
        speed_text = f"{name}: {speed:.0f} km/h"

        # Dodatkowo procent wciśnięcia gazu tylko dla pierwszego motocykla
        if idx == 0:
            percent = (gas + 1) / (counter + 1) * 100
            speed_text += f" {percent:.0f}%"

        text_speed = font.render(speed_text, True, screen_color)
        screen.blit(text_speed, (50, 50 + idx * 50))

        # Reakcja lub falstart
        if moto[idx].false_start:
            reaction_text = "FALSTART!"
        elif moto[idx].reaction_time is not None:
            reaction_text = f"{name.upper()}: {moto[idx].reaction_time} ms"
        else:
            reaction_text = ""

        if reaction_text:
            text_reaction = font.render(reaction_text, True, screen_color)
            screen.blit(text_reaction, (50, 75 + idx * 50))

    if keys[pygame.K_UP]:
        acc1 = font.render("!", True, (255, 0, 0))
        screen.blit(acc1, (30, 50))
        gas = gas+1

    pygame.display.flip()

    if not green_light_visible:
        clock.tick(240)
    else:
        clock.tick(50)

    counter = counter + 1

pygame.quit()