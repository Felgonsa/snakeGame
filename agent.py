from game import SnakeGameAI, Direction, Point
from collections import deque
import random
import matplotlib.pyplot as plt
from IPython import display

def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Treinando...')
    plt.xlabel('Número de Jogos')
    plt.ylabel('Pontuação')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)


MAX_MEMORY = 100_000
BATCH_SIZE = 100

SQUARE_SIZE = 25

class Agent:
        
    def __init__(self):
            self.n_games = 0
            self.gamma = 0.9  # discount rate
            self.learning_rate = 0.002
            self.q_table = {}
            self.memory = deque(maxlen=MAX_MEMORY) 
            
            
            #parametros de treinamento
            self.epsilon = 1.0
            self.epsilon_decay = 0.995
            self.epsilon_min = 0.01
            
        
    def get_state(self, game):
            head = game.snake[0]
            point_left = Point(head.x - SQUARE_SIZE, head.y)
            point_right = Point(head.x + SQUARE_SIZE, head.y)
            point_up = Point(head.x, head.y - SQUARE_SIZE)
            point_down = Point(head.x, head.y + SQUARE_SIZE)
            
            dir_left = game.direction == Direction.LEFT
            dir_right = game.direction == Direction.RIGHT
            dir_up = game.direction == Direction.UP 
            dir_down = game.direction == Direction.DOWN
            
            state = (
                #perigo em frente
                (dir_right and game.is_collision(point_right)) or
                (dir_left and game.is_collision(point_left)) or
                (dir_up and game.is_collision(point_up)) or
                (dir_down and game.is_collision(point_down)),
                #perigo a direita
                (dir_up and game.is_collision(point_right)) or
                (dir_down and game.is_collision(point_left)) or             
                (dir_left and game.is_collision(point_up)) or
                (dir_right and game.is_collision(point_down)),
                #perigo a esquerda
                (dir_down and game.is_collision(point_right)) or
                (dir_up and game.is_collision(point_left)) or       
                (dir_right and game.is_collision(point_up)) or
                (dir_left and game.is_collision(point_down)),
                
                #direção da cobra
                dir_left,  
                dir_right,
                dir_up,     
                dir_down,
                
                #posição da comida
                game.food.x < head.x,  # comida à esquerda
                game.food.x > head.x,  # comida à direita
                game.food.y < head.y,  # comida acima
                game.food.y > head.y   # comida abaixo
            )
                
                # Convertemos para tupla de inteiros para usar como chave do dicionário
            return tuple(int(i) for i in state)
                

    def get_action(self, state):
   
    
        final_move = [0, 0, 0]  # [reto, direita, esquerda]

        # Garante que o estado existe na tabela
        if state not in self.q_table:
            self.q_table[state] = [0, 0, 0]

        # CORREÇÃO LÓGICA #2: Usando randint, que corresponde ao seu Epsilon inteiro.
        if random.random() < self.epsilon:
            # Exploração: movimento aleatório
            move_index = random.randint(0, 2)
        else:
            # Explotação: pega a melhor ação da tabela
            q_values = self.q_table[state]
            move_index = q_values.index(max(q_values))
    
        # CORREÇÃO LÓGICA #1: Estas linhas agora estão FORA do if/else,
        # garantindo que sempre serão executadas.
        final_move[move_index] = 1
        return final_move
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # Pega um lote da memória
        else:
            mini_sample = self.memory
        
        for state, action, reward, next_state, done in mini_sample:
            self.train_short_memory(state, action, reward, next_state, done)
        
    def train_short_memory(self, state, action, reward, next_state, done):
            # pega o Q-valores atuais do estado
            action_index = action.index(1)
            old_q = self.q_table.get(state, [0, 0, 0])[action_index]
            
            if next_state not in self.q_table:
                # Se nunca vimos esse próximo estado, inicializamos seus Q-valores com 0
                self.q_table[next_state] = [0, 0, 0]
            max_future_q = max(self.q_table.get(next_state, [0, 0, 0]))
            
            
            if  done:
                # Se o jogo acabou, não há futuro Q
                new_q = reward
            else:
                # Atualiza o Q-valor com a fórmula de Bellman
                new_q = old_q + self.learning_rate * (reward + self.gamma * max_future_q - old_q)
            self.q_table[state][action_index] = new_q
        

if __name__ == '__main__':
    # --- CONFIGURAÇÃO INICIAL ---
    NUM_AGENTS = 5  # Defina quantos robôs você quer treinando ao mesmo tempo
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    
    # --- INSTANCIAÇÃO ---
    # Apenas UM agente (o cérebro)
    agent = Agent()
    
    # Uma lista de jogos (os "corpos"), onde só o primeiro é visível
    games = [SnakeGameAI(headless=(i != 0)) for i in range(NUM_AGENTS)]
    
    # Criamos uma lista para guardar o estado de cada jogo
    states_old = [None] * NUM_AGENTS

    # --- LAÇO DE TREINO PRINCIPAL ---
    while True:
        # Itera sobre cada um dos nossos jogos/ambientes
        for i, game in enumerate(games):
            
            # 1. Obter o estado atual (se for um novo jogo, reseta o estado)
            if states_old[i] is None:
                states_old[i] = agent.get_state(game)

            state_old = states_old[i]
            
            # 2. Obter a ação do cérebro compartilhado
            final_move = agent.get_action(state_old)
            
            # 3. Executar o passo no jogo específico
            reward, done, score = game.play_step(final_move, agent, record)
            
            # 4. Obter o novo estado
            state_new = agent.get_state(game)
            
            # 5. Treinar a memória curta (o cérebro aprende com a experiência deste corpo)
            agent.train_short_memory(state_old, final_move, reward, state_new, done)
            
            # 6. Guardar na memória longa compartilhada
            agent.remember(state_old, final_move, reward, state_new, done)

            # Atualiza o estado para o próximo ciclo
            states_old[i] = state_new

            if done: # Se o jogo específico acabou
                # Reseta apenas aquele jogo
                game.reset()
                states_old[i] = None # Limpa o estado para que seja pego de novo
                agent.n_games += 1
                
                # Treina com a memória longa (replay)
                agent.train_long_memory()
                
                agent.epsilon = max(agent.epsilon_min, agent.epsilon * agent.epsilon_decay)
                
                if score > record:
                    record = score
                    # agent.save() -> Futuramente
                
                
                # Lógica de plotagem
                plot_scores.append(score)
                total_score += score
                mean_score = total_score / agent.n_games
                plot_mean_scores.append(mean_score)
                plot(plot_scores, plot_mean_scores)