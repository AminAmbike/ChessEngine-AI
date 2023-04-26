#This is the main driver file. It will be responsible for handling user input and displaying the current GameState object.

import pygame as p
import ChessEngine
import ChessAI

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

'''
Initialize a global dictionary of images. Called only once in the main
'''
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bK', 'bp', 'bR', 'bN', 'bB', 'bR', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #Can now access an image by saying 'IMAGES['wp']

'''
The main driver. This will handle user input and updating graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    animate = False #flag variable for when we should animate a move
    loadImages()
    running = True
    sqSelected = () # No Square is selected, keep track of the last click of the user using a tuple (row, col)
    playerClicks = [] # Keeps track of the player clicks, two tuples [(6,4), (4,4)]
    gameOver = False
    playerOne = True #If a human is playing white, then this will be true. If an AI is playing, then False
    playerTwo = False #Same as above but for black
   
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn: 
                    location = p.mouse.get_pos() #(x,y) locatopn of the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col): #user clicked the same square twice
                        sqSelected = () #deselect
                        playerClicks = [] #clear player clicks
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected) #append for both 1st and 2nd clicks
                    if len(playerClicks) == 2: #after 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):  
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade=True
                                animate = True
                                sqSelected = () #reset user clicks
                                playerClicks = [] 
                        if not moveMade: 
                            playerClicks = [sqSelected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r: #reset the board when 'r' is pressed
                    gs= ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        #AI move finder logic
        if not gameOver and not humanTurn:
            AIMove = ChessAI.findBestMove(gs, validMoves) #AI uses greedy algorithm to find optimal move
            if AIMove is None:
                AIMove = ChessAI.findRandomMove(validMoves) #if AI unable to find a best move, it selects a random move
            gs.makeMove(AIMove)
            moveMade = True
            animate = True


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)    
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False


        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'CHECKMATE! Black Wins')
            else:
                drawText(screen, 'CHECKMATE! White Wins')
        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'STALEMATE!')

    
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Highlight square selected and moved for piece selected
'''
def highlightSquares(screen, gs, validMoves,sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparency value -> 0 transparent; 255 -> opaque
            s.fill(p.Color('purple'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('green'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))



   
'''
Responsible for all the graphics within a current game state. 
'''

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) #draw the squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) #draw pieces on top of those squares
    


'''
Draw the Squares on the board
'''

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE ))



'''
Draw the pieces on the board using current GameState.board
'''

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not empty
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    global colors
    coords = [] #list of coordinated that the animation will move through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 #frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = ((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)
    
def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Green'))
    screen.blit(textObject, textLocation.move(2, 2))



main()



