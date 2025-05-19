import pygame
import sys
from car import Car

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

line_spacing = 40      # px between dashed road lines
road_scroll = 0        # vertical position offset for road lines

font = pygame.font.SysFont(None, 24)

car = Car()
throttle_command = 0.1
throttle_step = 0.1

friction = 0.1
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
    # increase or decrease throttle request
    if keys[pygame.K_RIGHT]:
        throttle_command += throttle_step * dt
    if keys[pygame.K_LEFT]:
        throttle_command -= throttle_step * dt
    throttle_command = max(0.0, min(1.0, throttle_command))
    # forces simulation
    car.apply_throttle(throttle_command, dt) 
    car.set_speed(dt) # apply acceleration for this time step


    # --- Update road scroll based on speed ---
    road_scroll += car.get_speed() * dt * 50  # 50 = visual scale factor (pixels per m/s)
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

    # --- Telemetry Display ---
    speed_mph = car.get_speed() * 2.23694  # 1 m/s = 2.23694 mph
    speed_text = font.render(f"Speed: {speed_mph:.2f} MPH", True, (0, 0, 0))
    throttle_text = font.render(f"Throttle: {throttle_command:.2f}", True, (0, 0, 0))
    torque_text = font.render(f"Torque: {car.calc_torque(car.ecu.rpm):.2f} Nm", True, (0, 0, 0))
    rpm_text = font.render(f"RPM: {car.ecu.rpm:.0f}", True, (0, 0, 0))
    gear_text = font.render(f"Gear: {car.ecu.current_gear}", True, (0, 0, 0))

    screen.blit(speed_text, (10, 10))
    screen.blit(throttle_text, (10, 35))
    screen.blit(torque_text, (10, 60))
    screen.blit(rpm_text, (10, 85))
    screen.blit(gear_text, (10, 110))

    # --- Update Display ---
    pygame.display.flip()

pygame.quit()
sys.exit()
