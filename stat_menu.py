import PySimpleGUI as sg
import time
import stat_plot
import stat_ui_init


def select_session_menu(init_info, database):
    """
    select a session to view statistics
    uses a scrollable list to select a session, then calls show_session_stat_menu on the selected session
    :param init_info: the ui initialization info
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
            default_values = []
            print('No recorded session found. Record a game first.')
            break
        else:
            default_values = [items[0]]

        layout = [[sg.Text('Select a session to view statistics')],
                  [sg.Listbox(values=items, default_values=default_values,
                              select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
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
    :param database: the database to store the data
    :param session: the session to show statistics
    """
    # show the capture rate using pyplot
    # each spell's capture rate is displayed as sum of individual segments divided by Total

    im_bytes, width, height = stat_plot.plt_im_bytes_session_capture_rates(database, session)
    # reference:https://stackoverflow.com/questions/70474671/pysimplegui-graph-displaying-an-image-directly
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
    graph.draw_image(data=im_bytes, location=(0, height))

    while True:
        event, values = window.read()
        if event in [sg.WIN_CLOSED, 'Back']:
            break
    window.close()


def gameplay_session_creation_menu(init_info, database, session_idx):
    """
    the menu for a game session
    :param init_info: the ui initialization info
    :param database: the database to store the data
    :param session_idx: the index of the session
    """
    continue_flag = True
    chapter_list = database.config['Chapters']
    success_list = [1] * len(chapter_list)
    while continue_flag:
        layout = []
        chapter_buttons = []
        for i in range(len(chapter_list)):
            button_text = f'Chapter {i + 1}: {chapter_list[i]}'
            button_key = f'-CHAPTER{i + 1}-'

            if success_list[i] == 1:
                display_text = sg.Text('Passed', text_color='green')
            else:
                display_text = sg.Text('Failed', text_color='red')
            layout.append([sg.Button(button_text, key=button_key), display_text])
            chapter_buttons.append(button_key)
        layout.append([sg.Submit(), sg.Cancel()])

        window = sg.Window('thstat', layout)
        while True:
            event, values = window.read()
            if event in [sg.WIN_CLOSED, 'Cancel']:  # if user closes window or clicks cancel
                continue_flag = False
                break
            elif event == 'Submit':
                success_list = [1] * len(chapter_list)  # don't assume the player still have the same outcome
                break
            elif event in chapter_buttons:
                chapter_idx = int(event[8:len(event) - 1]) - 1
                success_list[chapter_idx] = 1 - success_list[chapter_idx]
                break  # refresh the window
        window.close()

        if event == 'Submit':
            database.add_game_result(session_idx, success_list)
            database.commit()


def main_menu(init_info, database):
    # reference: https://www.pysimplegui.org/en/latest/

    continue_flag = True
    while continue_flag:
        date_str = time.strftime("%Y-%m-%d", time.localtime())
        CREATE_STR = 'Create a new game session'
        STAT_STR = 'See game statistics'
        layout = [[sg.Text(f'Current date is {date_str}')],
                  [sg.Text('Keyboard Used'), sg.InputText(default_text=init_info.get(stat_ui_init.KEY_KEYBOARD_USED),
                                                          key='-KEYBOARD-')],
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
            keyboard = values['-KEYBOARD-']
            session_idx = database.add_game_session(date_str, keyboard)
            database.commit()
            gameplay_session_creation_menu(init_info, database, session_idx)
        elif event == STAT_STR:
            select_session_menu(init_info, database)
