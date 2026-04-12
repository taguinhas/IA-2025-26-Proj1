#creation assisted by chatGPT

import random
from players.minimaxPlayer import MinimaxPlayer, Strategy
from utils.heuristics import evaluate_board, WEIGHTS, training_weights, adjusted_weights

from game.game import Game
from game.piece import Player

import json
import os
import multiprocessing
num_cores = multiprocessing.cpu_count()

def update_fitness(winner, white_idx, black_idx, fitness):
    if winner == Player.WHITE:
        fitness[white_idx] += 1
    elif winner == Player.BLACK:
        fitness[black_idx] += 1
    else:
        fitness[white_idx] += 0.5
        fitness[black_idx] += 0.5

def make_player(weights):
    return MinimaxPlayer(
        "AI",
        eval_func = make_eval(weights),
        depth=5,
        strategy=Strategy.IDSALLTABLES
    )

def inject_diversity(population, rate=0.2):
    for i in range(len(population)):
        if random.random() < rate:
            population[i] = mutate(population[i])
    return population

def mutate(weights):
    new = weights.copy()

    for k in new:
        change = random.uniform(-5, 5)
        if random.random() < 0.2:
            change = random.uniform(-40, 40)  # occasional big mutation
        new[k] += change

        # clamp so it doesn't explode
        new[k] = max(0, min(200, new[k]))

    return new

def make_eval(weights):
    def eval_fn(b, d):
        return evaluate_board(b, d, weights)
    return eval_fn

def play_match(weightsA, weightsB, max_moves=200):
    game = Game()

    playerA = make_player(weightsA)
    playerB = make_player(weightsB)

    move_count = 0
    seen = {}

    while True:
        board = game.board
        if board.check_winner() != None:
            return board.check_winner()
        
        if move_count >= max_moves:
            return None
        

        key = board.current_hash
        seen[key] = seen.get(key, 0) + 1
        if seen[key] >= 3:
            return None

        if board.get_cur_player() == Player.WHITE:
            move = playerA.get_player_move(game)
        else:
            move = playerB.get_player_move(game)

        if move is None:
            return Player.BLACK 

        board.move_piece(move)
        move_count += 1

def run_match_pair(idx_i, idx_j, weight_i, weight_j):
    w1 = play_match(weight_i, weight_j)
    w2 = play_match(weight_j, weight_i)
    return (idx_i, idx_j, w1, w2)

def tournament_step(population, matches_per_agent=3):
    mutants = [mutate(w) for w in population]
    full_pop = population + mutants 

    pop_size = len(population)
    total_size = len(full_pop)

    fitness = [0 for _ in range(total_size)]

    match_tasks = []
    for i in range(total_size):
        for _ in range(matches_per_agent):
            j = random.randrange(total_size)
            while j == i:
                j = random.randrange(total_size)
            if i != j:
                match_tasks.append((i, j, full_pop[i], full_pop[j]))

    # 3. Use a Pool to run them in parallel
    with multiprocessing.Pool(processes=num_cores -1) as pool:
        results = pool.starmap(run_match_pair, match_tasks)

    # 4. Process the results back into fitness scores
    for i, j, w1, w2 in results:
        # Game 1
        if w1 == Player.WHITE: fitness[i] += 1
        elif w1 == Player.BLACK: fitness[j] += 1
        else: fitness[i] += 0.5; fitness[j] += 0.5
        
        # Game 2
        if w2 == Player.WHITE: fitness[j] += 1
        elif w2 == Player.BLACK: fitness[i] += 1
        else: fitness[i] += 0.5; fitness[j] += 0.5

    # 4. Rank population
    ranked_indices = sorted(
        range(total_size), 
        key=lambda i: fitness[i],
        reverse=True)

    # 5. Select next generation (top N)
    new_population = [full_pop[i] for i in ranked_indices[:pop_size]]

    # 6. Get top 5 for logging
    top5 = [(full_pop[i], fitness[i]) for i in ranked_indices[:5]]

    return new_population, top5

def save_checkpoint(filename, gen, population, best):
    data = {
        "gen": gen,
        "population": population,
        "best": best
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_checkpoint(filename):
    if not os.path.exists(filename):
        return None

    with open(filename, "r") as f:
        return json.load(f)
    
def train(generations=20, pop_size=10, checkpoint_file="checkpoint"):
    saved = load_checkpoint(checkpoint_file + ".json")

    if saved:
        population = saved["population"]
        start_gen = saved["gen"] + 1
        best = saved["best"]
        print(f"Resuming from generation {start_gen}")
    else:
        population = [WEIGHTS.copy() for _ in range(pop_size)]
        start_gen = 0

    for gen in range(start_gen, generations):
        population, top5 = tournament_step(population)
        ELITE = max(2, pop_size // 4)
        elites = population[:ELITE]
        rest = inject_diversity(population[ELITE:])
        population = elites + rest

        best = population[0]

        print(f"\nGEN {gen}")
        print("Best weights:", best)

        with open("log.txt", "a") as f:
            f.write(f"\nGEN {gen}\n")
            for i, (w_dict, score) in enumerate(top5):
                f.write(f"  #{i+1} score={score} weights={w_dict}\n")

        this_checkpoint_file =  checkpoint_file + str(gen) + ".json"
        save_checkpoint(this_checkpoint_file, gen, population, best)
        
        
    return best

def build_depth5_population():
    elites = [
        {"Material": 196.97, "Safety": 36.63, "Position": 2.45, "Control": 3.60},
        {"Material": 179.10, "Safety": 28.35, "Position": 26.90, "Control": 5.42},
        {"Material": 200.00, "Safety": 55.66, "Position": 9.84, "Control": 13.70},
        {"Material": 195.93, "Safety": 115.62, "Position": 12.10, "Control": 32.82},
        {"Material": 100,"Safety": 40, "Position": 20, "Control": 10},
    ]
    return elites

if __name__ == "__main__":
    #train(1, 5,"checkpoints/final")
    train(20, 10)
    #print(run_match_pair(0, 1, adjusted_weights, training_weights))
    #(0, 1, <Player.BLACK: 1>, None)
    #print(run_match_pair(0, 1, adjusted_weights, WEIGHTS))
    #(0, 1, <Player.WHITE: 0>, None)
    #print(run_match_pair(0, 1, WEIGHTS, training_weights))
    #(0, 1, None, <Player.BLACK: 1>)
    #training_weights > adjusted_weights > WEIGHTS > training weights ?????   