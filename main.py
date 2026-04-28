import pygame
import json
import sys
import os
import random

class Game:
    def __init__(self):
        pygame.init()
        self.V_WIDTH, self.V_HEIGHT = 1280, 720
        self.virtual_surface = pygame.Surface((self.V_WIDTH, self.V_HEIGHT))

        self.screen = pygame.display.set_mode((800, 450), pygame.RESIZABLE)
        self.REAL_WIDTH, self.REAL_HEIGHT = self.screen.get_size()

        self.calculate_scaling()

        pygame.display.set_caption("Space shooter 2030")

        self.clock = pygame.time.Clock()
        self.fps = 60

        self.states = ["MENU", "PLAYING", "SUMMARY", "SHOP"]
        self.current_state = "MENU"

        self.load_data()

        self.running = True

        # assets dir
        self.base_dir = os.path.dirname(__file__)
        self.assets_dir = os.path.join(self.base_dir, "assets")

        self.images = {}
        self.fonts = {}

        self.load_assets()

        self.start_btn = Button(640, 350, self.images["start_btn"], 1.0)
        self.shop_btn = Button(640, 480, self.images["shop_btn"], 1.0)
        self.exit_btn = Button(640, 610, self.images["exit_btn"], 1.0)
        self.back_btn = Button(50, 50, self.images["back_btn"], 1.0)

        self.font_small = pygame.font.Font("assets/fonts/font.ttf", 24)
        self.font_medium = pygame.font.Font("assets/fonts/font.ttf", 40)

        self.clicked = False
        self.active_ship_index = 0
        self.active_bullet_index = 0

        self.bg = Background(self.images["bg-playing"], 2)

        self.all_sprite = pygame.sprite.Group()

        self.player = None

        self.enemy_timer = pygame.USEREVENT + 1
        time_enemies = 1000
        pygame.time.set_timer(self.enemy_timer, time_enemies)

        self.enemy_group = pygame.sprite.Group()
        
        self.player_bullet = pygame.sprite.Group()
        self.enemy_bullet = pygame.sprite.Group()

        self.current_wave = 1
        self.spawned_enemies = 0
        self.spawned_boss = 0
        self.spawned_normal = 0
        self.wave_config = [
            {"normal":3, "boss":1},
            {"normal":5, "boss":2},
            {"normal":7, "boss":3}
        ]
        self.game_result = ""

        self.is_paused = False
        self.session_coins = 0

        self.kills = 0
        self.is_boss = False

        self.wave_text_timer = 0
        
        self.music_dir = os.path.join(self.assets_dir, "music")
        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(self.music_dir, "music.mp3"))
        pygame.mixer.music.play(-1)
        self.shop_sound = pygame.mixer.Sound(os.path.join(self.music_dir, 'shop.wav'))
        self.destroy_sound = pygame.mixer.Sound(os.path.join(self.music_dir, 'destroy.mp3'))

    def calculate_scaling(self):

        ratio = min(self.REAL_WIDTH / self.V_WIDTH, self.REAL_HEIGHT / self.V_HEIGHT)

        self.new_size = (int(self.V_WIDTH * ratio), int(self.V_HEIGHT * ratio))

        off_x = (self.REAL_WIDTH - self.new_size[0]) // 2
        off_y = (self.REAL_HEIGHT - self.new_size[1]) // 2

        self.pos = (off_x, off_y)

    def load_assets(self):
        img_dir = os.path.join(self.assets_dir, "images")

        self.images["bg-menu"] = pygame.image.load(os.path.join(img_dir, "main-background.png")).convert()
        self.images["bg-shop"] = pygame.image.load(os.path.join(img_dir, "shop-background.png")).convert()
        self.images["bg-playing"] = pygame.image.load(os.path.join(img_dir, "playing-background.png")).convert()
        
        # button images
        self.images["start_btn"] = pygame.transform.smoothscale(pygame.image.load(os.path.join(img_dir, "start_btn.png")).convert_alpha(), (220, 115))
        self.images["shop_btn"] = pygame.transform.smoothscale(pygame.image.load(os.path.join(img_dir, "shop_btn.png")).convert_alpha(), (220, 115))
        self.images["exit_btn"] = pygame.transform.smoothscale(pygame.image.load(os.path.join(img_dir, "exit_btn.png")).convert_alpha(), (220, 115))

        self.images["player_ship"] = pygame.transform.smoothscale(
            pygame.image.load(os.path.join(img_dir, "x1.png")).convert_alpha(), (85, 85)
        )
        
        self.images["item_box"] = pygame.image.load(os.path.join(img_dir, "shop-box.png")).convert_alpha()
        
        self.images["coin_icon"] = pygame.transform.smoothscale(pygame.image.load(os.path.join(img_dir, "coin.png")).convert_alpha(), (50, 50))
        self.images["back_btn"] = pygame.transform.smoothscale(pygame.image.load(os.path.join(img_dir, "back_btn.png")).convert_alpha(), (100, 100))

        
        self.images["X1"] = pygame.transform.smoothscale(
            pygame.image.load(os.path.join(img_dir, "x1.png")).convert_alpha(), (85, 85)
        )
        self.images["X2"] = pygame.transform.smoothscale(
            pygame.image.load(os.path.join(img_dir, "x2.png")).convert_alpha(), (85, 85)
        )
        self.images["X3"] = pygame.transform.smoothscale(
            pygame.image.load(os.path.join(img_dir, "x3.png")).convert_alpha(), (85, 85)
        )
        
        self.images["xx1"] = pygame.transform.smoothscale(
            pygame.image.load(os.path.join(img_dir, "xx1.png")).convert_alpha(), (30, 57)
        )
        
        self.images["xx2"] = pygame.transform.smoothscale(
            pygame.image.load(os.path.join(img_dir, "xx3.png")).convert_alpha(), (50, 97)
        )
        
        self.images["xx3"] = pygame.transform.smoothscale(
            pygame.image.load(os.path.join(img_dir, "xx2.png")).convert_alpha(), (30, 49)
        )
        
        self.images["shop_X1"] = pygame.image.load(os.path.join(img_dir, "shop-x1.png")).convert_alpha()
        self.images["shop_X2"] = pygame.image.load(os.path.join(img_dir, "shop-x2.png")).convert_alpha()
        self.images["shop_X3"] = pygame.image.load(os.path.join(img_dir, "shop-x3.png")).convert_alpha()
        
        self.images["shop_xx1"] = pygame.image.load(os.path.join(img_dir, "shop_xx1.png")).convert_alpha()
        self.images["shop_xx2"] = pygame.image.load(os.path.join(img_dir, "shop_xx2.png")).convert_alpha()
        self.images["shop_xx3"] = pygame.image.load(os.path.join(img_dir, "shop_xx3.png")).convert_alpha()
        
        self.images["heart"] = pygame.transform.smoothscale(pygame.image.load(os.path.join(img_dir, "heart_new.png")).convert_alpha(), (42, 40))
        
        self.images["boss"] = pygame.transform.smoothscale(pygame.image.load(os.path.join(img_dir, "boss.png")).convert_alpha(), (250, 140))
        self.images["enemy"] = pygame.transform.smoothscale(pygame.image.load(os.path.join(img_dir, "enemy.png")).convert_alpha(), (70, 70))
        
        self.images["enemy_bullet"] = pygame.transform.smoothscale(pygame.image.load(os.path.join(img_dir, "enemy_bullet.png")).convert_alpha(), (30, 47))
        self.images["boss_bullet"] = pygame.transform.smoothscale(pygame.image.load(os.path.join(img_dir, "boss_bullet.png")).convert_alpha(), (50, 109))
        
        self.images["exp"] = pygame.transform.smoothscale(pygame.image.load(os.path.join(img_dir, "VFX.png")).convert_alpha(), (125, 75))
        self.images["exp_boss"] = pygame.transform.smoothscale(pygame.image.load(os.path.join(img_dir, "VFX.png")).convert_alpha(), (250, 150))

    def load_data(self):
        try:
            with open("data.json", "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {
                "coins": 0,
                "selected_ship": "shop_X1",
                "selected_bullet": "shop_xx1",
                "ships": [
                    {
                        "image_name": "shop_X1",
                        "price": 0,
                        "owned": True
                    },
                    {
                        "image_name": "shop_X2",
                        "price": 500,
                        "owned": False
                    },
                    {
                        "image_name": "shop_X3",
                        "price": 1200,
                        "owned": False
                    }
                ],
                "bullets": [
                    {
                        "image_name": "shop_xx1",
                        "price": 0,
                        "owned": True
                    },
                    {
                        "image_name": "shop_xx2",
                        "price": 300,
                        "owned": False
                    },
                    {
                        "image_name": "shop_xx3",
                        "price": 500,
                        "owned": False
                    }
                ]
            }
            self.save_data()

    def save_data(self):
        with open("data.json", "w") as f:
            json.dump(self.data, f, indent=2)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

            self.clock.tick(self.fps)
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.VIDEORESIZE:
                self.REAL_WIDTH, self.REAL_HEIGHT = event.w, event.h
                self.screen = pygame.display.set_mode((self.REAL_WIDTH, self.REAL_HEIGHT), pygame.RESIZABLE)
                self.calculate_scaling()

            if event.type == pygame.KEYDOWN:
                if self.current_state == "MENU" and event.key == pygame.K_KP_ENTER:
                    self.current_state = "PLAYING"
                elif event.key == pygame.K_s:
                    self.current_state = "SHOP"
                elif event.key == pygame.K_ESCAPE and self.current_state == "PLAYING":
                    self.is_paused = not self.is_paused
                
                elif self.is_paused and event.key == pygame.K_q:
                    self.end_game("ABORT")
                    self.is_paused = False
            
            if event.type == pygame.MOUSEBUTTONUP:
                self.clicked = False
            
            if event.type == self.enemy_timer and self.current_state == "PLAYING":
                config = self.wave_config[self.current_wave - 1]
                total_in_wave = config["normal"] + config["boss"]

                if self.spawned_enemies < total_in_wave:
                    x_pos = random.randint(60, 1220)

                    can_spawn_boss = self.spawned_boss < config["boss"]
                    can_spawn_normal = self.spawned_normal < config["normal"]

                    if can_spawn_boss and random.random() < 0.1 or (not can_spawn_normal):
                        Enemy([self.all_sprite, self.enemy_group], self.images["boss"], (x_pos, -100), health=5)
                        self.spawned_boss += 1
                    elif can_spawn_normal:
                        Enemy([self.all_sprite, self.enemy_group], self.images["enemy"], (x_pos, -100), health=1)
                        self.spawned_normal += 1
                        
                    self.spawned_enemies = self.spawned_boss + self.spawned_normal

    def update(self):
        mx, my = pygame.mouse.get_pos()

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        try:
            virtual_mx = (mx - self.pos[0]) * (self.V_WIDTH / self.new_size[0])
            virtual_my = (my - self.pos[1]) * (self.V_HEIGHT / self.new_size[1])
            self.mouse_pos = (virtual_mx, virtual_my)
        except ZeroDivisionError:
            self.mouse_pos = (0, 0)

        if self.current_state == "PLAYING" and not self.is_paused:
            self.bg.update()
            self.all_sprite.update()
            self.collisions()
            self.check_wave_status()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.player.can_shoot:
            self.player.shoot([self.all_sprite, self.player_bullet], self.current_bullet_img, self.bullet_type)
            self.player.can_shoot = False
            self.player.shoot_time = pygame.time.get_ticks()

        for enemy in self.enemy_group:
                    bullet_img = self.images["enemy_bullet"] if enemy.health == 1 else self.images["boss_bullet"]
                    enemy.shoot([self.all_sprite, self.enemy_bullet], bullet_img)
       
    def draw(self):
        self.virtual_surface.fill((20, 20, 40))

        if self.current_state == "MENU":
            self.draw_menu()
        elif self.current_state == "SHOP":
            self.draw_shop()
        elif self.current_state == "PLAYING":
            self.bg.draw(self.virtual_surface)
            self.all_sprite.draw(self.virtual_surface)
        
            if self.is_paused:
                overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.virtual_surface.blit(overlay, (0,0))
                
                self.draw_text("GAME PAUSED", self.font_medium, (255,255,255), self.virtual_surface, 640, 300)
                self.draw_text("Press Q to Abort or ESC to Resume", self.font_small, (200,200,200), self.virtual_surface, 640, 380)
            
            if self.player is not None:
                for i in range(self.player.health):
                    heart_x = 30 + (i * 50)
                    self.virtual_surface.blit(self.images["heart"], (heart_x, 20))

            coin_txt = self.font_small.render(f"{self.session_coins}", True, (255, 215, 0))
            self.virtual_surface.blit(self.images["coin_icon"], (1200, 30))
            self.virtual_surface.blit(coin_txt, (1135, 39))

        elif self.current_state == "SUMMARY":
            self.draw_summary()
        
        current_time = pygame.time.get_ticks()
        if self.current_wave != 1:
            if current_time - self.wave_text_timer < 2000:
                overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100))
                self.virtual_surface.blit(overlay, (0,0))
                self.draw_text(f"WAVE {self.current_wave}", self.font_medium, (255, 0, 100), self.virtual_surface, 640, 360)
        
        scaled_surface = pygame.transform.smoothscale(self.virtual_surface, self.new_size)
        self.screen.blit(scaled_surface, self.pos)

        pygame.display.flip()

    def draw_menu(self):
        self.virtual_surface.blit(self.images["bg-menu"], (0, 0))

        if self.start_btn.draw(self.virtual_surface, self.mouse_pos):
            
            self.game_result = ""
            self.current_wave = 1
            self.is_paused = False
            self.spawned_boss = 0
            self.spawned_enemies = 0
            self.spawned_normal = 0
            
            self.all_sprite.empty()
            self.enemy_group.empty()
            self.enemy_bullet.empty()
            self.player_bullet.empty()

            self.session_coins = 0
            self.kills = 0
            self.is_boss = False
            
            active_img_key = self.data["selected_ship"].replace("shop_", "")
            player_img = self.images[active_img_key]

            active_ship = self.data["selected_ship"]

            if "X1" in active_ship:
                hp = 2
            elif "X2" in active_ship:
                hp = 4
            else:
                hp = 6

            self.player = Player(self.all_sprite, player_img, (640, 600), hp)

            self.current_state = "PLAYING"
            print("playing")

            bullet_name = self.data["selected_bullet"].replace("shop_", "")
            self.current_bullet_img = self.images[bullet_name]
            self.bullet_type = bullet_name

        if self.shop_btn.draw(self.virtual_surface, self.mouse_pos):
            self.current_state = "SHOP"
            print("shopping")
        if self.exit_btn.draw(self.virtual_surface, self.mouse_pos):
            self.current_state = "EXIT"
            self.running = False
            print("Exiting")
    
    def draw_shop(self):
        
        self.virtual_surface.blit(self.images["bg-shop"], (0, 0))

        coin_txt = self.font_small.render(f"{self.data['coins']}", True, (255, 215, 0))
        self.virtual_surface.blit(self.images["coin_icon"], (1200, 30))
        self.virtual_surface.blit(coin_txt, (1135, 39))

        if self.back_btn.draw(self.virtual_surface, self.mouse_pos):
            self.current_state = "MENU"
        
        positions = [300, 640, 980]

        for index, bullet_data in enumerate(self.data["bullets"]):
            x_pos = positions[index]
            y_pos = 550
            
            box_width, box_height = 300, 300
            bullet_width, bullet_height = 210, 107

            scaled_box = pygame.transform.smoothscale(self.images["item_box"], (box_width, box_height))

            box_rect = scaled_box.get_rect(center=(x_pos, y_pos))
            self.virtual_surface.blit(scaled_box, box_rect)

            if box_rect.collidepoint(self.mouse_pos):
                
                if pygame.mouse.get_pressed()[0] == 1 and not Button.clicked:
                    # self.clicked = True
                    Button.clicked = True

                    self.shop_sound.play()
                    
                    if not bullet_data["owned"]:
                        if self.data["coins"] >= bullet_data["price"]:
                            self.data["coins"] -= bullet_data["price"]
                            bullet_data["owned"] = True
                            self.save_data()
                        else:
                            print("No money!")
                    else:
                        self.active_bullet_index = index

                        self.data["selected_bullet"] = bullet_data["image_name"]
                        self.save_data()
                        print(f"bullet {index} selected")

            
            bullet_img = self.images[bullet_data["image_name"]]
            display_bullet = pygame.transform.smoothscale(bullet_img, (bullet_width, bullet_height))
            bullet_rect = display_bullet.get_rect(center=(x_pos, y_pos - 20))
            self.virtual_surface.blit(display_bullet, bullet_rect)
            
            if bullet_data["owned"]:
                status_txt = "OWNED"
                color = (255, 0, 0)
            else:
                status_txt = f"{bullet_data['price']} $"
                color = (255, 255, 255)
                
            price_surf = self.font_small.render(status_txt, True, color)
            price_rect = price_surf.get_rect(center=(x_pos, y_pos + 75))
            self.virtual_surface.blit(price_surf, price_rect)

            if self.active_bullet_index == index:
                selected_txt = self.font_small.render("SELECTED", True, (255, 255, 0))
                self.virtual_surface.blit(selected_txt, selected_txt.get_rect(center=(x_pos, y_pos + 105)))
        
        for index, ship_data in enumerate(self.data["ships"]):
            x_pos = positions[index]
            y_pos = 200
            
            box_width, box_height = 300, 300
            ship_width, ship_height = 185, 185

            scaled_box = pygame.transform.smoothscale(self.images["item_box"], (box_width, box_height))

            box_rect = scaled_box.get_rect(center=(x_pos, y_pos))
            self.virtual_surface.blit(scaled_box, box_rect)

            if box_rect.collidepoint(self.mouse_pos):

                if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                    self.clicked = True
                    if not ship_data["owned"]:
                        self.data["selected_ship"] = ship_data["image_name"]
                        if self.data["coins"] >= ship_data["price"]:
                            self.data["coins"] -= ship_data["price"]
                            ship_data["owned"] = True
                            self.save_data()
                        else:
                                print("No money!")
                    else:
                        self.data["selected_ship"] = ship_data["image_name"]
                        self.save_data()
                        self.active_ship_index = index
                        print(f"ship {index} selected and saved!")
            
            ship_img = self.images[ship_data["image_name"]]
            display_ship = pygame.transform.smoothscale(ship_img, (ship_width, ship_height))
            ship_rect = display_ship.get_rect(center=(x_pos, y_pos - 20))
            self.virtual_surface.blit(display_ship, ship_rect)
            
            if ship_data["owned"]:
                status_txt = "OWNED"
                color = (0, 255, 0)
            else:
                status_txt = f"{ship_data['price']} $"
                color = (255, 255, 255)
                
            price_surf = self.font_small.render(status_txt, True, color)
            price_rect = price_surf.get_rect(center=(x_pos, y_pos + 75))
            self.virtual_surface.blit(price_surf, price_rect)

            if self.active_ship_index == index:
                selected_txt = self.font_small.render("SELECTED", True, (255, 255, 0))
                self.virtual_surface.blit(selected_txt, selected_txt.get_rect(center=(x_pos, y_pos + 105)))
            
            if pygame.mouse.get_pressed()[0] == 0:
                Button.clicked = False
                
    def collisions(self):
        hits = pygame.sprite.groupcollide(self.enemy_group, self.player_bullet, False, True)
        for enemy in hits:
            enemy.health -= 1
            if enemy.health <= 0:
                if enemy.is_boss:
                    SimpleExplosion(self.all_sprite, self.images["exp_boss"], enemy.rect.center)
                    self.destroy_sound.play()
                else:
                    SimpleExplosion(self.all_sprite, self.images["exp"], enemy.rect.center)
                    self.destroy_sound.play()

                enemy.kill()
                self.kills += 1
                self.session_coins += 50 if self.is_boss else 10
                print(f"received {50 if self.is_boss else 10} coins.")
        
        if pygame.sprite.spritecollide(self.player, self.enemy_bullet, True):
            self.player.health -= 1
            print(f"Player HP: {self.player.health}")
            
            if self.player.health <= 0:      
                self.end_game("LOSE")
                print("Game Over!")
        
        bullet_hit = pygame.sprite.groupcollide(self.enemy_bullet, self.player_bullet, True, True)
        for _ in bullet_hit:
            print("Neutralize!")
    
    def check_wave_status(self):
        config = self.wave_config[self.current_wave - 1]
        total_in_wave = config["normal"] + config["boss"]

        if self.spawned_enemies >= total_in_wave and len(self.enemy_group) == 0:
            if self.current_wave < 3:
                self.current_wave += 1
                self.wave_text_timer = pygame.time.get_ticks()
                self.spawned_enemies = self.spawned_boss  = self.spawned_normal = 0
                print(f"Wave {self.current_wave} Started!")
                
                if self.current_wave == 2:
                    pygame.time.set_timer(self.enemy_timer, 750)
                elif self.current_wave == 3:
                    pygame.time.set_timer(self.enemy_timer, 450)

            else:
                self.end_game("WIN")

    def draw_text(self, text, font, color, surface, x, y):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        surface.blit(text_obj, text_rect)

    def end_game(self, result):
        self.game_result = result
        self.current_state = "SUMMARY"
        
        self.data["coins"] += self.session_coins
        self.save_data()

    def draw_summary(self):
        self.virtual_surface.fill((10, 10, 20)) # رنگ پس‌زمینه تیره
        
        title = ""
        color = (255, 255, 255)
        if self.game_result == "WIN":
            title, color = "MISSION ACCOMPLISHED", (0, 255, 100)
        elif self.game_result == "LOSE":
            title, color = "SHIP DESTROYED", (255, 50, 50)
        else:
            title, color = "MISSION ABORTED", (255, 200, 0)

        self.draw_text(title, self.font_medium, color, self.virtual_surface, 640, 150)
        self.draw_text(f"Total Kills: {self.kills}", self.font_small, (255, 255, 255), self.virtual_surface, 640, 300)
        self.draw_text(f"Coins Earned: {self.session_coins}", self.font_small, (255, 215, 0), self.virtual_surface, 640, 370)
        self.draw_text(f"Current Wave: {self.current_wave}", self.font_small, (200, 200, 200), self.virtual_surface, 640, 440)
        
        self.draw_text("Press [Enter] for return to Menu", self.font_small, (150, 150, 150), self.virtual_surface, 640, 600)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_KP_ENTER]:
            self.current_state = "MENU"

