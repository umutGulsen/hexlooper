from Player import Player


class Game(object):
    def __init__(self, player_count, player_starting_positions, board_config):
        players = []
        for i in range(player_count):
            players.append(Player(id=i, pos=player_starting_positions[i]))
        self.players = players

    def find_winner(self):
        pass

    def start_game(self):
        pass
