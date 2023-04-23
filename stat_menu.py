import PySimpleGUI as sg
import time
from matplotlib import pyplot as plt
from io import BytesIO


def select_session_menu(init_info, database):
    """
    select a session to view statistics
    uses a scrollable list to select a session, then calls show_session_stat_menu on the selected session
    :param init_info: the ui initialization info
    :param window: the window to display the menu
    :param database: the database to store the data
    """
    SHOW_STAT_STR = 'Show Statistics'

    continue_flag = True
    while continue_flag:
        # show the list of all recorded gameplay sessions
        items = []
        for i, session in enumerate(database.data['Data']):
            items.append(f'{i}.{session["Date"]}')
        if len(items) == 0:
            print('No recorded session found. Record a game first.')
            break

        layout = [[sg.Text('Select a session to view statistics')],
                  [sg.Listbox(values=items, select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                              size=(40, 20), key='-SESSION-')],
                  [sg.Button(SHOW_STAT_STR), sg.Button('Back')]]

        window = sg.Window('thstat', layout)
        while True:
            event, values = window.read()
            if event in [sg.WIN_CLOSED, 'Back']:  # if user closes window or clicks cancel
                continue_flag = False
                break
            elif event == SHOW_STAT_STR:
                break
        window.close()
        if event == SHOW_STAT_STR:
            selected_strs = values['-SESSION-']
            if len(selected_strs) != 0:
                session_idx = int(values['-SESSION-'][0].split('.')[0])
                session = database.data['Data'][session_idx]
                show_session_stat_menu(init_info, database, session)
            else:
                print('No session selected. Please select a session.')


def show_session_stat_menu(init_info, database, session):
    """
    show the game statistics
    :param init_info: the ui initialization info
    :param window: the window to display the menu
    :param database: the database to store the data
    :param session: the session to show statistics
    """
    # show the capture rate using pyplot
    # each spell's capture rate is displayed as sum of individual segments divided by Total

    chapters_list = database.config['Chapters']
    capture_list = [0] * len(chapters_list)
    total_list = database.data['Total']
    for i, run in enumerate(session['Result']):
        for j, success in enumerate(run):
            capture_list[j] += success
    capture_rate = [capture_list[i] / total_list[i] for i in range(len(capture_list))]
    plt.bar(range(len(capture_rate)), capture_rate)
    plt.xlabel('section')
    plt.ylabel('NN rate')
    bio = BytesIO()
    plt.savefig(bio, format='png')
    plt.show()
    plt.cla()
    bio.seek(0)
    im_bytes = bio.getvalue()

    width, height = 320, 240
    # reference: https: // stackoverflow.com / questions / 70474671 / pysimplegui - graph - displaying - an - image - directly
    graph = sg.Graph(
        canvas_size=(width, height),
        graph_bottom_left=(0, 0),
        graph_top_right=(width, height),
        background_color='white',
        key='-GRAPH-',
    )
    layout = [[graph],
              [sg.Button('Back')]]
    window = sg.Window('thstat', layout, finalize=True)
    graph = window['-GRAPH-']

    graph.draw_image(data=im_bytes, location=(0, 0))

    while True:
        event, values = window.read()
        if event in [sg.WIN_CLOSED, 'Back']:
            break
    window.close()


def session_menu(init_info, database, session_idx):
    """
    the menu for a game session
    :param init_info: the ui initialization info
    :param window: the window to display the menu
    :param database: the database to store the data
    :param session_idx: the index of the session
    """
    layout = [[sg.Text('Please enter the result of the game')],
              [sg.InputText(key='-RESULT-')],
              [sg.Submit(), sg.Cancel()]]

    window = sg.Window('thstat', layout)
    while True:
        event, values = window.read()
        if event in [sg.WIN_CLOSED, 'Cancel', 'Submit']:  # if user closes window or clicks cancel
            break
    window.close()

    if event == 'Submit':
        result_str = values['-RESULT-']
        result = []
        for c in result_str:
            if c == '0':
                result.append(0)
            elif c == '1':
                result.append(1)
        database.add_game_result(session_idx, result)
        database.save()


def main_menu(init_info, database):
    # reference: https://www.pysimplegui.org/en/latest/

    continue_flag = True
    while continue_flag:
        date_str = time.strftime("%Y-%m-%d", time.localtime())
        CREATE_STR = 'Create a new game session'
        STAT_STR = 'See game statistics'
        layout = [[sg.Text(f'Current date is {date_str}')],
                  [sg.Text('Keyboard Used'), sg.InputText(key='keyboard_used')],
                  [sg.Button(CREATE_STR)],
                  [sg.Text('OR')],
                  [sg.Button(STAT_STR)]]

        window = sg.Window('thstat', layout)
        while True:
            event, values = window.read()
            if event in [sg.WIN_CLOSED, 'Cancel']:  # if user closes window or clicks cancel
                continue_flag = False
                break
            if event in [CREATE_STR, STAT_STR]:
                break
        window.close()
        if event == CREATE_STR:
            keyboard = values['keyboard_used']
            session_idx = database.add_game_session(date_str, keyboard)
            session_menu(init_info, database, session_idx)
        elif event == STAT_STR:
            select_session_menu(init_info, database)