class Button:
    clicked = False
    def __init__(self, x, y, image, scale):
        self.original_image = image
        self.scale = scale
        self.x = x
        self.y = y
        
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.smoothscale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect(center=(x, y))
        self.clicked = False
        
        self.target_scale = scale
        self.current_scale = scale
        self.speed = 0.1

    def draw(self, surface, mouse_pos):
        action = False
        
        if self.rect.collidepoint(mouse_pos):
            # hover
            self.target_scale = self.scale * 1.1

            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            
            if pygame.mouse.get_pressed()[0] == 1 and not Button.clicked:
                Button.clicked = True
                action = True
        else:
            self.target_scale = self.scale
            
        if pygame.mouse.get_pressed()[0] == 0:
            Button.clicked = False

        self.current_scale += (self.target_scale - self.current_scale) * self.speed
        
        self.update_image(self.current_scale)
        
        surface.blit(self.image, self.rect)
        return action

    def update_image(self, current_scale):
        width = int(self.original_image.get_width())
        height = int(self.original_image.get_height())
        self.image = pygame.transform.smoothscale(self.original_image, 
                                                 (int(width * current_scale), int(height * current_scale)))
        self.rect = self.image.get_rect(center=(self.x, self.y))

class Background:
    def __init__(self, image, speed):
        self.image = image
        self.speed = speed
        self.y1 = 0
        self.y2 = -720
        
    def update(self):
        self.y1 += self.speed
        self.y2 += self.speed
        
        if self.y1 >= 720:
            self.y1 = -720
            
        if self.y2 >= 720:
            self.y2 = -720
    
    def draw(self, surface):
        surface.blit(self.image, (0, self.y1))
        surface.blit(self.image, (0, self.y2))
    
