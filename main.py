import pygame
import os
import random
pygame.init()

# --- Setup ---
width = 800
height = 700

display = pygame.display.set_mode((width, height))
pygame.display.set_caption('2D Test Game')

clock = pygame.time.Clock()
fps = 60
background = (0, 100, 0)

font = pygame.font.SysFont("Consolas", 36, bold=True)

# --- High Score Functions ---
def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))


# --- Classes ---
class Player:
    def __init__(self, x, y, size, color):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        self.speed = 3
        self.dx = self.speed
        self.dy = 0

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.dx, self.dy = -self.speed, 0
        if keys[pygame.K_RIGHT]:
            self.dx, self.dy = self.speed, 0
        if keys[pygame.K_UP]:
            self.dx, self.dy = 0, -self.speed
        if keys[pygame.K_DOWN]:
            self.dx, self.dy = 0, self.speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Wrap around screen edges
        if self.rect.right < 0:
            self.rect.left = width
        elif self.rect.left > width:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = height
        elif self.rect.top > height:
            self.rect.bottom = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)


class Enemy:
    def __init__(self, x, y, size, color):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        self.speed = random.randint(1, 3)
        self.dx = 0
        self.dy = 0
        self.last_update = pygame.time.get_ticks()
        self.update_delay = random.randint(200, 600)

    def chase(self, player):
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.update_delay:
            self.last_update = now
            if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
                if player.rect.x < self.rect.x:
                    self.dx, self.dy = -self.speed, 0
                else:
                    self.dx, self.dy = self.speed, 0
            else:
                if player.rect.y < self.rect.y:
                    self.dx, self.dy = 0, -self.speed
                else:
                    self.dx, self.dy = 0, self.speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Wrap around screen edges
        if self.rect.right < 0:
            self.rect.left = width
        elif self.rect.left > width:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = height
        elif self.rect.top > height:
            self.rect.bottom = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)


# --- Game Reset ---
def reset_game(selected_color):
    global player, enemies, score, last_score_update, game_over
    player = Player(200, 200, 20, selected_color)
    enemies = [Enemy(400, 400, 25, (255, 100, 0))]
    score = 0
    last_score_update = pygame.time.get_ticks()
    game_over = False


# --- Initialize ---
colors = [(0, 200, 255), (255, 50, 50), (50, 255, 50), (255, 255, 0), (200, 0, 200)]
color_index = 0
selected_color = colors[color_index]

high_score = load_high_score()
game_over = False
in_menu = True
score = 0


# --- Main Loop ---
run = True
while run:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if in_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    color_index = (color_index - 1) % len(colors)
                    selected_color = colors[color_index]
                if event.key == pygame.K_RIGHT:
                    color_index = (color_index + 1) % len(colors)
                    selected_color = colors[color_index]
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    reset_game(selected_color)
                    in_menu = False
        else:
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game(selected_color)
                if event.key == pygame.K_m:  # go back to menu
                    in_menu = True
                    game_over = False

    display.fill(background)

    if in_menu:
        title = font.render("Choose Your Color", True, (255, 255, 255))
        display.blit(title, (width//2 - title.get_width()//2, 100))

        # Draw color options
        for i, c in enumerate(colors):
            rect = pygame.Rect(200 + i*100, 300, 50, 50)
            pygame.draw.rect(display, c, rect, border_radius=5)
            if i == color_index:
                pygame.draw.rect(display, (255, 255, 255), rect, 3)

        info = font.render("← → to choose, ENTER to start", True, (200, 200, 200))
        display.blit(info, (width//2 - info.get_width()//2, 500))

    elif not game_over:
        # Update score
        current_time = pygame.time.get_ticks()
        if current_time - last_score_update >= 1000:
            score += 1
            last_score_update = current_time
            if score % 10 == 0:
                rand_x = random.randint(0, width - 25)
                rand_y = random.randint(0, height - 25)
                enemies.append(Enemy(rand_x, rand_y, 25, (255, 100, 0)))

        # Player
        player.handle_keys()
        player.update()
        player.draw(display)

        # Enemies
        for enemy in enemies:
            enemy.chase(player)
            enemy.update()
            enemy.draw(display)
            if player.rect.colliderect(enemy.rect):
                game_over = True
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)

        # Draw scores
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        display.blit(score_text, (10, 10))
        high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 0))
        display.blit(high_score_text, (10, 50))

    else:
        game_over_text = font.render("GAME OVER!", True, (255, 50, 50))
        display.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2,
                                      height // 2 - game_over_text.get_height() // 2))

        score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        display.blit(score_text, (width // 2 - score_text.get_width() // 2,
                                  height // 2 + 50))

        high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 0))
        display.blit(high_score_text, (width // 2 - high_score_text.get_width() // 2,
                                       height // 2 + 100))

        restart_text = font.render("Press R to Restart", True, (200, 200, 200))
        display.blit(restart_text, (width // 2 - restart_text.get_width() // 2,
                                    height // 2 + 160))

        menu_text = font.render("Press M for Menu", True, (200, 200, 200))
        display.blit(menu_text, (width // 2 - menu_text.get_width() // 2,
                                 height // 2 + 210))

    pygame.display.update()

pygame.quit()
