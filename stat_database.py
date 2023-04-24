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

    def commit(self):
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

    def remove_game_session(self, session_idx):
        """
        remove the last game session from 'Data'
        """
        data_field = self.data['Data']
        for i in range(len(data_field[session_idx]['Result']) - 1, -1, -1):
            self.pop_game_result(session_idx)
        data_field.pop(session_idx)  # remove the game session entirely

    def add_game_result(self, session_idx, result):
        """
        add a game result to the database
        :param session_idx: the index of the session
        :param result: the result of the game, a list of 0 (fail) or 1 (capture)
        """
        self.data['Data'][session_idx]['Result'].append(result.copy())
        for i in range(len(result)):
            self.data['Total'][i] += 1

    def pop_game_result(self, session_idx):
        """
        remove the last game result from the specified session
        :param session_idx: the index of the session
        """
        result = self.data['Data'][session_idx]['Result'].pop()
        for i in range(len(result)):
            self.data['Total'][i] -= 1

    def aggregate_cap_rates(self):
        """
        aggregate the capture rates
        :return: ((sessions cap, sessions attempt, sessions rate), (total cap, total attempt, total rate))
        """
        total = self.data['Total']

        sessions_cap = []
        sessions_attempt = []
        sessions_rate = []
        for session in self.data['Data']:
            chapters_list = self.config['Chapters']
            capture_list = [0] * len(chapters_list)
            attempt_list = [0] * len(chapters_list)
            for i, run in enumerate(session['Result']):
                for j, success in enumerate(run):
                    capture_list[j] += success
                    attempt_list[j] += 1
            capture_rate = [capture_list[i] / attempt_list[i] if attempt_list[i] > 0 else 0 for i in range(len(capture_list))]
            sessions_cap.append(capture_list)
            sessions_attempt.append(attempt_list)
            sessions_rate.append(capture_rate)

        # calculate total cap info as three single lists
        total_cap = [0] * len(total)
        total_attempt = [0] * len(total)
        total_rate = [0] * len(total)
        for i in range(len(sessions_cap)):
            for j in range(len(sessions_cap[i])):
                total_cap[j] += sessions_cap[i][j]
                total_attempt[j] += sessions_attempt[i][j]
        for i in range(len(total_cap)):
            total_rate[i] = total_cap[i] / total_attempt[i] if total_attempt[i] > 0 else 0

        return (sessions_cap, sessions_attempt, sessions_rate), (total_cap, total_attempt, total_rate)
