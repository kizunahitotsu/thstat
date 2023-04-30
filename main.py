import PySimpleGUI as sg
import stat_config
from stat_database import StatDatabase
import time
import stat_menu
import stat_ui_init
import ctypes
import constants
ctypes.windll.shcore.SetProcessDpiAwareness(2)


def ask_for_config(init_info):
    """
    ask for a config path and return the result
    :param init_info: the ui initialization info
    :return: a tuple of (config_path, config, data)
    """
    if init_info.has(constants.KEY_CONFIG_PATH):
        default_text = init_info.get(constants.KEY_CONFIG_PATH)
    else:
        default_text = ''
    layout = [[sg.Text('Please enter the path to the config file')],
              [sg.InputText(default_text=default_text), sg.FileBrowse()],
              [sg.Submit(), sg.Cancel()]]

    window = sg.Window('thstat', layout)
    while True:
        event, values = window.read()
        if event in [sg.WIN_CLOSED, 'Cancel', 'Submit']:  # if user closes window or clicks cancel
            break
    window.close()

    if event != 'Submit':
        return None
    else:
        config_path = values[0]
        config, data = stat_config.load_config(config_path)
        init_info.set(constants.KEY_CONFIG_PATH, config_path)
        return config_path, config, data


def main():
    # load user's past selected values in menus
    init_info = stat_ui_init.UIHistory()

    # load the config file specified by the user
    sg.theme('Gray Gray Gray')
    # font = ("Courier New", 11)
    # sg.set_options(font=font)
    result = ask_for_config(init_info)
    if result:
        config_path, config, data = result
    else:
        return
    database = StatDatabase(config_path, config, data)

    # enter the main menu
    stat_menu.main_menu(init_info, database)


if __name__ == "__main__":
    main()

