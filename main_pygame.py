# Example file showing a basic pygame "game loop"
import pygame
from game.game import Game
from game.piece import Piece, Player, Shape, Size
from utils.heuristics import evaluate_board

import threading

from players.minimaxPlayer import MinimaxPlayer, Strategy


# pygame setup
pygame.init()

width = 1000
height = 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Alapo')
cur_state = "MENU" # MENU, MODE, PLAYING, GAME_OVER, CREDITS
game_mode = 0 # 0: PVP, 1: P vs AI, 2: AI vs AI  
clock = pygame.time.Clock()
fps = 30

#fonts
font = pygame.font.SysFont(None, 80)
btn_font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 30)
title_font = pygame.font.SysFont(None, 120)
winner_txt = ""

# buttons
menu_btn = pygame.Rect(width//2 - 100, height//2 + 50, 200, 60)
quit_btn = pygame.Rect(width//2 - 100, 450, 200, 60)
back_btn = pygame.Rect(20, 20, 100, 40)
credits_btn = pygame.Rect(width - 150, height - 80, 130, 50)

play_btn = pygame.Rect(width//2 - 100, 350, 200, 60)
mode_2p_btn = pygame.Rect(width//2 - 150, 250, 300, 60)
mode_1p_btn = pygame.Rect(width//2 - 150, 350, 300, 60)
mode_ai_btn = pygame.Rect(width//2 - 150, 450, 300, 60)

# initialize game and states
alapo = Game()
select_piece = None # coords of a clicked piece
valid_moves = [] # coords of moves selected piece can make
last_move_pos = None # coords of last moved piece

depth = 5
strat = Strategy.IDSALLTABLES
ai_player = MinimaxPlayer("HumanDestroyer9000", evaluate_board, depth, strat)

# images:
menu_img = pygame.image.load("assets/background.jpg").convert()
menu_img = pygame.transform.scale(menu_img, (width, height))

title_img = pygame.image.load("assets/ALAPO.png").convert()
title_img.set_colorkey(title_img.get_at((0,0))) # removes background around title
title_img = pygame.transform.smoothscale(title_img, (500, 500))

# draw board:
def draw_board():
     for row in range(6):
        for col in range(6):
            x = 200 + (col * 100)
            y = 100 + (row * 100)
            color = (145, 190, 218) if (row + col) % 2 == 0 else (241, 231, 221)
            pygame.draw.rect(screen, color, [x, y, 100, 100])

# draw pieces:
def draw_pieces(game_instance):
    
    if last_move_pos is not None:
        lx, ly = last_move_pos
        last_x = 200 + (lx*100)
        last_y = 100 + (ly*100)
        highlight_color = (75, 130, 148) if (ly + lx) % 2 == 0 else (161, 151, 141)
        pygame.draw.rect(screen, highlight_color, [last_x, last_y, 100, 100])
    
    for y in range(game_instance.board.size):
        for x in range(game_instance.board.size):
            piece = game_instance.board.get_piece(x, y)
            
            if piece is None:
                continue
            
            # place piece in the center of a square:
            pixel_x = 200 + (x*100) + 50
            pixel_y = 100 + (y*100) + 50

            # piece color and size:
            base_color = 'white' if piece.owner == Player.WHITE else 'black'
            if select_piece == (x, y):
                color = pygame.Color('yellow') if piece.owner == Player.WHITE else pygame.Color(50, 50, 200)
            else:
                color = base_color

            dim = 15 if piece.size == Size.SMALL else 25

            # draw shape:
            if piece.shape == Shape.CIRCLE:
                pygame.draw.circle(screen, color, (pixel_x, pixel_y), dim)
            
            elif piece.shape == Shape.SQUARE:
                pygame.draw.rect(screen, color, (pixel_x - dim, pixel_y - dim, dim*2, dim*2))
             
            elif piece.shape == Shape.TRIANGLE:
                vertices = [
                    (pixel_x, pixel_y - dim), # top 
                    (pixel_x - dim, pixel_y + dim), # bottom left
                    (pixel_x + dim, pixel_y + dim) # bottom right
                ]

                pygame.draw.polygon(screen, color, vertices)

# draw moves a piece can make:
def draw_moves():
    for move in valid_moves:
        x = 200+(move.fx*100)+50
        y = 100+(move.fy*100)+50
        pygame.draw.circle(screen, 'red', (x, y), 10)

def reset_game():
    global alapo, select_piece, valid_moves, last_move_pos
    alapo = Game()
    select_piece = None
    valid_moves = []
    last_move_pos = None

def check_for_winner():
    global cur_state, winner_txt
    winner = alapo.board.check_winner()
    if winner is not None:
        cur_state = "GAME_OVER"
        winner_name = "White" if winner == Player.WHITE else "Black"
        winner_txt = f"{winner_name} Won!"
        return True
    return False

# main pygame loop:
running = True
ai_thinking = False
ai_move = None
while running:
    clock.tick(fps)
    cur_player = alapo.board.get_cur_player()

    if cur_state == "PLAYING":
        is_ai_turn = False # Meto falso por default
        if game_mode == 1 and cur_player == Player.BLACK:
            is_ai_turn = True # Human Vs. AI, assumo player branco AI preto
        elif game_mode == 2:
            is_ai_turn = True # Sempre AI lmao

        if is_ai_turn:
            if not ai_thinking:
                def fetch_ai_move(current_game):
                    global ai_move, ai_thinking
                    ai_move = ai_player.get_player_move(current_game)
                    ai_thinking = False

                ai_thinking = True
                thread = threading.Thread(target=fetch_ai_move, args=(alapo,))
                thread.daemon = True # Thread dies if the main program closes
                thread.start()

            if ai_move is not None:
                alapo.board.move_piece(ai_move)
                last_move_pos = (ai_move.fx, ai_move.fy)
                check_for_winner()
                ai_move = None # Clear the move for the next turn

    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # mouse clicks:    
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx = event.pos[0] 
            my = event.pos[1] 

            # back button:
            if back_btn.collidepoint((mx, my)):
                cur_state = "MENU"
                reset_game()
                continue
            
            # menu screen:
            if cur_state == "MENU":
                if play_btn.collidepoint((mx, my)):
                    cur_state = "MODE"
                elif quit_btn.collidepoint((mx, my)):
                    running = False
                elif credits_btn.collidepoint((mx, my)):
                    cur_state = "CREDITS"

            # mode select screen:
            elif cur_state == "MODE":
                if mode_2p_btn.collidepoint((mx, my)):
                    game_mode = 0
                    reset_game()
                    cur_state = "PLAYING"

                elif mode_1p_btn.collidepoint((mx, my)):
                    game_mode = 1
                    reset_game()
                    cur_state = "PLAYING"

                elif mode_ai_btn.collidepoint((mx, my)):
                    game_mode = 2
                    reset_game()
                    cur_state = "PLAYING"

            elif cur_state == "CREDITS":
                if back_btn.collidepoint((mx, my)):
                    cur_state = "MENU"
            
            # game over screen:
            elif cur_state == "GAME_OVER":
                if menu_btn.collidepoint((mx, my)):
                    cur_state = "MENU"
                    reset_game()

            # playing screen (board):
            elif cur_state == "PLAYING":
                x = (event.pos[0] - 200) // 100
                y = (event.pos[1] - 100)// 100

                #check if click is within the board:
                if 0 <= x < 6 and 0 <= y <6:
                    move_exec = False
                    for move in valid_moves:
                        if move.fx == x and move.fy == y:
                            alapo.board.move_piece(move)
                            last_move_pos = (move.fx, move.fy)

                            # check if win:
                            check_for_winner()

                            # reset selection
                            select_piece = None
                            valid_moves = []
                            move_exec = True
                            break
                        
                    if not move_exec:
                        piece = alapo.board.get_piece(x, y)
                        cur_player = alapo.board.get_cur_player()

                        # de-select current piece:
                        if select_piece == (x, y):
                            select_piece = None
                            valid_moves = []
                            last_move_pos = None

                        # select another piece:
                        elif piece and piece.owner == cur_player:
                            select_piece = (x, y)
                            valid_moves = piece.get_moves(alapo.board, x, y)
                            last_move_pos = None

                        # clear select:    
                        else:
                            select_piece = None
                            valid_moves = []



    # rendering
    screen.blit(menu_img, (0,0))
    shadow_offset = 5
    
    if cur_state != "MENU":
        pygame.draw.rect(screen, 'dark gray', back_btn, border_radius=5)
        back_txt = small_font.render("Back", True, 'black')
        
        screen.blit(back_txt, (back_btn.centerx - back_txt.get_width()//2, back_btn.centery - back_txt.get_height()//2))

    if cur_state == "MENU":
        # title = title_font.render("ALAPO", True, 'black')
        screen.blit(title_img, (width//2 - title_img.get_width()//2, -50))


        # buttons:
        pygame.draw.rect(screen, (20, 50, 20), (play_btn.x + shadow_offset, play_btn.y + shadow_offset, play_btn.width, play_btn.height))
        pygame.draw.rect(screen, 'green', play_btn)

        pygame.draw.rect(screen, (50, 20, 20), (quit_btn.x + shadow_offset, quit_btn.y + shadow_offset, quit_btn.width, quit_btn.height))
        pygame.draw.rect(screen, 'red', quit_btn)

        pygame.draw.rect(screen, (50, 50, 50), (credits_btn.x + 3, credits_btn.y + 3, credits_btn.width, credits_btn.height))
        pygame.draw.rect(screen, 'gray', credits_btn)

        play_txt = btn_font.render("Play", True, 'white')
        quit_txt = btn_font.render("Quit", True, 'white')
        cred_txt = small_font.render("Credits", True, 'white')
        screen.blit(play_txt, (play_btn.centerx - play_txt.get_width()//2, play_btn.centery - play_txt.get_height()//2))
        screen.blit(quit_txt, (quit_btn.centerx - quit_txt.get_width()//2, quit_btn.centery - quit_txt.get_height()//2))
        screen.blit(cred_txt, (credits_btn.centerx - cred_txt.get_width()//2, credits_btn.centery - cred_txt.get_height()//2))

    elif cur_state == "CREDITS":

        title_y = 200
        line_spacing = 80
        
        header = font.render("This Project was made by:", True, 'black')
        p1 = btn_font.render("Gabriel Cardoso Mota - up202306287", True, 'black')
        p2 = btn_font.render("Sofia Sousa Furtado - up202305878", True, 'black')
        p3 = btn_font.render("Tiago Alexandre de Boaventura Nunes - up202304047", True, 'black')

        screen.blit(header, (width//2 - header.get_width()//2, title_y))
        screen.blit(p1, (width//2 - p1.get_width()//2, title_y + 150))
        screen.blit(p2, (width//2 - p2.get_width()//2, title_y + 150 + line_spacing))
        screen.blit(p3, (width//2 - p3.get_width()//2, title_y + 150 + line_spacing * 2))

    elif cur_state == "MODE":
        title = font.render("SELECT MODE", True, 'black')
        screen.blit(title, (width//2 - title.get_width()//2, 120))
        
        pygame.draw.rect(screen, (20, 50, 20), (mode_2p_btn.x + shadow_offset, mode_2p_btn.y + shadow_offset, mode_2p_btn.width, mode_2p_btn.height))
        pygame.draw.rect(screen, 'dark blue', mode_2p_btn)

        pygame.draw.rect(screen, (20, 50, 20), (mode_1p_btn.x + shadow_offset, mode_1p_btn.y + shadow_offset, mode_1p_btn.width, mode_1p_btn.height))
        pygame.draw.rect(screen, 'dark blue', mode_1p_btn)

        pygame.draw.rect(screen, (20, 50, 20), (mode_ai_btn.x + shadow_offset, mode_ai_btn.y + shadow_offset, mode_ai_btn.width, mode_ai_btn.height))
        pygame.draw.rect(screen, 'dark blue', mode_ai_btn)

        txt_2p = btn_font.render("Human vs Human", True, 'white')
        txt_1p = btn_font.render("Human vs AI", True, 'white')
        txt_ai = btn_font.render("AI vs AI", True, 'white')

        screen.blit(txt_2p, (mode_2p_btn.centerx - txt_2p.get_width()//2, mode_2p_btn.centery - txt_2p.get_height()//2))
        screen.blit(txt_1p, (mode_1p_btn.centerx - txt_1p.get_width()//2, mode_1p_btn.centery - txt_1p.get_height()//2))
        screen.blit(txt_ai, (mode_ai_btn.centerx - txt_ai.get_width()//2, mode_ai_btn.centery - txt_ai.get_height()//2))

    elif cur_state == "PLAYING" or cur_state == "GAME_OVER":
        draw_board()
        draw_pieces(alapo)
        draw_moves()

        if cur_state == "GAME_OVER":
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            text_surface = font.render(winner_txt, True, 'white')
            text_rect = text_surface.get_rect(center=(width//2, height//2 - 50))
            screen.blit(text_surface, text_rect)

            pygame.draw.rect(screen, 'dodgerblue', menu_btn)
            menu_txt = btn_font.render("Main Menu", True, 'white')
            screen.blit(menu_txt, (menu_btn.centerx - menu_txt.get_width()//2, menu_btn.centery - menu_txt.get_height()//2))

    # flip() the display to put work on screen
    pygame.display.flip()
pygame.quit()