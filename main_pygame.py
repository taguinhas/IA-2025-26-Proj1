# Example file showing a basic pygame "game loop"
import pygame

# pygame setup
pygame.init()
width = 1000
height = 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Alapo')
clock = pygame.time.Clock()
fps = 30


# draw board:
def draw_board():
     for i in range(18):
        col = i%3
        row = i//3
        if row % 2 == 0:
            pygame.draw.rect(screen, 'light gray', 
            [600 - (col*200), row*100, 100, 100])
            pygame.draw.rect(screen, 'dark gray', 
            [700 - (col*200), row*100, 100, 100])
        else:
            pygame.draw.rect(screen, 'dark gray', 
            [600 - (col*200), row*100, 100, 100])
            pygame.draw.rect(screen, 'light gray', 
            [700 - (col*200), row*100, 100, 100])

# main pygame loop:
running = True
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill('gray')
    draw_board()

    # flip() the display to put your work on screen
    pygame.display.flip()
pygame.quit()