import pygame
import sys
from Game import Game
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import optuna
import copy
import json
import os
import time
from optuna.visualization import plot_contour
from optuna.visualization import plot_parallel_coordinate
from optuna.visualization import plot_param_importances
from optuna.visualization import plot_optimization_history
import logging

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.INFO)


# import cProfile
# cProfile.run("g.run_game(fps=40960, display_interval=10000)", sort="tottime")


def genetic_algorithm(initial_mutation_chance: float, move_length: int, display_interval: int, train_fps: int = 4096,
                      **params):
    generations = params.get("generations")
    pop_size = params.get("pop_size")
    mutation_chance = params.get("mutation_chance")

    stagnancy_length = params.get("stagnancy_length")
    stagnancy_extra_mutation_chance = params.get("stagnancy_extra_mutation_chance")

    record = {}
    generation_scores = np.zeros((generations, pop_size))
    champion_scores = np.zeros(generations)
    champ_score = -1
    champ_moves = ((np.random.rand(move_length) * 6 + 1).astype(int))

    for gen in range(generations):
        logging.info(f"Started Generation {gen}")
        g = Game(player_count=pop_size,
                 player_starting_positions="fixed",
                 board_config=config["board_config"],
                 move_count=move_length,
                 move_generation_type="list",
                 game_mode="coexist",
                 colors=colors,
                 random_player_colors=True)

        if gen == 0:
            g.mutate_moves(champ_moves, mut_chance=initial_mutation_chance)
        else:
            enough_gens_to_measure_stagnancy = gen >= stagnancy_length
            if enough_gens_to_measure_stagnancy:
                scores_stagnant = champion_scores[gen - stagnancy_length] == champion_scores[gen - 1]
                if scores_stagnant:
                    g.mutate_moves(champ_moves, mut_chance=mutation_chance + stagnancy_extra_mutation_chance)
                    logging.info(f"Stagnancy detected in Gen {gen}!")
                else:
                    g.mutate_moves(champ_moves, mut_chance=mutation_chance)
            else:
                g.mutate_moves(champ_moves, mut_chance=mutation_chance)

        g.run_game(fps=train_fps, display_interval=display_interval)
        generation_scores[gen, :] = [p.score for p in g.players]
        gen_champ, best_score = g.find_winner()
        if best_score > champ_score:
            champ_score = best_score
            champ_moves = copy.deepcopy(gen_champ.static_move_list)
        champion_scores[gen] = champ_score
        logging.info(f"Finished Generation {gen} with score: {best_score} / Last Champ: {champ_score}")
        record["champion_scores"] = champion_scores
        record["generation_scores"] = generation_scores
    return champ_moves, record


def visualize_scores(record):
    plt.plot(record["champion_scores"])

    for g, gen_score_list in enumerate(record["generation_scores"]):
        sns.scatterplot(x=[g for _ in range(gen_score_list.shape[0])], y=gen_score_list, color="k", hue=gen_score_list,
                        legend=False)

    plt.show()


def display_ga_champion(champ_disp_count=1, move_length: int = 100, params: dict = None):
    theoretical_max = move_length * (move_length + 1) / 2
    logging.info(f"Theoretical Max Score: {theoretical_max}")
    best_moves, record = genetic_algorithm(initial_mutation_chance=.8,
                                           move_length=move_length,
                                           display_interval=200,
                                           train_fps=40960,
                                           **params)
    logging.info(
        f"Achieved score (% of theoretical max): %{round(100 * record['champion_scores'][-1] / theoretical_max, 2)}")
    # best_moves=[_%2 for _ in range(5)]
    # print(best_moves)
    for _ in range(champ_disp_count):
        g = Game(**game_params)
        g = Game(player_count=1,
                 player_starting_positions="fixed",
                 board_config=config["board_config"],
                 move_count=move_length,
                 move_generation_type="list",
                 colors=colors)

        g.mutate_moves(best_moves, mut_chance=0)
        g.run_game(fps=5, display_interval=1, wait_for_user=False)
        # time.sleep(2)
    pygame.quit()
    visualize_scores(record)


def objective(trial):
    move_length = 50
    params = {
        # "generations": trial.suggest_int("generations", 15, 40),
        # "pop_size": trial.suggest_int("pop_size", 1, 40),
        "generations": 40,
        "pop_size": 40,
        "mutation_chance": trial.suggest_float("mutation_chance", .01, .35),
        "stagnancy_length": trial.suggest_int("stagnancy_length", 1, 10),
        "stagnancy_extra_mutation_chance": trial.suggest_float("stagnancy_extra_mutation_chance", .01, .7)
    }
    _, trial_record = genetic_algorithm(initial_mutation_chance=.8,
                                        move_length=move_length,
                                        display_interval=500,
                                        train_fps=10000,
                                        **params)
    return trial_record["champion_scores"][-1] / (move_length * (move_length + 1) / 2)


