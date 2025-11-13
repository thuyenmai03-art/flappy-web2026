import pygame, asyncio
from random import randint
from pathlib import Path

# ====== Cấu hình cơ bản ======
WIDTH, HEIGHT = 400, 600
GREEN = (0, 200, 0)
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
BLACK = (0, 0, 0)

TUBE_WIDTH    = 50
TUBE_VELOCITY = 3
TUBE_GAP      = 175

BIRD_X       = 50
BIRD_WIDTH   = 35
BIRD_HEIGHT  = 35
GRAVITY      = 0.65

ASSET_BG   = Path("background.png")
ASSET_BIRD = Path("bird.png")

# ====== Game loop dùng asyncio cho web ======
async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pixel Bird")
    clock = pygame.time.Clock()

    # Font mặc định (ổn định trên web)
    font = pygame.font.Font(None, 24)

    # Ảnh nền & chim (có thể thiếu -> fallback an toàn)
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

    # Trạng thái ban đầu
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

    while running:
        # ====== Input ======
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if pausing:
                        # Reset
                        bird_y = 400
                        bird_drop_velocity = 0
                        tube1_x, tube2_x, tube3_x = 600, 800, 1000
                        tube1_height = randint(100, 400)
                        tube2_height = randint(100, 400)
                        tube3_height = randint(100, 400)
                        tube1_pass = tube2_pass = tube3_pass = False
                        score = 0
                        pausing = False
                        tube_velocity = TUBE_VELOCITY
                    # nhảy
                    bird_drop_velocity = -10

        # ====== Update ======
        if not pausing:
            bird_y += bird_drop_velocity
            bird_drop_velocity += GRAVITY

            tube1_x -= tube_velocity
            tube2_x -= tube_velocity
            tube3_x -= tube_velocity

            if tube1_x < -TUBE_WIDTH:
                tube1_x = 550
                tube1_height = randint(100, 400)
                tube1_pass = False
            if tube2_x < -TUBE_WIDTH:
                tube2_x = 550
                tube2_height = randint(100, 400)
                tube2_pass = False
            if tube3_x < -TUBE_WIDTH:
                tube3_x = 550
                tube3_height = randint(100, 400)
                tube3_pass = False

        # ====== Render ======
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(GREEN)

        # Ống trên
        tube1_rect = pygame.draw.rect(screen, BLUE, (tube1_x, 0, TUBE_WIDTH, tube1_height))
        tube2_rect = pygame.draw.rect(screen, BLUE, (tube2_x, 0, TUBE_WIDTH, tube2_height))
        tube3_rect = pygame.draw.rect(screen, BLUE, (tube3_x, 0, TUBE_WIDTH, tube3_height))
        # Ống dưới
        tube1_rect_inv = pygame.draw.rect(
            screen, BLUE, (tube1_x, tube1_height + TUBE_GAP, TUBE_WIDTH, HEIGHT - tube1_height - TUBE_GAP)
        )
        tube2_rect_inv = pygame.draw.rect(
            screen, BLUE, (tube2_x, tube2_height + TUBE_GAP, TUBE_WIDTH, HEIGHT - tube2_height - TUBE_GAP)
        )
        tube3_rect_inv = pygame.draw.rect(
            screen, BLUE, (tube3_x, tube3_height + TUBE_GAP, TUBE_WIDTH, HEIGHT - tube3_height - TUBE_GAP)
        )

        # Chim
        if bird_image:
            bird_rect = screen.blit(bird_image, (BIRD_X, bird_y))
        else:
            bird_rect = pygame.draw.rect(screen, RED, (BIRD_X, bird_y, BIRD_WIDTH, BIRD_HEIGHT))

        # Score
        score_surf = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_surf, (5, 5))

        # Cộng điểm khi qua ống
        if tube1_x + TUBE_WIDTH <= BIRD_X and not tube1_pass:
            score += 1; tube1_pass = True
        if tube2_x + TUBE_WIDTH <= BIRD_X and not tube2_pass:
            score += 1; tube2_pass = True
        if tube3_x + TUBE_WIDTH <= BIRD_X and not tube3_pass:
            score += 1; tube3_pass = True

        # Va chạm
        for tube in (tube1_rect, tube2_rect, tube3_rect, tube1_rect_inv, tube2_rect_inv, tube3_rect_inv):
            if bird_rect.colliderect(tube) and not pausing:
                pausing = True
                tube_velocity = 0
                bird_drop_velocity = 0

        if pausing:
            game_over_txt = font.render(f"Game Over, Score: {score}", True, BLACK)
            press_space_txt = font.render("Press SPACE to continue", True, BLACK)
            screen.blit(game_over_txt, (100, 200))
            screen.blit(press_space_txt, (90, 230))

        pygame.display.flip()
        clock.tick(60)
        # QUAN TRỌNG cho web
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
