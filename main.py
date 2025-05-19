import pygame
import sys

# --- Init ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Constants ---
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
YELLOW = (255, 255, 0)
CAR_COLOR = (100, 200, 255)

CAR_WIDTH, CAR_HEIGHT = 60, 30
car_x = WIDTH // 2 - CAR_WIDTH // 2
car_y = HEIGHT - 100

car_speed = 0          # m/s
max_speed = 30         # m/s
acceleration = 5       # m/s²
brake_decel = 7        # m/s²
friction = 0.8         # % loss per second

line_spacing = 40      # px between dashed road lines
road_scroll = 0        # vertical position offset for road lines

font = pygame.font.SysFont(None, 24)

# --- Main Loop ---
running = True
while running:
    # --- Time Management ---
    dt_ms = clock.tick(60)         # Milliseconds since last frame
    dt = dt_ms / 1000.0            # Convert to seconds

    screen.fill(WHITE)

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Controls (Throttle/Brake) ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        car_speed += acceleration * dt
    if keys[pygame.K_LEFT]:
        car_speed -= brake_decel * dt

    # --- Apply Friction ---
    car_speed *= (1 - friction * dt)
    car_speed = max(min(car_speed, max_speed), -max_speed)

    # --- Update road scroll based on speed ---
    road_scroll += car_speed * dt * 50  # 50 = visual scale factor (pixels per m/s)
    if road_scroll >= line_spacing:
        road_scroll -= line_spacing

    # --- Draw Road ---
    road_rect = pygame.Rect(WIDTH//3, 0, WIDTH//3, HEIGHT)
    pygame.draw.rect(screen, GREY, road_rect)

    # Dashed center line
    for i in range(0, HEIGHT, line_spacing * 2):
        pygame.draw.rect(
            screen,
            YELLOW,
            (WIDTH // 2 - 5, i + road_scroll, 10, line_spacing)
        )

    # --- Draw Car (stationary) ---
    pygame.draw.rect(screen, CAR_COLOR, (car_x, car_y, CAR_WIDTH, CAR_HEIGHT))

    # --- Speed Display ---
    speed_text = font.render(f"Speed: {car_speed:.2f} m/s", True, (0, 0, 0))
    screen.blit(speed_text, (10, 10))

    # --- Update Display ---
    pygame.display.flip()

pygame.quit()
sys.exit()
