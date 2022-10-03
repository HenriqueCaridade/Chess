import pygame, sys
import requests

class Board:
    COLORS = {
        "whiteTiles": pygame.Color("#DCDCDC"),
        "blackTiles": pygame.Color("#ABABAB")
    }

    def __init__(self, side):
        self.side = side
        self.position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        self.pieces = {}
        try:
            with open("Pieces/SavedInfo", "r") as f:
                saved_side = int(f.read())
        except FileNotFoundError:
            saved_side = 0
        with open("Pieces/SavedInfo", "w") as f:
            f.write(str(self.side))
        pieces = ("wp", "wr", "wn", "wb", "wq", "wk", "bp", "br", "bn", "bb", "bq", "bk")
        if saved_side != self.side:
            for piece in pieces:
                img_data = requests.get(f"https://images.chesscomfiles.com/chess-themes/pieces/glass/{self.side}/{piece}.png").content
                with open(f'Pieces/{piece}.png', 'wb') as handler:
                    handler.write(img_data)
        for piece in pieces:
            key = piece[1] if piece[0] == "b" else piece[1].upper()
            self.pieces[key] = pygame.image.load(f"Pieces/{piece}.png")

    def drawBoard(self, screen):
        for i in range(8):
            for j in range(8):
                aux_rect = pygame.Rect(i * self.side, j * self.side, self.side, self.side)
                pygame.draw.rect(screen, self.COLORS["whiteTiles"] if (i + j) % 2 == 0 else self.COLORS["blackTiles"], aux_rect)

    def drawPieces(self, screen):
        for y, row in enumerate(self.position.split("/")):
            x = 0
            for c in row:
                if c.isdigit():
                    x += int(c)
                else:
                    screen.blit(self.pieces[c], (x * self.side, y * self.side))
                    x += 1

    def draw(self, screen):
        self.drawBoard(screen)
        self.drawPieces(screen)

def main():
    pygame.init()
    FPS = 60
    TILESIZE = 100
    SCREENSIZE = (TILESIZE * 8, TILESIZE * 8)
    screen = pygame.display.set_mode(SCREENSIZE)
    clock = pygame.time.Clock()

    board = Board(TILESIZE)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1: # Left Click
                    print(pygame.mouse.get_pos())
        screen.fill("black")

        board.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
