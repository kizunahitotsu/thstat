
import PySimpleGUI as sg


def confirm_popup(title, message):
    """
    show a popup window to confirm the action
    :param title: the title of the popup window
    :param message: the message of the popup window
    :return: True if the user clicks "Confirm", False otherwise
    """
    layout = [
        [sg.Text(message)],
        [sg.Button('Yes'), sg.Button('No')]
    ]
    window = sg.Window(title, layout)
    event, values = window.read()
    window.close()
    if event == 'Yes':
        return True
    else:
        return False
