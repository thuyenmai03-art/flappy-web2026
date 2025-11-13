import pygame, asyncio
from random import randint
from pathlib import Path

# ====== Config ======
WIDTH, HEIGHT = 400, 700
GREEN = (0, 200, 0)
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
BLACK = (0, 0, 0)

TUBE_WIDTH    = 50
TUBE_VELOCITY = 3
TUBE_GAP      = 175

BIRD_X     = 50
BIRD_WIDTH = 35
BIRD_HEIGHT= 35
GRAVITY    = 0.65

ASSET_BG   = Path("background.png")
ASSET_BIRD = Path("bird.png")

# ====== Async game loop (web-friendly) ======
async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pixel Bird")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    # Assets (with safe fallbacks)
    background_image = None
    bird_image = None
    try:
        if ASSET_BG.exists():
            background_image = pygame.image.load(str(ASSET_BG)).convert()
    except Exception:
        background_image = None
    try:
        if ASSET_BIRD.exists():
            bird_image = pygame.image.load(str(ASSET_BIRD)).convert_alpha()
            bird_image = pygame.transform.scale(bird_image, (BIRD_WIDTH, BIRD_HEIGHT))
    except Exception:
        bird_image = None

    # State
    tube1_x, tube2_x, tube3_x = 600, 800, 1000
    tube1_height = randint(100, 400)
    tube2_height = randint(100, 400)
    tube3_height = randint(100, 400)

    bird_y = 400
    bird_drop_velocity = 0.0

    score = 0
    tube1_pass = tube2_pass = tube3_pass = False
    pausing = False
    running = True
    tube_velocity = TUBE_VELOCITY

    # --- helper: SPACE or TAP does the same ---
    def jump_or_reset():
        nonlocal pausing, bird_y, bird_drop_velocity, tube_velocity
        nonlocal tube1_x, tube2_x, tube3_x, tube1_height, tube2_height, tube3_height
        nonlocal tube1_pass, tube2_pass, tube3_pass, score
        if pausing:
            # reset game
            bird_y = 400
            bird_drop_velocity = 0.0
            tube_velocity = TUBE_VELOCITY
            tube1_x, tube2_x, tube3_x = 600, 800, 1000
            tube1_height = randint(100, 400)
            tube2_height = randint(100, 400)
            tube3_height = randint(100, 400)
            tube1_pass = tube2_pass = tube3_pass = False
            score = 0
            pausing = False
        # jump
        bird_drop_velocity = -10

    while running:
        # ====== Input ======
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # keyboard
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                jump_or_reset()
            # mouse click (desktop & web tap usually maps here)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                jump_or_reset()
            # true touch event (on mobile SDL2)
            elif hasattr(pygame, "FINGERDOWN") and event.type == pygame.FINGERDOWN:
                jump_or_reset()

        # ====== Update ======
        if not pausing:
            bird_y += bird_drop_velocity
            bird_drop_velocity += GRAVITY

            tube1_x -= tube_velocity
            tube2_x -= tube_velocity
            tube3_x -= tube_velocity

            if tube1_x < -TUBE_WIDTH:
                tube1_x = 550; tube1_height = randint(100, 400); tube1_pass = False
            if tube2_x < -TUBE_WIDTH:
                tube2_x = 550; tube2_height = randint(100, 400); tube2_pass = False
            if tube3_x < -TUBE_WIDTH:
                tube3_x = 550; tube3_height = randint(100, 400); tube3_pass = False

        # ====== Render ======
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(GREEN)

        # pipes
        tube1_rect = pygame.draw.rect(screen, BLUE, (tube1_x, 0, TUBE_WIDTH, tube1_height))
        tube2_rect = pygame.draw.rect(screen, BLUE, (tube2_x, 0, TUBE_WIDTH, tube2_height))
        tube3_rect = pygame.draw.rect(screen, BLUE, (tube3_x, 0, TUBE_WIDTH, tube3_height))
        tube1_rect_inv = pygame.draw.rect(
            screen, BLUE, (tube1_x, tube1_height + TUBE_GAP, TUBE_WIDTH, HEIGHT - tube1_height - TUBE_GAP)
        )
        tube2_rect_inv = pygame.draw.rect(
            screen, BLUE, (tube2_x, tube2_height + TUBE_GAP, TUBE_WIDTH, HEIGHT - tube2_height - TUBE_GAP)
        )
        tube3_rect_inv = pygame.draw.rect(
            screen, BLUE, (tube3_x, tube3_height + TUBE_GAP, TUBE_WIDTH, HEIGHT - tube3_height - TUBE_GAP)
        )

        # bird
        if bird_image:
            bird_rect = screen.blit(bird_image, (BIRD_X, bird_y))
        else:
            bird_rect = pygame.draw.rect(screen, RED, (BIRD_X, bird_y, BIRD_WIDTH, BIRD_HEIGHT))

        # score & pass checks
        score_surf = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_surf, (5, 5))

        if tube1_x + TUBE_WIDTH <= BIRD_X and not tube1_pass:
            score += 1; tube1_pass = True
        if tube2_x + TUBE_WIDTH <= BIRD_X and not tube2_pass:
            score += 1; tube2_pass = True
        if tube3_x + TUBE_WIDTH <= BIRD_X and not tube3_pass:
            score += 1; tube3_pass = True

        # collisions
        for tube in (tube1_rect, tube2_rect, tube3_rect, tube1_rect_inv, tube2_rect_inv, tube3_rect_inv):
            if bird_rect.colliderect(tube) and not pausing:
                pausing = True
                tube_velocity = 0
                bird_drop_velocity = 0

        if pausing:
            game_over_txt = font.render(f"Game Over, Score: {score}", True, BLACK)
            press_space_txt = font.render("Press SPACE or TAP to continue", True, BLACK)
            screen.blit(game_over_txt, (100, 200))
            screen.blit(press_space_txt, (60, 230))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)   # important for web

    pygame.quit()

asyncio.run(main())
