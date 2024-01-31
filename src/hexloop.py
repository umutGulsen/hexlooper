import pygame
import sys
from Game import Game
import numpy as np
import copy
import matplotlib.pyplot as plt
import seaborn as sns

board_config = {"height": 600,
                "width": 1000,
                "hex_radius": 10
                }

colors = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GRAY": (200, 200, 200),
    "GREEN": (0, 153, 51),
    "PLAYER_COLOR": (153, 0, 0),
    "HIGHLIGHT_COLOR": (255, 255, 0),  # Yellow for highlight
    "TRACK_COLOR": (102, 153, 255)
}


# import cProfile
# cProfile.run("g.run_game(fps=40960, display_interval=10000)", sort="tottime")


def genetic_algorithm(initial_mutation_chance: float, move_length: int, display_interval: int, generations: int, pop_size: int,
                      mutation_chance: float, train_fps: int = 4096):

    record = {}
    generation_scores = np.zeros((generations, pop_size))
    champion_scores = np.zeros(generations)
    champ_score = -1
    champ_moves = ((np.random.rand(move_length) * 6 + 1).astype(int))

    best_scores = []
    for gen in range(generations):
        print(f"Started Generation {gen}")
        g = Game(player_count=pop_size,
                 player_starting_positions="fixed",
                 board_config=board_config,
                 random_move_count=move_length,
                 move_generation_type="list",
                 game_mode="coexist",
                 colors=colors,
                 random_player_colors=True)

        move = copy.deepcopy(champ_moves)
        if gen == 0:
            g.mutate_moves(move, mut_chance=initial_mutation_chance)
        else:
            g.mutate_moves(move, mut_chance=mutation_chance)

        g.run_game(fps=train_fps, display_interval=display_interval)
        generation_scores[gen, :] = [p.score for p in g.players]
        gen_champ, best_score = g.find_winner()
        if best_score > champ_score:
            champ_score = best_score
            champ_moves = gen_champ.static_move_list
        champion_scores[gen] = champ_score
        print(f"Finished Generation {gen} with score: {best_score} / Last Champ: {champ_score}")
        record["champion_scores"] = champion_scores
        record["generation_scores"] = generation_scores
    return champ_moves, record


def visualize_scores(record):
    plt.plot(record["champion_scores"])

    for g, gen_score_list in enumerate(record["generation_scores"]):
        sns.scatterplot(x=[g for _ in range(gen_score_list.shape[0])], y=gen_score_list, color="k", hue=gen_score_list, legend=False)

    plt.show()


def display_ga_champion(champ_disp_count=1):
    move_length = 100
    theretical_max = move_length * (move_length + 1) / 2
    print(f"Theoretical Max Score: {theretical_max}")
    best_moves, record = genetic_algorithm(initial_mutation_chance=.8,
                                           move_length=move_length,
                                           display_interval=50,
                                           generations=80,
                                           pop_size=100,
                                           mutation_chance=.04,
                                           train_fps=2048)
    print(f"Achineved score (% of theoretical max): %{round(100*record['champion_scores'][-1]/theretical_max,2)}")
    for _ in range(champ_disp_count):
        g = Game(player_count=1,
                 player_starting_positions="fixed",
                 board_config=board_config,
                 random_move_count=move_length,
                 move_generation_type="list",
                 colors=colors)

        g.mutate_moves(best_moves, mut_chance=0)
        g.run_game(fps=12, display_interval=1, wait_for_user=False)
    pygame.quit()
    visualize_scores(record)


display_ga_champion(champ_disp_count=3)

"""
g = Game(player_count=5,
         player_starting_positions="fixed",
         board_config=board_config,
         turn_limit=500,
         move_generation_type="fixed",
         game_mode="coexist",
         colors=colors)
g.run_game(fps=50, display_interval=1, wait_for_user=True)
"""
#pygame.quit()
# print(g.find_winner())
sys.exit()
