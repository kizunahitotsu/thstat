import PySimpleGUI as sg
import stat_config
from stat_database import StatDatabase


def ask_for_config():
    """
    ask for a config path and return the result
    :return: a tuple of (config_path, config, data)
    """
    layout = [[sg.Text('Please enter the path to the config file')],
              [sg.InputText(), sg.FileBrowse()],
              [sg.Submit(), sg.Cancel()]]

    window = sg.Window('thstat', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            quit_flag = True
            break
        if event == 'Submit':
            quit_flag = False
            break
    window.close()

    if quit_flag:
        return None
    else:
        config_path = values[0]
        config, data = stat_config.load_config(config_path)
        return config_path, config, data


def main():
    sg.theme('Default')

    result = ask_for_config()
    if result:
        config_path, config, data = result
    else:
        return
    database = StatDatabase(config_path, config, data)

    print(database.data)
    print(database.config)
    print(database.config_path)

    # reference: https://www.pysimplegui.org/en/latest/
    # TODO
    layout = [[sg.Text('Some text on Row 1')],
              [sg.Text('Enter something on Row 2'), sg.InputText()],
              [sg.Button('Ok'), sg.Button('Cancel')]]

    window = sg.Window('thstat', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break

    window.close()


if __name__ == "__main__":
    main()