def run_optimization_with_optuna(n_trials: int = 20):
    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=0)
                                )
    study.optimize(objective, n_trials=n_trials)
    file_path = 'optuna_results/optimal_params.txt'

    # Open the file in write mode and write the dictionary items as key-value pairs
    with open(file_path, 'w') as file:
        for key, value in study.best_params.items():
            file.write(f'{key}: {value}\n')

    plot_optimization_history(study).write_html("optuna_results/study_history.html")

    plot_parallel_coordinate(study).write_html("optuna_results/plot_parallel_coordinate.html")

    plot_param_importances(study).write_html("optuna_results/plot_param_importances.html")

    plot_param_importances(study, target=lambda t: t.duration.total_seconds(), target_name="duration").write_html(
        "optuna_results/plot_param_duration_impact.html")

    plot_contour(study).write_html("optuna_results/contour.html")


def network_evolution(generations: int, pop_size: int, layer_sizes: list, move_length: int, display_interval: int,
                      train_fps: int = 4096, **params):
    theoretical_max = move_length * (move_length + 1) / 2
    record = {}
    generation_scores = np.zeros((generations, pop_size))
    champion_scores = np.zeros(generations)
    champ_score = -1
    champ_network = None
    for gen in range(generations):
        g = Game(player_count=pop_size,
                 player_starting_positions="fixed",
                 turn_limit=move_length,
                 board_config=config["board_config"],
                 move_generation_type="network",
                 game_mode="coexist",
                 colors=colors,
                 random_player_colors=True,
                 layer_sizes=layer_sizes,
                 base_network=champ_network,
                 **params)
        g.run_game(fps=train_fps, display_interval=display_interval)
        generation_scores[gen, :] = [p.score for p in g.players]

        gen_champ, best_score = g.find_winner()
        # best_score += gen_champ.track_score / 5

        if best_score > champ_score:
            champ_score = best_score
            champ_network = copy.deepcopy(gen_champ.network)
        champion_scores[gen] = champ_score
        logging.info(f"Finished Generation {gen} with score: {best_score} / Last Champ: {champ_score}")
        record["champion_scores"] = champion_scores
        record["generation_scores"] = generation_scores
        if champ_score >= theoretical_max:
            logging.info("Theoretical Max Score Achieved!!")
            break
    return champ_network, record


def display_ne_champion(champ_disp_count=1, move_length: int = 10, **params):
    theoretical_max = move_length * (move_length + 1) / 2
    logging.info(f"Theoretical Max Score: {theoretical_max}")
    best_network, record = network_evolution(move_length=move_length,
                                             **params)
    logging.info(
        f"Achieved score (% of theoretical max): %{round(100 * record['champion_scores'][-1] / theoretical_max, 2)}")
    # best_moves=[_%2 for _ in range(5)]
    # print(best_moves)
    for _ in range(champ_disp_count):
        g = Game(player_count=1,
                 player_starting_positions="fixed",
                 board_config=config["board_config"],
                 turn_limit=move_length,
                 move_generation_type="network",
                 game_mode="coexist",
                 base_network=best_network,
                 network_update_variance=0,
                 colors=colors)

        # g.players[0].network = best_network
        g.run_game(fps=4, display_interval=1, wait_for_user=False)
        # time.sleep(2)
    pygame.quit()
    visualize_scores(record)


colors = {
    "BLACK": (45, 45, 45),
    "WHITE": (255, 255, 255),
    "GRAY": (200, 200, 200),
    "GREEN": (0, 153, 51),
    "PLAYER_COLOR": (153, 0, 0),
    "HIGHLIGHT_COLOR": (255, 255, 0),  # Yellow for highlight
    "TRACK_COLOR": (102, 153, 255)
}

# display_ne_champion(champ_disp_count=40, **ne_params, **train_params)

"""



run_optimization_with_optuna(
)"""
"""
g = Game(player_count=1,
         player_starting_positions="random",
         random_move_count=0,
         board_config=board_config,
         turn_limit=10,
         move_generation_type="network",
         game_mode="",
         colors=colors,
         random_player_colors=True,
         layer_sizes=[4, 4])
g.run_game(fps=1, display_interval=1, wait_for_user=False)

"""


# pygame.quit()
# print(g.find_winner())


def main():
    global config
    with open('src/config.json', 'r') as file:
        config = json.load(file)

    print("### WELCOME TO HEXLOOPER ###")
    print("### CHOOSE THE GAME MODE... ###")
    print(
        "Profiling (p) - Just Play (j) - Random Evolution (r) - Neural Network Evolution (n) - Hyperparameter Optimization (h)")
    while True:
        mode = input("")
        if mode not in ["p", "j", "r", "n", "h"]:
            print("Choose a valid mode")
            continue
        else:
            if mode == "p":
                import cProfile
                cProfile.run("display_ne_champion(champ_disp_count=10, **ne_params, **train_params)", sort="tottime")
            elif mode == "j":
                player_count = input("Choose player count: ")
                game_params = {"player_count": int(player_count),
                               "player_starting_positions": "random",
                               "board_config": config["board_config"],
                               "turn_limit": 10,
                               "move_generation_type": "manual",
                               "game_mode": "just_play",
                               "colors": colors,
                               "random_player_colors": True,
                               }
                print(f"Game is running with following parameters:")
                for key, value in game_params.items():
                    print(f"{key}: {value}")
                g = Game(**game_params)
                g.run_game(fps=10, display_interval=1, wait_for_user=True)
            elif mode == "r":
                display_ga_champion(champ_disp_count=10, **config["ga_params"], **config["train_params"])
            else:
                print("Enter a valid input.")
            break
    sys.exit()


if __name__ == '__main__':
    main()
