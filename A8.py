#Brittan Glade 11/3/26 The sequal to the old game
#Help the headcrab escape the guards. You have to get enough pizza to leave the cave. (I let my younger siblings choose the images)
import sys
import random
import pygame
from pygame.locals import Rect
width = 800
height = 600
FPS = 60
Inventory = 80
speed = 3.5
reqitems = 3

# Images
Background_img = "map.png"
Player_img = "hc.png"
Guard_img = "guard.png"
Item_img = "pizza.png"
potion_img = "timepotion.png"

# Goal
goalrect = Rect(width - 80, 100, 60, height - 200)

def load_image(name):
    try:
        return pygame.image.load(name).convert_alpha()
    except Exception as e:
        raise SystemExit(f"Failed to load image '{name}': {e}")

# Temporary helper to let collision helpers accept GameObject instances
def to_pygame_sprite(obj):
    s = pygame.sprite.Sprite()
    s.rect = obj.rect
    s.mask = obj.mask
    return s
#object class
class GameObject:
    def __init__(self, surface):
        self.image = surface
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def set_position(self, x, y):
        self.rect.topleft = (round(x), round(y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def collides_with(self, other):
        offset = (other.rect.left - self.rect.left, other.rect.top - self.rect.top)
        return self.mask.overlap(other.mask, offset)
#speed and collisions for headcrab
class Character(GameObject):
    def __init__(self, surface, center, walls, speed=speed):
        super().__init__(surface)
        self.rect.center = center
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(0, 0)
        self.walls = walls
        self.speed = speed
#sets centers
    def set_center(self, cx, cy):
        tx = cx - self.rect.width // 2
        ty = cy - self.rect.height // 2
        super().set_position(tx, ty)
#speed
    def update_velocity(self):
        keys = pygame.key.get_pressed()
        vx = vy = 0
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
            v = v.normalize() * self.speed
        self.vel = v

    def move_and_collide(self):
        self.pos += self.vel

        # horizontal
        self.rect.centerx = round(self.pos.x)
        for w in pygame.sprite.spritecollide(to_pygame_sprite(self), self.walls, False):
            if self.vel.x > 0:
                self.rect.right = w.rect.left
            elif self.vel.x < 0:
                self.rect.left = w.rect.right
            self.pos.x = self.rect.centerx

        # vertical
        self.rect.centery = round(self.pos.y)
        for w in pygame.sprite.spritecollide(to_pygame_sprite(self), self.walls, False):
            if self.vel.y > 0:
                self.rect.bottom = w.rect.top
            elif self.vel.y < 0:
                self.rect.top = w.rect.bottom
            self.pos.y = self.rect.centery

        # prevent entering inventory UI
        if self.rect.bottom > height - Inventory:
            self.rect.bottom = height - Inventory
            self.pos.y = self.rect.centery

        # sync back top-left
        self.set_position(self.rect.left, self.rect.top)

    def update(self):
        self.update_velocity()
        self.move_and_collide()
#code for normal guards
class Guard(GameObject):
    def __init__(self, surface, center, velocity, walls):
        super().__init__(surface)
        self.rect.center = center
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(velocity)
        self.walls = walls

    def set_center(self, cx, cy):
        tx = cx - self.rect.width // 2
        ty = cy - self.rect.height // 2
        super().set_position(tx, ty)

    def move(self):
        self.pos += self.vel

        # horizontal
        self.rect.centerx = round(self.pos.x)
        for w in pygame.sprite.spritecollide(to_pygame_sprite(self), self.walls, False):
            if self.vel.x > 0:
                self.rect.right = w.rect.left
            elif self.vel.x < 0:
                self.rect.left = w.rect.right
            self.pos.x = self.rect.centerx
            self.vel.x *= -1

        # vertical
        self.rect.centery = round(self.pos.y)
        for w in pygame.sprite.spritecollide(to_pygame_sprite(self), self.walls, False):
            if self.vel.y > 0:
                self.rect.bottom = w.rect.top
            elif self.vel.y < 0:
                self.rect.top = w.rect.bottom
            self.pos.y = self.rect.centery
            self.vel.y *= -1

        # UI boundary
        if self.rect.bottom > height - Inventory:
            self.rect.bottom = height - Inventory
            self.pos.y = self.rect.centery
            self.vel.y *= -1

        self.set_center(self.rect.centerx, self.rect.centery)
#guard teleport code
class TeleportGuard(Guard):
    def __init__(self, surface, center, velocity, walls, teleport_ms=3000):
        super().__init__(surface, center, velocity, walls)
        self.teleport_interval = teleport_ms
        self.last_teleport = pygame.time.get_ticks()

    def update(self, now, bounds_rect):
        if now - self.last_teleport >= self.teleport_interval:
            x = random.randint(bounds_rect.left + 10, bounds_rect.right - self.rect.width - 10)
            y = random.randint(bounds_rect.top + 10, bounds_rect.bottom - self.rect.height - 10)
            self.set_center(x + self.rect.width // 2, y + self.rect.height // 2)
            self.pos = pygame.math.Vector2(self.rect.center)
            self.last_teleport = now
        else:
            self.move()
#classes for the various items
class Item(GameObject):
    def __init__(self, surface, center):
        super().__init__(surface)
        self.rect.center = center

    def on_pickup(self, game_state):
        return True

class TimeItem(Item):
    def __init__(self, surface, center, add_seconds=5):
        super().__init__(surface, center)
        self.add_seconds = add_seconds

    def on_pickup(self, game_state):
        game_state['timer'] += self.add_seconds
        return True
    #makes the walls
class Wall(pygame.sprite.Sprite):
    def __init__(self, rect, color=(100, 50, 20)):
        super().__init__()
        self.image = pygame.Surface((rect.width, rect.height))
        self.image.fill(color)
        self.rect = rect
def main():
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Minecraft the squeakual")
    clock = pygame.time.Clock()

    # load images
    bg = load_image(Background_img)
    bg = pygame.transform.smoothscale(bg, (width, height))
    player_surf = pygame.transform.smoothscale(load_image(Player_img), (48, 48))
    guard_base = load_image(Guard_img)
    item_surf = pygame.transform.smoothscale(load_image(Item_img), (40, 40))
    timepotion_surf = pygame.transform.smoothscale(load_image(potion_img), (40, 40))

    # walls
    walls = pygame.sprite.Group()
    all_walls_rects = [
        Rect(0, 0, width, 20),
        Rect(0, 0, 20, height - Inventory),
        Rect(width - 20, 0, 20, height - Inventory),
        Rect(0, height - Inventory - 20, width, 20),
        Rect(150, 80, 40, 360),
        Rect(300, 200, 300, 40),
        Rect(300, 340, 300, 40),
        Rect(520, 80, 40, 120),
        Rect(100, 480, 200, 40),
    ]
    for r in all_walls_rects:
        w = Wall(r)
        walls.add(w)

    # Headcrab
    player_start = (60, 60)
    player = Character(player_surf, player_start, walls)

    # item positions
    initial_positions = [(220, 140), (420, 260), (420, 380), (700, 120), (120, 360)]
    items = []
    for pos in initial_positions:
        items.append(TimeItem(item_surf, pos, add_seconds=7))

    # guards that are a mix of normal and teleport guards
    g1 = Guard(pygame.transform.smoothscale(guard_base, (100, 100)), (240, 220), (2.0, 0.0), walls)
    g2 = TeleportGuard(pygame.transform.smoothscale(guard_base, (140, 140)), (500, 300), (0.0, 1.6), walls, teleport_ms=4000)
    g3 = Guard(pygame.transform.smoothscale(guard_base, (80, 80)), (600, 180), (-1.4, 1.0), walls)
    guards = [g1, g2, g3]

    # UI and fonts
    font = pygame.font.SysFont(None, 24)
    bigfont = pygame.font.SysFont(None, 36)

    # game timer via pygame event
    Timerevent = pygame.USEREVENT + 1
    pygame.time.set_timer(Timerevent, 1000)
    game_state = {"timer": 60}

    inventory = []
    running = True
    won = False
    game_over = False
    message_timer = 0.0
    show_timeout_msg = False

    # play area for teleports that avoids the ui like the plague
    play_bounds = Rect(20, 20, width - 40, height - Inventory - 20)

    while running:
        dt = clock.tick(FPS) / 1000.0

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == Timerevent and not won and not game_over:
                game_state['timer'] -= 1
                if game_state['timer'] <= 0:
                    game_over = True
                    show_timeout_msg = True
                    message_timer = 4.0

        # updates when active
        if not won and not game_over:
            player.update()

            now = pygame.time.get_ticks()
            for g in guards:
                if isinstance(g, TeleportGuard):
                    g.update(now, play_bounds)
                else:
                    g.move()

            # player item collisions
            picked = []
            for it in list(items):
                # compute offset stuff
                if player.collides_with(it):
                    removed = it.on_pickup(game_state)
                    if removed:
                        picked.append(it)
                        inventory.append("Pizza")
                        message_timer = 1.8
            for it in picked:
                if it in items:
                    items.remove(it)

            # random spawn chance per loop for a new TimeItem
            if random.randint(1, 100) == 1:
                for _ in range(20):
                    rx = random.randint(play_bounds.left + 20, play_bounds.right - 20)
                    ry = random.randint(play_bounds.top + 20, play_bounds.bottom - 20)
                    cand = TimeItem(item_surf, (rx, ry), add_seconds=5)
                    # simple wall overlap check via rect
                    blocked = any(cand.rect.colliderect(w.rect) for w in walls)
                    if not blocked:
                        items.append(cand)
                        break

            # guard collisions
            for g in guards:
                if player.collides_with(g):
                    player.set_center(*player_start)
                    player.pos = pygame.math.Vector2(player.rect.center)
                    if inventory:
                        inventory.pop()
                    message_timer = 1.8

            # reach goal
            if player.rect.colliderect(goalrect):
                if len(inventory) >= reqitems:
                    won = True
                    message_timer = 4.0
                else:
                    message_timer = 1.8

        # draw
        screen.blit(bg, (0, 0))
        pygame.draw.rect(screen, (30, 180, 30), goalrect)

        # draw walls
        for w in walls:
            screen.blit(w.image, w.rect)

        # draw items
        for it in items:
            it.draw(screen)

        # draw guards and player
        for g in guards:
            g.draw(screen)
        player.draw(screen)

        # inventory UI
        inv_bar = Rect(0, height - Inventory, width, Inventory)
        pygame.draw.rect(screen, (40, 40, 40), inv_bar)
        pygame.draw.line(screen, (180, 180, 180), (0, height - Inventory), (width, height - Inventory), 2)
        inv_text = font.render(f"Inventory: {len(inventory)} / {reqitems}", True, (255, 255, 255))
        screen.blit(inv_text, (10, height - Inventory + 10))
        small_icon = pygame.transform.smoothscale(item_surf, (40, 40))
        for i in range(len(inventory)):
            screen.blit(small_icon, (10 + i * 46, height - Inventory + 30))

        # timer HUD with color changes
        timer_val = max(0, game_state['timer'])
        if timer_val <= 5:
            timer_color = (220, 40, 40)
        elif timer_val <= 12:
            timer_color = (230, 200, 30)
        else:
            timer_color = (255, 255, 255)
        timer_text = bigfont.render(f"Time: {timer_val}", True, timer_color)
        screen.blit(timer_text, (width - timer_text.get_width() - 10, 10))

        # messages
        if message_timer > 0:
            message_timer -= dt
            if won:
                txt = bigfont.render("Freedom at last!", True, (255, 240, 200))
                screen.blit(txt, (width // 2 - txt.get_width() // 2, 10))
            elif show_timeout_msg and game_over:
                txt = bigfont.render("You ran out of time!", True, (255, 80, 80))
                screen.blit(txt, (width // 2 - txt.get_width() // 2, 10))
            else:
                txt = font.render("YEEEEEEEOWCH!", True, (255, 240, 200))
                screen.blit(txt, (width // 2 - txt.get_width() // 2, 10))

        # prevents door from opening without enought items
        if player.rect.colliderect(goalrect) and not won and len(inventory) < reqitems:
            hint = font.render(f"You need {reqitems} items to leave!", True, (255, 200, 50))
            screen.blit(hint, (goalrect.left - hint.get_width() - 10, goalrect.centery - hint.get_height() // 2))

        # end screens
        if game_over:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            go_text = bigfont.render("Haha you're bad", True, (255, 80, 80))
            screen.blit(go_text, (width // 2 - go_text.get_width() // 2, height // 2 - 20))
            sub = font.render("Press ESC to close the window :)", True, (200, 200, 200))
            screen.blit(sub, (width // 2 - sub.get_width() // 2, height // 2 + 20))
        elif won:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            wtext = bigfont.render("We gotta winner!", True, (200, 255, 200))
            screen.blit(wtext, (width // 2 - wtext.get_width() // 2, height // 2 - 20))
            sub = font.render("Press ESC to quit tee hee", True, (200, 200, 200))
            screen.blit(sub, (width // 2 - sub.get_width() // 2, height // 2 + 20))

        pygame.display.flip()

        # quit with escape key

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()