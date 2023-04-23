import PySimpleGUI as sg
import stat_config
from stat_database import StatDatabase
import time
import stat_menu
import ui_init


def ask_for_config(init_info):
    """
    ask for a config path and return the result
    :param init_info: the ui initialization info
    :return: a tuple of (config_path, config, data)
    """
    layout = [[sg.Text('Please enter the path to the config file')],
              [sg.InputText(default_text=init_info.get(ui_init.KEY_KEYBOARD_USED)), sg.FileBrowse()],
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
        init_info.set(ui_init.KEY_KEYBOARD_USED, config_path)
        return config_path, config, data


def main():
    # load user's past selected values in menus
    init_info = ui_init.UIHistory()

    # load the config file specified by the user
    sg.theme('Gray Gray Gray')
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

