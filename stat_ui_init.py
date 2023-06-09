import os


class UIHistory:
    def __init__(self):
        if os.path.exists('ui.init'):
            ui_history_file = open('ui.init', mode='r', encoding='UTF-8')
            ui_history = {}
            for line in ui_history_file.readlines():
                split_idx = line.index(':')
                key = line[:split_idx]
                value = line[split_idx + 1:].rstrip('\n')
                ui_history[key] = value
        else:
            # use default settings
            ui_history = {}

        self.history = ui_history

    def has(self, key):
        return key in self.history

    def get(self, key):
        return self.history[key]

    def set(self, key, value):
        self.history[key] = value
        self.write_to_file()

    def write_to_file(self):
        with open('ui.init', mode='w', encoding='UTF-8') as f:
            for key, value in self.history.items():
                f.write(f'{key}:{value}\n')
