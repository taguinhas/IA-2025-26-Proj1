import time
from dataclasses import dataclass
from copy import deepcopy

from game.game import Game
from players.minimaxPlayer import MinimaxPlayer, Strategy
from utils.heuristics import evaluate_board

@dataclass
class TestPosition:
    name: str
    game: Game

def get_test_positions():
    positions = []

    g1 = Game()
    positions.append(TestPosition("start", g1))

    g2 = Game()
    g2.load_board_from_file("boards/mid.txt")
    positions.append(TestPosition("mid1", g2))

    g3 = Game()
    g3.load_board_from_file("boards/tactical1.txt")
    positions.append(TestPosition("tactical1", g3))

    return positions

def make_player(weights_name):
    if weights_name == "ABPRUNING":
        return MinimaxPlayer("AI", evaluate_board, depth=6, strategy=Strategy.ABPRUNING)

    if weights_name == "ABTABLE":
        return MinimaxPlayer("AI", evaluate_board, depth=6, strategy=Strategy.ABTABLE)
    
    if weights_name == "REGULARIDS":
        return MinimaxPlayer("AI", evaluate_board, depth=6, strategy=Strategy.IDS)

    if weights_name == "tt_heavy":
        p = MinimaxPlayer("AI", evaluate_board, depth=6, strategy=Strategy.IDSALLTABLES)
        p.score_weights = {"TT": 30000, "CO": 10000, "CAP": 20000}
        return p

    if weights_name == "killer_heavy":
        p = MinimaxPlayer("AI", evaluate_board, depth=6, strategy=Strategy.IDSALLTABLES)
        p.score_weights = {"TT": 10000, "CO": 30000, "CAP": 20000}
        return p
    
    if weights_name == "cap_heavy":
        p = MinimaxPlayer("AI", evaluate_board, depth=6, strategy=Strategy.IDSALLTABLES)
        p.score_weights = {"TT": 20000, "CO": 10000, "CAP": 30000}
        return p

def run_benchmark(position: TestPosition, player: MinimaxPlayer):
    game = deepcopy(position.game)

    player.nodes = 0
    player.table_hits = 0
    player.cutoffs = 0

    start = time.time()
    move = player.get_player_move(game)
    end = time.time()

    return {
        "position": position.name,
        "nodes": player.nodes,
        "time": end - start,
        "tt_hits": player.table_hits,
        "cutoffs": player.cutoffs,
        "move": move
    }

def run_all():
    positions = get_test_positions()

    configs = ["ABPRUNING", "ABTABLE", "REGULARIDS", "tt_heavy", "killer_heavy", "cap_heavy"]

    results = []

    for pos in positions:
        for cfg in configs:
            player = make_player(cfg)
            result = run_benchmark(pos, player)
            result["config"] = cfg
            results.append(result)

    print_results(results)

def print_results(results):
    print("\n=== BENCHMARK RESULTS ===\n")

    for r in results:
        print(
            f"{r['position']:10} | {r['config']:12} | "
            f"Nodes: {r['nodes']:6} | "
            f"Time: {r['time']:.3f}s | "
            f"TT: {r['tt_hits']:5} | "
            f"Cutoffs: {r['cutoffs']:5}"
        )
    
run_all()