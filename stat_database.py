import PySimpleGUI as sg
import stat_config


class StatDatabase:
    """
    This class is used to store the statistics of the game.
    """
    def __init__(self, config_path, config, data):
        self.config_path = config_path
        self.config_file = open(config_path, mode='a+', encoding='UTF-8')
        self.config = config
        self.data = data
