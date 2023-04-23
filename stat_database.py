import PySimpleGUI as sg
import stat_config
import time


class StatDatabase:
    """
    This class is used to store the statistics of the game.
    """
    def __init__(self, config_path, config, data):
        self.config_path = config_path
        self.config = config
        self.data = data

    def save(self):
        """
        save the data to the file
        """
        stat_config.save_config(self.config_path, self.config, self.data)

    def add_game_session(self, date_str, keyboard):
        """
        add a data to the database
        :param keyboard: the keyboard
        :return: an index to the newly added session
        """
        game_session = {
            'Date': date_str,
            'Keyboard': keyboard,
            'Result': [],
        }
        idx = len(self.data['Data'])
        self.data['Data'].append(game_session)
        return idx

    def add_game_result(self, session_idx, result):
        """
        add a game result to the database
        :param session_idx: the index of the session
        :param result: the result of the game, a list of 0 (fail) or 1 (capture)
        """
        self.data['Data'][session_idx]['Result'].append(result)
        for i in range(len(result)):
            self.data['Total'][i] += 1


