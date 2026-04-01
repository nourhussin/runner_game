import random
import pgzrun

WIDTH = 400
HEIGHT = 600
TITLE = "Runner Game"
LEFT_BOUNDARY = 40
RIGHT_BOUNDARY = WIDTH - 40

player = Actor("player", (WIDTH//2, HEIGHT - 40)) # Start and buttom middle
PLAYER_SPEED = 4
player_frames = ["player", "player_f"]  # Forward walking frames
current_frame = 0
frame_timer = 0
FRAME_DELAY = 8
hearts = 3
score = 0

enemies = []
OBSTACLE_HEIGHT = 30
obstacle_speed = 3
timer = 0 # To add obstacles

# -------------------- Menu --------------------
main_menu_options = ["Start", "Music", "Sounds", "Exit"]
game_over_options = ["Replay", "Main Menu"]
selected_index = 0
in_main_menu = True
in_game = False
in_game_over = False
music_on = True
sound_on = True


class Obstacle:
    def __init__(self):
        self.y = -OBSTACLE_HEIGHT
        self.speed = obstacle_speed
        self.gap_width = 80
        self.gap_x = random.randint(LEFT_BOUNDARY, RIGHT_BOUNDARY - self.gap_width)

        # Divide the obstacle into 2 rectangles to provide a gap
        self.left_rect = Rect((LEFT_BOUNDARY, self.y), (self.gap_x - LEFT_BOUNDARY, OBSTACLE_HEIGHT))
        self.right_rect = Rect((self.gap_x + self.gap_width, self.y), (RIGHT_BOUNDARY - (self.gap_x+self.gap_width), OBSTACLE_HEIGHT))

    def move(self):
        self.y += self.speed
        self.left_rect.y = self.y
        self.right_rect.y = self.y

    def draw(self):
        screen.draw.filled_rect(self.left_rect, "saddlebrown")
        screen.draw.filled_rect(self.right_rect, "saddlebrown")

class Monster:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = -OBSTACLE_HEIGHT
        self.mode = random.choice(["easy", "hard"])
        self.speed = 6 if self.mode == "easy" else 2
        self.dir_x = random.choice([-1, 1])

    def move(self):
        if self.mode == "easy":
            self.move_easy()
        else:
            self.move_hard()

    def move_easy(self):
        self.x += self.dir_x * self.speed
        if self.x <= LEFT_BOUNDARY or self.x >= RIGHT_BOUNDARY:
            self.dir_x *= -1
        self.y += obstacle_speed

    def move_hard(self):
        # Track player on X-axis
        if player.x > self.x:
            self.x += self.speed
        else:
            self.x -= self.speed

        self.y += obstacle_speed

        # Keep inside boundaries
        self.x = max(LEFT_BOUNDARY, min(self.x, RIGHT_BOUNDARY))

    def draw(self):
        color = "blue" if self.mode == "easy" else "red"
        screen.draw.filled_circle((self.x, self.y), 15, color)

def update():
    global hearts, in_main_menu, main_menu_options, in_game, in_game_over, game_over_options
    global obstacle_speed, timer, score, selected_index, current_frame, frame_timer

    if in_main_menu or in_game_over:
        return

    if keyboard.left and player.left > LEFT_BOUNDARY:
        player.x -= PLAYER_SPEED
        player.image = "player_left"
    elif keyboard.right and player.right < RIGHT_BOUNDARY:
        player.x += PLAYER_SPEED
        player.image = "player_right"
    else:
        frame_timer += 1
        if frame_timer >= FRAME_DELAY:
            frame_timer = 0
            current_frame = (current_frame + 1) % len(player_frames)
        player.image = player_frames[current_frame]

    timer += 1
    if timer > 80:  # every 80 frames
        timer = 0
        if random.random() < 0.7:
            enemies.append(Obstacle())   # 70% chance
        else:
            enemies.append(Monster())    # 30% chance
            if sound_on:
                sounds.monster.play()

    for obj in enemies[:]:
        obj.move()
         # Collision
        if isinstance(obj, Obstacle):
            if player.colliderect(obj.left_rect) or player.colliderect(obj.right_rect):
                hearts -= 1
                if sound_on:
                    sounds.hit.play()
                enemies.remove(obj)

        elif isinstance(obj, Monster):
            if player.collidepoint((obj.x, obj.y)):
                hearts -= 1
                if sound_on:
                    sounds.hit.play()
                enemies.remove(obj)

        if hearts <= 0:
            if sound_on:
                sounds.gameover.play()
            music.stop()
            in_game = False
            in_game_over = True
            selected_index = 0

        if obj.y > HEIGHT:
            enemies.remove(obj)
            score += 1
            obstacle_speed += 0.1
            if score % 10 == 0:
                if sound_on:
                    sounds.score.play()

def draw():
    screen.fill((237, 201, 175))  # sand color
    screen.draw.filled_rect(Rect((0,0),(LEFT_BOUNDARY, HEIGHT)), (139,69,19))   # brown
    screen.draw.filled_rect(Rect((RIGHT_BOUNDARY,0),(WIDTH-RIGHT_BOUNDARY, HEIGHT)), (139,69,19))
    
    if in_main_menu:
        draw_menu(main_menu_options)
        return
    if in_game_over:
        draw_menu(game_over_options)
        return
    
    player.draw()
    for obj in enemies:
        obj.draw()
    screen.draw.text(f"Score: {score}", (60,10), fontsize=30, color="brown")

    for i in range(hearts):
        screen.draw.text("O", (270+i*25,10), fontsize=30, color="red")

def draw_menu(options):
    for i, option in enumerate(options):
        y = 200 + i*40
        color = "yellow" if i == selected_index else "brown"
        if option == "Music":
            status = "ON" if music_on else "OFF"
            status_color = "green" if music_on else "red"
            screen.draw.text("Music:", (100, y), fontsize=30, color=color)
            screen.draw.text(status, (100 + 70, y), fontsize=30, color=status_color)

        elif option == "Sounds":
            status = "ON" if sound_on else "OFF"
            status_color = "green" if sound_on else "red"
            screen.draw.text("Sounds:", (100, y), fontsize=30, color=color)
            screen.draw.text(status, (100 + 90, y), fontsize=30, color=status_color)

        else:
            screen.draw.text(option, (100, y), fontsize=30, color=color)

def on_key_down(key):
    global selected_index, in_main_menu, in_game_over
    if in_main_menu or in_game_over:
        options = main_menu_options if in_main_menu else game_over_options
        if key == keys.UP:
            selected_index = (selected_index - 1) % len(options)
        elif key == keys.DOWN:
            selected_index = (selected_index + 1) % len(options)
        elif key == keys.SPACE:
            handle_selection(options)

def handle_selection(options):
    global in_main_menu, in_game, in_game_over, music_on, sound_on, selected_index
    choice = options[selected_index]
    if in_main_menu:
        if choice == "Start":
            start_game()
        elif choice == "Music":
            music_on = not music_on
        elif choice == "Sounds":
            sound_on = not sound_on
        elif choice == "Exit":
            quit()

    elif in_game_over:
        if choice == "Replay":
            start_game()
        elif choice == "Main Menu":
            in_game_over = False
            in_main_menu = True
    selected_index = 0

def start_game(index=None):
    global in_main_menu, in_game, in_game_over, score, hearts, obstacles, obstacle_speed, selected_index
    in_main_menu = False
    in_game = True
    in_game_over = False
    selected_index = 0
    score = 0
    hearts = 3
    obstacles = []
    obstacle_speed = 3
    player.x = WIDTH//2
    if music_on:
        music.play("music")

pgzrun.go()