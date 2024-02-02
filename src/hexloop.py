import pygame
import sys
from Game import Game
import numpy as np
import copy
import matplotlib.pyplot as plt
import seaborn as sns
import optuna
import os
from optuna.visualization import plot_contour
from optuna.visualization import plot_parallel_coordinate
from optuna.visualization import plot_param_importances
from optuna.visualization import plot_optimization_history

board_config = {"height": 600,
                "width": 1000,
                "hex_radius": 12
                }

colors = {
    "BLACK": (30, 30, 30),
    "WHITE": (255, 255, 255),
    "GRAY": (200, 200, 200),
    "GREEN": (0, 153, 51),
    "PLAYER_COLOR": (153, 0, 0),
    "HIGHLIGHT_COLOR": (255, 255, 0),  # Yellow for highlight
    "TRACK_COLOR": (102, 153, 255)
}


# import cProfile
# cProfile.run("g.run_game(fps=40960, display_interval=10000)", sort="tottime")


def genetic_algorithm(initial_mutation_chance: float, move_length: int, display_interval: int, train_fps: int = 4096, **params):
    generations = params.get("generations")
    pop_size = params.get("pop_size")
    mutation_chance = params.get("mutation_chance")
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


def display_ga_champion(champ_disp_count=1, move_length=100, **params):

    theretical_max = move_length * (move_length + 1) / 2
    print(f"Theoretical Max Score: {theretical_max}")
    best_moves, record = genetic_algorithm(initial_mutation_chance=.8,
                                           move_length=move_length,
                                           display_interval=1,
                                           train_fps=16,
                                           **params)
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


def objective(trial):
    move_length = 100
    params = {
        "generations": trial.suggest_int("generations", 3, 30),
        "pop_size": trial.suggest_int("pop_size", 3, 5),
        "mutation_chance": trial.suggest_float("mutation_chance", .01, .20),
    }
    _, trial_record = genetic_algorithm(initial_mutation_chance=.8,
                                            move_length=move_length,
                                            display_interval=101,
                                            train_fps=1024,
                                            **params)
    return trial_record["champion_scores"][-1]
print(os.listdir(os.getcwd()))

study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=0)
                            )
study.optimize(objective, n_trials=5)
file_path = 'optuna_results/optimal_params.txt'

# Open the file in write mode and write the dictionary items as key-value pairs
with open(file_path, 'w') as file:
    for key, value in study.best_params.items():
        file.write(f'{key}: {value}\n')

plot_optimization_history(study).write_html("optuna_results/study_history.html")

plot_parallel_coordinate(study).write_html("optuna_results/plot_parallel_coordinate.html")

plot_param_importances(study).write_html("optuna_results/plot_param_importances.html")

plot_contour(study).write_html("optuna_results/contour.html")
"""

display_ga_champion(champ_disp_count=3)


g = Game(player_count=8,
         player_starting_positions="random",
         random_move_count=300,
         board_config=board_config,
         turn_limit=300,
         move_generation_type="list",
         game_mode="",
         colors=colors,
         random_player_colors=True)
g.run_game(fps=36, display_interval=1, wait_for_user=True)
"""
#pygame.quit()
# print(g.find_winner())
sys.exit()
