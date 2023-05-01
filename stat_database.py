import stat_config
import time
import constants


class StatDatabase:
    """
    This class is used to store the statistics of the game.
    """
    def __init__(self, config_path, config, data):
        self.config_path = config_path
        self.config = config
        self.data = data

        self.stage_idx_from_id = {}
        for stage_id in config[constants.CONFIG_CHAPTERS]:
            stage_idx = len(self.stage_idx_from_id)
            self.stage_idx_from_id[stage_id] = stage_idx
        self.dropdown_attribute_name = []
        self.current_dropdown_attributes = {}
        for key in config.keys():
            attr = config[key]
            if type(attr) == dict and 'Type' in attr.keys():
                if attr['Type'] == 'SelectFromMainMenuDropdown':
                    self.dropdown_attribute_name.append(key)

    def commit(self):
        """
        save the data to the file
        """
        stat_config.save_config(self.config_path, self.config, self.data)

    def add_game_session(self, date_str):
        """
        record a game session to the database
        :param date_str: the date of the game session
        :return: an index to the newly added session
        """
        game_session = {
            'Date': date_str,
            'Attributes': self.current_dropdown_attributes.copy(),
            constants.DATA_RESULT: [],
        }
        idx = len(self.data[constants.DATA_DATA])
        self.data[constants.DATA_DATA].append(game_session)
        return idx

    def remove_game_session(self, session_idx):
        """
        remove the last game session from data field
        """
        data_field = self.data[constants.DATA_DATA]
        for i in range(len(data_field[session_idx][constants.DATA_RESULT]) - 1, -1, -1):
            self.pop_game_result(session_idx)
        data_field.pop(session_idx)  # remove the game session entirely

    def add_game_result(self, session_idx, result):
        """
        add a game result to the database
        :param session_idx: the index of the session
        :param result: the result of the game, a list of 0 (fail) or 1 (capture)
        """
        self.data[constants.DATA_DATA][session_idx][constants.DATA_RESULT].append(result.copy())

    def pop_game_result(self, session_idx):
        """
        remove the last game result from the specified session
        :param session_idx: the index of the session
        """
        self.data[constants.DATA_DATA][session_idx][constants.DATA_RESULT].pop()

    def cap_rates_from_results(self, results, stage_id):
        chapters_list = self.get_config_stage_dict()[stage_id]
        # for the following lists, each has one element for every chapter in the stage
        cap = [0] * len(chapters_list)
        attempt = [0] * len(chapters_list)
        for run in results:
            for i, success in enumerate(run[stage_id]):
                cap[i] += success
                attempt[i] += 1
        rate = [cap[i] / attempt[i] if attempt[i] > 0 else 0 for i in range(len(chapters_list))]
        return cap, attempt, rate

    def aggregate_cap_rates(self, stage_id):
        """
        aggregate the capture rates
        :return: ((sessions cap, sessions attempt, sessions rate), (total cap, total attempt, total rate))
        """
        sessions_cap, sessions_attempt, sessions_rate = [], [], []
        for session_idx in range(len(self.data[constants.DATA_DATA])):
            cap, attempt, rate = self.cap_rates_from_results(self.collect_game_results((session_idx, )), stage_id)
            sessions_cap.append(cap)
            sessions_attempt.append(attempt)
            sessions_rate.append(rate)
        # calculate total cap info as three single lists
        total_cap, total_attempt, total_rate = self.cap_rates_from_results(self.collect_all_game_results(), stage_id)

        return (sessions_cap, sessions_attempt, sessions_rate), (total_cap, total_attempt, total_rate)

    def compute_advanced_summary_statistics(self, stages_cap_rates):
        """
        compute summary statistics. The statistics include:
        1. average number of misses of each level and in total
        2. NN rate of each level and in total
        :param stages_cap_rates:
        :return: (level_misses_arr, total_misses), (level_nn_rate_arr, total_nn_rate)
        """
        level_misses_arr = []
        total_misses = 0.
        level_nn_rate_arr = []
        total_nn_rate = 1.
        for stage_id in stages_cap_rates:
            cap_rates = stages_cap_rates[stage_id]
            level_misses = 0.
            level_nn_rate = 1.
            (sessions_cap, sessions_attempt, sessions_rate), (total_cap, total_attempt, total_rate) = cap_rates
            for rate in total_rate:
                level_misses += 1. - rate
                level_nn_rate *= rate

            level_misses_arr.append(level_misses)
            total_misses += level_misses
            level_nn_rate_arr.append(level_nn_rate)
            total_nn_rate *= level_nn_rate

        return (level_misses_arr, total_misses), (level_nn_rate_arr, total_nn_rate)

    def get_config_stage_dict(self):
        """
        get the chapters list
        :return: the chapters list
        """
        return self.config[constants.CONFIG_CHAPTERS]

    def get_all_dropdown_attribute_name(self):
        """
        get all the attributes that can be used in the dropdown menu
        :return: a list of attributes
        """
        return self.dropdown_attribute_name.copy()

    def set_current_dropdown_attributes(self, attributes):
        """
        set the current dropdown attributes
        :param attributes: a dictionary of attributes {SaveKey = value}
        """
        self.current_dropdown_attributes = attributes.copy()

    def get_stage_idx_from_id(self, stage_id):
        """
        get the stage index from the stage id
        :param stage_id: the stage id
        :return: the stage index
        """
        return self.stage_idx_from_id[stage_id]

    def get_last_game_session_idx(self):
        """
        get the index of the last game session
        :return: the index of the last game session
        """
        return len(self.data[constants.DATA_DATA]) - 1

    def get_stages_cap_rates(self):
        """
        get the capture rates for all stages
        :return: the capture rates dictionary for stages
        """
        config_stages = self.get_config_stage_dict()
        stages_cap_rates = {}
        # add the stage name to the layout
        for stage_id in config_stages:
            cap_rates = self.aggregate_cap_rates(stage_id)
            stages_cap_rates[stage_id] = cap_rates
        return stages_cap_rates

    def collect_game_results(self, session_idx_range):
        """
        collect the game results from the specified sessions as a single matrix
        :param session_idx_range: the range of the sessions
        :return: a list of game results
        """
        game_results = []
        for session_idx in session_idx_range:
            game_results += self.data[constants.DATA_DATA][session_idx][constants.DATA_RESULT]
        return game_results

    def collect_all_game_results(self):
        return self.collect_game_results(range(len(self.data[constants.DATA_DATA])))
