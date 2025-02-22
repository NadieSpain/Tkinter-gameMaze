import random as rn
from itertools import product
import tkinter as tk
from tkinter import messagebox


CHUNK_SIZE = 10 #Tamaño de los chunks
CHUNKS_per_SIDE = 2 #Número de chunks por lado + 1

#La cantidad de chunks en el laberinto será (CHUNKS_per_SIDE+1)**2
#El tamaño del laberinto será (2 * (CHUNK_SIZE * CHUNKS_per_SIDE) + 1) x (2 * (CHUNK_SIZE * CHUNKS_per_SIDE) + 1)
#El tamaño del laberinto no debe ser mayor a 50x50

CANVAS_SIZE = 500 #Tamaño del canvas
SQ = CANVAS_SIZE // CHUNK_SIZE #Tamaño de cada cuadrado en el canvas
COLORS = { 
    "empty": "white",
    "wall": "black",
    "player": "orange",
    "locator": "red",
    "ENTRY": "green",
    "EXIT": "blue"
}

def create_maze(m, n):
    # Inicializar el laberinto con paredes
    laberinto = [[1] * (2 * n + 1) for _ in range(2 * m + 1)]

    # Crear celdas vacías en las posiciones de los nodos
    for i, j in product(range(m), range(n)):
        laberinto[2 * i + 1][2 * j + 1] = 0

    # Algoritmo de Backtracking Iterativo
    def vecinos(i, j):
        return [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]

    stack = [(rn.randint(0, m - 1), rn.randint(0, n - 1))]
    visitados = set(stack)
    
    while stack:
        x, y = stack[-1]
        vecinos_lista = [(nx, ny) for nx, ny in vecinos(x, y) if 0 <= nx < m and 0 <= ny < n and (nx, ny) not in visitados]
        rn.shuffle(vecinos_lista)
        
        if vecinos_lista:
            nx, ny = vecinos_lista.pop()
            visitados.add((nx, ny))
            stack.append((nx, ny))
            
            laberinto[2 * x + 1 + nx - x][2 * y + 1 + ny - y] = 0
        else:
            stack.pop()

    return laberinto


class Player:
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y

    def action(self, command:str):

        moves = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0)
        }

        if command in moves:
            dx, dy = moves[command]
            nx, ny = self.x + dx, self.y + dy
            if self.game.maze[ny][nx] != 1:
                self.x, self.y = nx, ny

        elif command == "restart":
            self.game.reset_game()

        elif command == "loc":
            if (self.x, self.y) in self.game.locators:
                self.game.locators.remove((self.x, self.y))
            else:
                self.game.locators.append((self.x, self.y))

        self.game.draw_chunk()


class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Maze Game")
        self.canvas = tk.Canvas(self.root, background=COLORS["empty"], width=CANVAS_SIZE, height=CANVAS_SIZE)
        self.canvas.pack()
        self.maze = create_maze(CHUNK_SIZE*CHUNKS_per_SIDE, CHUNK_SIZE*CHUNKS_per_SIDE)
        self.player = Player(self, 1, 1)
        self.locators = []
        self.draw_chunk()

        key_bindings = {
            "<Up>": "up",
            "<Down>": "down",
            "<Left>": "left",
            "<Right>": "right",
            "<r>": "restart",
            "<c>": "loc"
        }
        for key, command in key_bindings.items():
            self.root.bind(key, lambda event, cmd=command: self.player.action(cmd))

    def draw_square(self, x, y, color, i=1):
        chunk_x = self.player.x // CHUNK_SIZE * CHUNK_SIZE#Posición del chunk en x
        chunk_y = self.player.y // CHUNK_SIZE * CHUNK_SIZE#Posición del chunk en y
        X_=(x - chunk_x) * SQ
        Y_=(y - chunk_y) * SQ
        margin = (SQ * (1 - i)) // 2 
                
        self.canvas.create_rectangle(X_+margin, Y_+margin, X_ + SQ-margin, Y_ + SQ-margin, fill=color, outline="gray")

    def draw_chunk(self):
        self.canvas.delete("all")
        chunk_x = self.player.x // CHUNK_SIZE * CHUNK_SIZE#Posición del chunk en x
        chunk_y = self.player.y // CHUNK_SIZE * CHUNK_SIZE#Posición del chunk en y

        #Dibuja el chunk paredes y espacios vacíos
        for i in range(chunk_y, min(chunk_y + CHUNK_SIZE, len(self.maze))):
            for j in range(chunk_x, min(chunk_x + CHUNK_SIZE, len(self.maze[0]))):
                color = COLORS["empty"] if self.maze[i][j] == 0 else COLORS["wall"]
                self.draw_square(j,i, color)

        #Dibuja las localizaciones
        for x, y in self.locators:
            if chunk_x <= x < chunk_x + CHUNK_SIZE and chunk_y <= y < chunk_y + CHUNK_SIZE:
                self.draw_square(x, y, COLORS["locator"],0.6)

        if 0 <= chunk_x < CHUNK_SIZE and 0 <= chunk_y < CHUNK_SIZE: #Comprueba si el jugador está en el chunk de la entrada
            self.draw_square(1,1, COLORS["ENTRY"])#Dibuja la entrada

        self.draw_square(self.player.x, self.player.y, COLORS["player"])#Dibuja al jugador

        exit_x = (len(self.maze[0]) - 2)
        exit_y = (len(self.maze) - 2)
        if 0 <= exit_x < CHUNK_SIZE * SQ and 0 <= exit_y < CHUNK_SIZE * SQ:#Comprueba si el jugador está en el chunk de la salida
            self.draw_square(exit_x, exit_y, COLORS["EXIT"])#Dibuja la salida

        if self.check_win():#Comprueba si el jugador ha ganado
            messagebox.showinfo("¡Felicidades!", "¡Has ganado!")
            self.reset_game()

    def check_win(self):
        return self.player.x == len(self.maze[0]) - 2 and self.player.y == len(self.maze) - 2

    def reset_game(self):
        self.locators=[]
        self.maze = create_maze(CHUNK_SIZE*CHUNKS_per_SIDE, CHUNK_SIZE*CHUNKS_per_SIDE)
        self.player.x, self.player.y = 1, 1
        self.draw_chunk()


if __name__ == "__main__":
    game = Game()
    game.root.mainloop()