class Player(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos, hp):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(center = (pos[0], 720 - 100))
        
        self.target_x = pos[0]
        self.speed = 12
        self.lerp_factor = 0.1

        self.can_shoot = True
        self.shoot_time = 0
        self.cooldown = 400

        self.health = hp
    
    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.target_x += self.speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.target_x -= self.speed
            
        self.target_x = max(60, min(self.target_x, 1220))

    def update(self):
        self.input()
        new_x = self.rect.centerx + (self.target_x - self.rect.centerx) * self.lerp_factor
        self.rect.centerx = new_x
        self.check_cooldown()
    
    def check_cooldown(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.cooldown:
                self.can_shoot = True

    def shoot(self, bullet_group, bullet_img, bullet_type):
        
        if bullet_type == "xx1":
            Bullet(bullet_group, bullet_img, self.rect.midtop)
            
        if bullet_type == "xx2":
            Bullet(bullet_group, bullet_img, self.rect.topleft)
            Bullet(bullet_group, bullet_img, self.rect.topright)
            
        if bullet_type == "xx3":
            Bullet(bullet_group, bullet_img, self.rect.topleft)
            Bullet(bullet_group, bullet_img, self.rect.topright)
            Bullet(bullet_group, bullet_img, self.rect.midtop)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, group, image, pos):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.speed = -15
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, group, enemy_img, pos, health):
        super().__init__(group)
        self.image = enemy_img
        self.rect = self.image.get_rect(center=pos)
        self.health = health
        self.dir_y = 1
        self.dir_x = 1

        self.speed = 4 if health == 1 else 1
        
        self.shoot_cooldown = 1500 if health == 1 else 1000
        self.last_shot = pygame.time.get_ticks()
        
        self.is_boss = True if health != 1 else False
        
    def update(self):
        self.rect.y += (self.speed * self.dir_y)
        
        if self.rect.y > 420:
            self.rect.y = 420
            self.dir_y = -1

        elif self.rect.y < 40:
                    self.dir_y = 1

        if self.health != 1:
            self.rect.x += (self.speed * self.dir_x)
            
            if self.rect.right > 1200: 
                self.rect.right = 1200
                self.dir_x = -1
                
            elif self.rect.left < 80:
                self.rect.left = 80
                self.dir_x = 1
    
    def shoot(self, bullet_groups, bullet_img):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_shot >= self.shoot_cooldown:
            if self.health == 1:
                if random.random() < 0.2:
                    from __main__ import EnemyBullet
                    EnemyBullet(bullet_groups, bullet_img, self.rect.midbottom)
            else:
                from __main__ import EnemyBullet
                EnemyBullet(bullet_groups, bullet_img, self.rect.midbottom)
                game.is_boss = True
            
            self.last_shot = current_time

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(center = pos)
        self.speed = 7

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 720:
            self.kill()

class SimpleExplosion(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.timer = pygame.time.get_ticks()
    
    def update(self):
        if pygame.time.get_ticks() - self.timer > 100:
            self.kill()
            
if __name__ == "__main__":
    game = Game()
    game.run()