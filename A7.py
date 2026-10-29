#Brittan Glade u1529888 10/26/26
#Cave Game (Not Minecraft)
#Help the headcrab escape the guards. You have to get enough pizza to leave the cave. (I let my younger siblings choose the images)
#https://github.com/Psy-Pug/A7
import sys
import pygame
from pygame.locals import Rect
#window and screen setup
screen_width = 800
screen_height = 600
fps = 60
inventory_height = 80
player_speed = 3.5
required_items = 3
#Image filenames
background_img = "map.png"
player_img = "hc.png"
guard_img = "guard.png"
item_img = "pizza.png"
#Goal/exit
goal_rect = Rect(screen_width - 80, 100, 60, screen_height - 200)
#loads images
def load_image(name):
    try:
        return pygame.image.load(name).convert_alpha()
    except Exception as e:
        raise SystemExit(f"Failed to load image '{name}': {e}")
#sprite classes
# creates walls with collision
class Wall(pygame.sprite.Sprite):
    def __init__(self, rect, color=(100, 50, 20)):
        super().__init__()
        self.image = pygame.Surface((rect.width, rect.height))
        self.image.fill(color)
        self.rect = rect
#makes the pizza item so it can be collected
class Item(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
#makes the guards move, collide, and bounce off walls
class Guard(pygame.sprite.Sprite):
    def __init__(self, image, pos, velocity, walls):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(velocity)
        self.speed = self.vel.length()
        self.walls = walls
        self.mask = pygame.mask.from_surface(self.image)
#logic for moving and bouncing
    def move(self):
        self.pos += self.vel
#horizantal movement
        self.rect.centerx = round(self.pos.x)
        for wall in pygame.sprite.spritecollide(self, self.walls, False):
            if self.vel.x > 0:
                self.rect.right = wall.rect.left
            elif self.vel.x < 0:
                self.rect.left = wall.rect.right
            self.pos.x = self.rect.centerx
            self.vel.x *= -1
#vertical movement
        self.rect.centery = round(self.pos.y)
        for wall in pygame.sprite.spritecollide(self, self.walls, False):
            if self.vel.y > 0:
                self.rect.bottom = wall.rect.top
            elif self.vel.y < 0:
                self.rect.top = wall.rect.bottom
            self.pos.y = self.rect.centery
            self.vel.y *= -1
#prevents guards from going in the inventory ui area
        if self.rect.bottom > screen_height - inventory_height:
            self.rect.bottom = screen_height - inventory_height
            self.pos.y = self.rect.centery
            self.vel.y *= -1
#Headcrab player sprite/movement/collision,controls
class Player(pygame.sprite.Sprite):
    def __init__(self, image, pos, walls):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(0, 0)
        self.walls = walls
        self.mask = pygame.mask.from_surface(self.image)
#ajusts speed and velocity for the controls
    def update_velocity(self):
        keys = pygame.key.get_pressed()
        vx, vy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vx = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vy = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vy = 1
        v = pygame.math.Vector2(vx, vy)
        if v.length_squared() > 0:
            v = v.normalize() * player_speed
        self.vel = v
#handles wall collision
    def move_and_collide(self):
        self.pos += self.vel

        self.rect.centerx = round(self.pos.x)
        for wall in pygame.sprite.spritecollide(self, self.walls, False):
            if self.vel.x > 0:
                self.rect.right = wall.rect.left
            elif self.vel.x < 0:
                self.rect.left = wall.rect.right
            self.pos.x = self.rect.centerx

        self.rect.centery = round(self.pos.y)
        for wall in pygame.sprite.spritecollide(self, self.walls, False):
            if self.vel.y > 0:
                self.rect.bottom = wall.rect.top
            elif self.vel.y < 0:
                self.rect.top = wall.rect.bottom
            self.pos.y = self.rect.centery
#prevents the player from being able to move into the ui area
        if self.rect.bottom > screen_height - inventory_height:
            self.rect.bottom = screen_height - inventory_height
            self.pos.y = self.rect.centery
#updates player state
    def update(self):
        self.update_velocity()
        self.move_and_collide()
#main game loop
def main():
    #establishes the pygame, window, and clock
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Cave Game (Not Minecraft)")
    clock = pygame.time.Clock()
#loads and scales images
    bg_img = load_image(background_img)
    player_img_loaded = load_image(player_img)
    guard_img_loaded = load_image(guard_img)
    item_img_loaded = load_image(item_img)

    player_img_scaled = pygame.transform.smoothscale(player_img_loaded, (48, 48))

    bg_img = pygame.transform.smoothscale(bg_img, (screen_width, screen_height))
#sprite groups
    all_sprites = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    guards = pygame.sprite.Group()
    items = pygame.sprite.Group()
#creates my walls
    wall_rects = [
        Rect(0, 0, screen_width, 20),
        Rect(0, 0, 20, screen_height - inventory_height),
        Rect(screen_width - 20, 0, 20, screen_height - inventory_height),
        Rect(0, screen_height - inventory_height - 20, screen_width, 20),
        Rect(150, 80, 40, 360),
        Rect(300, 200, 300, 40),
        Rect(300, 340, 300, 40),
        Rect(520, 80, 40, 120),
        Rect(100, 480, 200, 40),
    ]
    for r in wall_rects:
        w = Wall(r)
        walls.add(w)
        all_sprites.add(w)
#creates player
    player_start = (60, 60)
    player = Player(player_img_scaled, player_start, walls)
    all_sprites.add(player)
#places pizza
    item_positions = [(220, 140), (420, 260), (420, 380), (700, 120), (120, 360)]
    for pos in item_positions:
        it = Item(item_img_loaded, pos)
        items.add(it)
        all_sprites.add(it)
#makes 3 different guards with varying sizes and speeds
    g1_img = pygame.transform.smoothscale(guard_img_loaded, (100, 100))
    g2_img = pygame.transform.smoothscale(guard_img_loaded, (140, 140))
    g3_img = pygame.transform.smoothscale(guard_img_loaded, (80, 80))

    g1 = Guard(g1_img, (240, 220), (2.0, 0.0), walls)
    g2 = Guard(g2_img, (500, 300), (0.0, 1.6), walls)
    g3 = Guard(g3_img, (600, 180), (-1.4, 1.0), walls)
    for g in (g1, g2, g3):
        guards.add(g)
        all_sprites.add(g)
#inventory for pizza as well as fonts
    inventory = []
    font = pygame.font.SysFont(None, 24)
    bigfont = pygame.font.SysFont(None, 36)
#flags for the game state
    running = True
    won = False
    message_timer = 0.0
#game loop
    while running:
        dt = clock.tick(fps) / 1000.0
#handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
#player and guard updates
        if not won:
            player.update()

            for g in guards:
                g.move()
#item pickup
            picked = pygame.sprite.spritecollide(player, items, dokill=True, collided=pygame.sprite.collide_mask)
            for _ in picked:
                inventory.append("Pizza")
                message_timer = 1.8
#guard collision/reset player/take 1 pizza
            if pygame.sprite.spritecollideany(player, guards, collided=pygame.sprite.collide_mask):
                player.pos = pygame.math.Vector2(player_start)
                player.rect.center = player_start
                if inventory:
                    inventory.pop()
                message_timer = 1.8

            if player.rect.colliderect(goal_rect):
                if len(inventory) >= required_items:
                    won = True
                    message_timer = 4.0
                else:
                    message_timer = 1.8
#background stuff
        screen.blit(bg_img, (0, 0))
        pygame.draw.rect(screen, (30, 180, 30), goal_rect)
#draws the objects
        for s in all_sprites:
            if isinstance(s, Wall):
                screen.blit(s.image, s.rect)
        for it in items:
            screen.blit(it.image, it.rect)
        for g in guards:
            screen.blit(g.image, g.rect)
        screen.blit(player.image, player.rect)
#ui stuff for the inventory
        inv_bar = Rect(0, screen_height - inventory_height, screen_width, inventory_height)
        pygame.draw.rect(screen, (40, 40, 40), inv_bar)
        pygame.draw.line(screen, (180, 180, 180), (0, screen_height - inventory_height), (screen_width, screen_height - inventory_height), 2)
        inv_text = font.render(f"Inventory: {len(inventory)} / {required_items}", True, (255, 255, 255))
        screen.blit(inv_text, (10, screen_height - inventory_height + 10))
        icon_size = 40
        small_icon = pygame.transform.smoothscale(item_img_loaded, (icon_size, icon_size))
        for i in range(len(inventory)):
            screen.blit(small_icon, (10 + i * (icon_size + 6), screen_height - inventory_height + 30))
#hit/win messeges
        if message_timer > 0:
            message_timer -= dt
            if won:
                txt = bigfont.render("Freedom at last!", True, (255, 240, 200))
                screen.blit(txt, (screen_width//2 - txt.get_width()//2, 10))
            else:
                txt = font.render("AAAAUUUGGHHH", True, (255, 240, 200))
                screen.blit(txt, (screen_width//2 - txt.get_width()//2, 10))
#Messege if the player doesn't have enough pizza
        if player.rect.colliderect(goal_rect) and not won and len(inventory) < required_items:
            hint = font.render(f"You need {required_items} items to leave you silly goose!", True, (255, 200, 50))
            screen.blit(hint, (goal_rect.left - hint.get_width() - 10, goal_rect.centery - hint.get_height()//2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
