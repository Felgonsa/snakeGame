import pygame
import random
from collections import namedtuple
from enum import Enum # Usaremos Enum para direções, fica mais legível

pygame.init()

# CORREÇÃO 1: Typo na importação
from collections import namedtuple

# Enum para as direções
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')
font = pygame.font.SysFont("arial", 25)

# Cores e Constantes
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
square_size = 25
speed = 800

class SnakeGameAI:  
    def __init__(self, w= 1200, h=600, headless=False):
        self.w = w
        self.h = h
        self.game_area_w = 800
        self.headless = headless
        
        if not self.headless:
            pygame.display.set_caption("Snake Game AI")
            self.screen = pygame.display.set_mode((self.w, self.h))
            
        
        self.screen = pygame.display.set_mode((self.w, self.h))
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        # Adicionamos a direção ao estado do jogo
        self.direction = Direction.RIGHT
        
        # CORREÇÃO 2: Criando o Point com parênteses ()
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                    Point(self.head.x - square_size, self.head.y),
                    Point(self.head.x - (2 * square_size), self.head.y)]
                    
        self.score = 0
        self.food = None
        self._generate_food()
        self.frame_iteration = 0
            
    def _generate_food(self):
        x = round(random.randrange(0, (self.game_area_w - square_size) // square_size) * square_size)
        y = round(random.randrange(0, (self.h - square_size) // square_size) * square_size)
        self.food = Point(x, y)
        if self.food in self.snake:
            self._generate_food()

    def draw_ui(self, agent, record_score):
        
        if not self.headless:
            self.screen.fill(black)
       
        
        # CORREÇÃO 3: Lógica de desenho corrigida
        for pt in self.snake:
            pygame.draw.rect(self.screen, white, pygame.Rect(pt.x, pt.y, square_size, square_size))
        
        pygame.draw.rect(self.screen, green, [self.food.x, self.food.y, square_size, square_size])
        
        text = font.render(f"Pontuação: {self.score}", True, blue)
        self.screen.blit(text, [1, 1])
    
        # NOVO: Desenha o painel lateral
        
        panel_x_start = self.game_area_w
        pygame.draw.rect(self.screen, (50, 50, 50), [panel_x_start, 0, self.w - panel_x_start, self.h])
        
        
        info = {
            "Jogo Nº": agent.n_games,
            "Pontuação Atual": self.score,
            "Recorde": record_score,
            "Epsilon": f"{agent.epsilon:.4f}"
            }
        y_offset = 20
        for key, value in info.items():
            text = font.render(f"{key}: {value}", True, white)
            self.screen.blit(text, [panel_x_start + 20, y_offset])
            y_offset += 40
            
        pygame.display.flip()
            
    def _move(self, action):
        # As ações da IA são relativas: [reto, direita, esquerda]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if action == [1, 0, 0]: # Reto
            new_dir = clock_wise[idx] 
        elif action == [0, 1, 0]: # Virar à Direita
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else: # [0, 0, 1] Virar à Esquerda
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]
        
        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += square_size
        elif self.direction == Direction.LEFT:
            x -= square_size
        elif self.direction == Direction.DOWN:
            y += square_size
        elif self.direction == Direction.UP:
            y -= square_size
            
        self.head = Point(x, y)
        
    def play_step(self, action, agent, record_score):
        self.frame_iteration += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   
                pygame.quit()
                quit()   
                
        # 1. Mover a cobra com base na ação
        self._move(action)
        self.snake.insert(0, self.head)
            
        reward = 0
        game_over = False
            
        if self.frame_iteration > 100 * len(self.snake):
            reward = -10
            game_over = True
            return reward, game_over, self.score    
        
        if self.is_collision():
            reward = -10
            game_over = True
            return reward, game_over, self.score
                
        if self.head == self.food:
            self.score += 1 
            reward = 10
            self._generate_food()
        else:
            self.snake.pop()
                
        self.draw_ui(agent, record_score)
        self.clock.tick(speed)
            
        return reward, game_over, self.score
            
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
            
        if pt.x > self.game_area_w - square_size or pt.x < 0 or pt.y > self.h - square_size or pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True
        return False

if __name__ == '__main__':
    DummyAgent = namedtuple('DummyAgent', ['n_games'])
    dummy_agent = DummyAgent(n_games=0)
    record = 0
    
    game = SnakeGameAI()
    
    while True:
        # CORREÇÃO: Definimos uma ação padrão no início de cada ciclo.
        # Se nenhuma tecla for pressionada, a cobra continua indo reto.
        action = [1, 0, 0] 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                # A ação padrão será sobrescrita se uma tecla for pressionada.
                if event.key == pygame.K_q: action = [0, 0, 1] # Esquerda
                elif event.key == pygame.K_e: action = [0, 1, 0] # Direita

        # Agora, a variável 'action' SEMPRE terá um valor quando esta linha for executada.
        reward, game_over, score = game.play_step(action, dummy_agent, record)
        
        if game_over:
            if score > record: record = score
            dummy_agent = DummyAgent(n_games=dummy_agent.n_games + 1)
            game.reset()