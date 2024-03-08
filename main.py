#Import modules
import pygame # Pygame library for game development
import os # To interact with the operating system for file paths
import random # For generating random numbers, like enemy spawn locations
pygame.font.init() # Initialize font module

# Set the width and height of the game window
WIDTH, HEIGHT = 750, 750
# Create the game window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
# Set the title of the game window
pygame.display.set_caption("Space Shooter Tutorial")

# Load spaceship images from the assets folder
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Load player spaceship image
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Load laser images
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Load and scale the background image to fit the game window
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Laser class to manage laser behavior
class Laser:
    def __init__(self, x, y, img):
        self.x = x # X position of the laser
        self.y = y # Y position of the laser
        self.img = img # Laser image
        self.mask = pygame.mask.from_surface(self.img) # Collision mask
        
    # Draws the laser on the game window
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    # Moves the laser vertically by the velocity amount
    def move(self, vel):
        self.y += vel
        
    # Checks if the laser has moved off-screen
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    
    # Checks if the laser has collided with another object
    def collision(self, obj):
        return collide(obj, self)

# Ship base class for the player and enemies
class Ship:
    COOLDOWN = 10 # Cooldown period between shots

    def __init__(self, x, y, health=100):
        self.x = x # X position of the ship
        self.y = y # Y position of the ship
        self.health = health # Ship health
        self.ship_img = None # Ship image, to be defined in subclasses
        self.laser_img = None # Laser image, to be defined in subclasses
        self.lasers = [] # List of lasers shot by the ship
        self.cool_down_counter = 0 # Counter to manage shooting cooldown
        
    def draw(self, window):
        # Draw the ship and its lasers on the game window
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
            
    def move_lasers(self, vel, obj):
        # Move lasers and handle collisions with the specified object
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10 # Damage the object upon collision
                self.lasers.remove(laser)
            
    def cooldown(self):
        # Manage the cooldown counter for shooting
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        # Shoot a laser if the cooldown period has elapsed
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        # Return the width of the ship's image
        return self.ship_img.get_width()
    
    def get_height(self):
        # Return the height of the ship's image
        return self.ship_img.get_height()

# Define the Player class, inheriting from Ship, for the player-controlled spaceship        
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) # Create a mask for collision detection
        self.max_health = health # Max health for the health bar

    def move_lasers(self, vel, objs):
        # Override move_lasers to handle collisions with multiple objects (enemy ships)
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj) # Remove the enemy ship upon collision
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    def draw(self, window):
        # Override draw to include the health bar
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        # Draw the health bar above the player's ship
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))     

# Define the Enemy class, inheriting from Ship, for enemy spaceships
class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }
    
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color] # Assign ship and laser images based on color
        self.mask = pygame.mask.from_surface(self.ship_img) # Create a mask for collision detection
        
    # Move the enemy ship vertically down the screen
    def move(self, vel):
        self.y += vel
    
    # Override shoot to position the laser correctly relative to the enemy ship
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img) # Adjust the laser's starting position
            self.lasers.append(laser)
            self.cool_down_counter = 1

# Function to detect collision between two objects using masks for pixel-perfect collision      
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x # Calculate x offset
    offset_y = obj2.y - obj1.y # Calculate y offset
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None # Check for mask overlap, indicating a collision

# Main game function
def main():
    run = True
    FPS = 60 # Frames per second
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    
    enemies = []  # List to store enemies
    wave_length = 5  # Number of enemies per wave
    enemy_vel = 2  # Enemy movement speed

    player_vel = 10  # Player movement speed
    laser_vel = 20  # Laser movement speed

    player = Player(300, 630)  # Create a Player instance

    clock = pygame.time.Clock()  # Create a clock object to manage the game's frame rate

    lost = False  # Flag to indicate whether the player has lost
    lost_count = 0  # Counter to manage the lost screen display time

    # Function to redraw the game window
    def redraw_window():
        WIN.blit(BG, (0, 0))  # Draw the background
        # Draw lives and level information
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
    
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
    
        for enemy in enemies:
            enemy.draw(WIN)  # Draw each enemy

        player.draw(WIN)  # Draw the player        

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()  # Update the display

    while run:
        clock.tick(FPS)  # Cap the game's frame rate
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        
        if lost:
            if lost_count > FPS * 3:  # Display the lost screen for 3 seconds
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1  # Increment the level
            wave_length += 5  # Increase the number of enemies
            for i in range(wave_length):  # Spawn new enemies
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            
        keys = pygame.key.get_pressed()  # Get a dictionary of all keyboard key states
        # Move the player based on key inputs
        if keys[pygame.K_a] and player.x - player_vel > 0: # Move left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # Move right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # Move up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # Move down
            player.y += player_vel
        if keys[pygame.K_SPACE]:  # Shoot laser
            player.shoot()
            
        for enemy in enemies[:]:  # Loop through a copy of the enemies list to avoid modification issues
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
        
            if random.randrange(0, 2*60) == 1:  # Random chance for each enemy to shoot
                enemy.shoot()
        
            if collide(enemy, player):  # Check for collision with the player
                player.health -= 10  # Damage the player
                enemies.remove(enemy)  # Remove the enemy
            elif enemy.y + enemy.get_height() > HEIGHT:  # Remove the enemy if it moves off the screen
                lives -= 1 
                enemies.remove(enemy)
            
        player.move_lasers(-laser_vel, enemies)  # Move and handle collisions for the player's lasers

# Function to display the main menu
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 40)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350)) # Draw the title
        
        pygame.display.update() # Update the display               
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN: # Start the game on mouse click
                main()
        
    pygame.quit() # Quit the game
            
main_menu() # Start the game by calling the main_menu function