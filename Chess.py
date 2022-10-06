import pygame, sys
import requests


class Piece:
    def __init__(self, tile, type):
        self.tile = tile
        self.type = type
        self.selected = False
        self.held = False
        self.possible_moves = None

    def __repr__(self):
        return f"Piece(tile = {self.tile}, type = {self.type}, selected = {self.selected}, held = {self.held})"

    def drawOnBoard(self, screen, piece, side):
        screen.blit(piece, (self.tile[0] * side, self.tile[1] * side))

    def drawOnPosition(self, screen, piece, position, side):
        screen.blit(piece, (position[0] - side // 2, position[1] - side // 2))

    def select(self):
        self.selected = True

    def unselect(self):
        self.selected = False

    def canMoveTo(self, position):
        for pos in self.possible_moves:
            if pos[:2] == position:
                return True, pos
        return False, ()

    def moveTo(self, tile):
        self.tile = tile

    def captures(self, piece):
        return self.type.isupper() ^ piece.type.isupper()

class Tile:
    def __init__(self):
        self.piece = None
        self.som = True

class Board:
    COLORS = {
        "whiteTiles": pygame.Color("#DCDCDC"),
        "blackTiles": pygame.Color("#ABABAB")
    }

    def __init__(self, side):
        self.side = side
        self.pieces, self.board = self.getPositionFromFEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        self.images = {}
        try:
            with open("Pieces/SavedInfo", "r") as f:
                saved_side = int(f.read())
        except FileNotFoundError:
            saved_side = -1
        with open("Pieces/SavedInfo", "w") as f:
            f.write(str(self.side))
        piece_types = ("wp", "wr", "wn", "wb", "wq", "wk", "bp", "br", "bn", "bb", "bq", "bk")
        if saved_side != self.side:
            for piece in piece_types:
                img_data = requests.get(
                    f"https://images.chesscomfiles.com/chess-themes/pieces/glass/{self.side}/{piece}.png").content
                with open(f'Pieces/{piece}.png', 'wb') as handler:
                    handler.write(img_data)
        for piece in piece_types:
            key = piece[1] if piece[0] == "b" else piece[1].upper()
            self.images[key] = pygame.image.load(f"Pieces/{piece}.png")
        surf = pygame.Surface((side, side), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0, 0, 0, 26), (side / 2, side / 2), side / 5)
        self.images["hint"] = surf
        surf = pygame.Surface((side, side), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0, 0, 0, 26), (side / 2, side / 2), side / 2)
        pygame.draw.circle(surf, (0, 0, 0, 0), (side / 2, side / 2), side * 5 / 12)
        self.images["capture_hint"] = surf

    def getPositionFromFEN(self, position):
        pieces = []
        board = [[Tile() for _ in range(8)] for _ in range(8)]
        for y, row in enumerate(position.split("/")):
            x = 0
            for c in row:
                if c.isdigit():
                    x += int(c)
                else:
                    new_piece = Piece((x, y), c)
                    pieces.append(new_piece)
                    board[y][x].piece = new_piece
                    x += 1
        return pieces, board

    def select(self, piece):
        piece.select()
        piece.possible_moves = self.getPossibleMoves(piece)

    def unselect(self, piece):
        piece.unselect()

    def getPossibleMoves(self, piece):
        # Position = (x, y)
        possible_moves = []
        if piece.type in ("p", "P"):  # ============ Pawns ============
            direction = piece.type.isupper()
            tile = (piece.tile[0], piece.tile[1] + (-1 if direction else 1))
            for x in range(tile[0] - 1, tile[0] + 2, 2):
                aux_pos = (x, tile[1])
                if self.inBoard(aux_pos):
                    other_piece = self.getPieceFromTile(aux_pos)
                    if other_piece is not None:
                        is_capture = piece.captures(other_piece)
                        if is_capture:
                            possible_moves.append((x, tile[1], is_capture))
            if self.getPieceFromTile(tile) is None:
                possible_moves.append(tile + (False,))
            if piece.tile[1] == (6 if piece.type.isupper() else 1):
                tile = (tile[0], tile[1] + (-1 if direction else 1))
                if self.getPieceFromTile(tile) is None:
                    possible_moves.append(tile + (False,))
        elif piece.type in ("n", "N"):  # ============ Knight ============
            pass
        elif piece.type in ("b", "B"):  # ============ Bishop ============
            pass
        elif piece.type in ("r", "R"):  # ============ Rook ============
            pass
        elif piece.type in ("q", "Q"):  # ============ Queen ============
            pass
        elif piece.type in ("k", "K"):  # ============ King ============
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i != 0 or j != 0:
                        tile = (piece.tile[0] + i, piece.tile[1] + j)
                        if self.inBoard(tile):
                            other_piece = self.getPieceFromTile(tile)
                            if other_piece is None:
                                if not self.tileUnderAttack(piece, tile):
                                    possible_moves.append(tile + (False,))
                            elif piece.captures(other_piece):
                                possible_moves.append(tile + (True,))
        return possible_moves

    def tileUnderAttack(self, piece, square):
        for pc in self.pieces:
            if piece.captures(pc):
                return False
        return False

    def movePieceTo(self, piece, tile):
        self.getTile(piece.tile).piece = None
        piece.moveTo(tile)
        self.getTile(piece.tile).piece = piece
        self.unselect(piece)

    def capture(self, piece, position):
        self.pieces.remove(self.board[position[1]][position[0]].piece)
        self.movePieceTo(piece, position)

    def inBoard(self, pos):
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    def getPieceFromPosition(self, position):
        return self.getPieceFromTile(self.getTileFromPosition(position))

    def getPieceFromTile(self, tile):
        return self.getTile(tile).piece

    def getTileFromPosition(self, position):
        return position[0] // self.side, position[1] // self.side

    def getTile(self, tile):
        return self.board[tile[1]][tile[0]]

    def getImage(self, piece):
        return self.images[piece.type]

    def drawBoard(self, screen):
        for i in range(8):
            for j in range(8):
                aux_rect = pygame.Rect(i * self.side, j * self.side, self.side, self.side)
                pygame.draw.rect(screen,
                                 self.COLORS["whiteTiles"] if (i + j) % 2 == 0 else self.COLORS["blackTiles"],
                                 aux_rect)

    def drawPieces(self, screen):
        for piece in self.pieces:
            if not piece.held:
                piece.drawOnBoard(screen, self.getImage(piece), self.side)
            else:
                piece.drawOnPosition(screen, self.getImage(piece), pygame.mouse.get_pos(), self.side)
            if piece.selected:
                self.drawHints(screen, piece)

    def drawHints(self, screen, piece):
        for pos in piece.possible_moves:
            if pos[2]:
                screen.blit(self.images["capture_hint"], (pos[0] * self.side, pos[1] * self.side))
            else:
                screen.blit(self.images["hint"], (pos[0] * self.side, pos[1] * self.side))
    
    def draw(self, screen):
        self.drawBoard(screen)
        self.drawPieces(screen)

    def printBoard(self):
        for row in self.board:
            for tile in row:
                if tile.piece is None:
                    print(".", end=" ")
                else:
                    print(tile.piece.type, end=" ")
            print()

    def printPieces(self):
        for piece in self.pieces:
            print(piece)

def main():
    pygame.init()
    FPS = 60
    TILESIZE = 100
    SCREENSIZE = (TILESIZE * 8, TILESIZE * 8)
    screen = pygame.display.set_mode(SCREENSIZE)
    clock = pygame.time.Clock()

    board = Board(TILESIZE)
    holding_left_click = False
    selected_piece = None
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_p:
                    board.printBoard()
                    print("---------------")
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:  # Left Click
                    if selected_piece is not None:
                        board.unselect(selected_piece)
                    selected_piece = board.getPieceFromPosition(pygame.mouse.get_pos())
                    if selected_piece is not None:
                        board.select(selected_piece)
                    holding_left_click = True
            elif ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 1:
                    holding_left_click = False
                    if selected_piece is not None:
                        mouse_square = board.getTileFromPosition(pygame.mouse.get_pos())
                        can_move, pos = selected_piece.canMoveTo(mouse_square)
                        if can_move:
                            if pos[2]: # is_capture
                                board.capture(selected_piece, pos)
                            else: # just move
                                board.movePieceTo(selected_piece, mouse_square)

        screen.fill("black")
        if selected_piece is not None:
            if holding_left_click:
                selected_piece.held = True
            else:
                selected_piece.held = False

        board.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
