import PySimpleGUI as sg
import time
import stat_plot
import stat_ui_init


def create_session_text_statistics_layout(database, session_idx):
    """
    create a column listbox layout that shows the rates as the following format:
    session_cap/session_attempt (session_rate%) | total_cap/total_attempt (total_rate%) | chapter_name
    """
    chapters_list = database.config['Chapters']
    (sessions_cap, sessions_attempt, sessions_rate), (total_cap, total_attempt, total_rate) = database.aggregate_cap_rates()
    text_layout = []
    for i, chapter in enumerate(chapters_list):
        text_layout.append([sg.Text(
            f'({sessions_rate[session_idx][i] * 100:.2f}%) '
            f'{sessions_cap[session_idx][i]}/{sessions_attempt[session_idx][i]} | '
            f'total ({total_rate[i] * 100:.2f}%) '
            f'{total_cap[i]}/{total_attempt[i]} | '
            f'{chapter}')])
    return text_layout


def select_session_menu(init_info, database):
    """
    select a session to view statistics
    uses a scrollable list to select a session, then calls show_session_stat_menu on the selected session
    :param init_info: the ui initialization info
    :param database: the database to store the data
    """
    SHOW_STAT_STR = 'Show Statistics'
    REMOVE_SESSION_STR = 'Remove Selected Session'

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
                  [sg.Button(SHOW_STAT_STR), sg.Button(REMOVE_SESSION_STR), sg.Button('Back')]]

        window = sg.Window('thstat', layout)
        while True:
            event, values = window.read()
            if event in [sg.WIN_CLOSED, 'Back']:  # if user closes window or clicks cancel
                continue_flag = False
                break
            elif event in [SHOW_STAT_STR, REMOVE_SESSION_STR]:
                break
        window.close()
        if event in [SHOW_STAT_STR, REMOVE_SESSION_STR]:
            selected_strs = values['-SESSION-']
            if len(selected_strs) != 0:
                session_idx = int(values['-SESSION-'][0].split('.')[0])
                if event == SHOW_STAT_STR:
                    show_session_stat_menu(init_info, database, session_idx)
                elif event == REMOVE_SESSION_STR:
                    database.remove_game_session(session_idx)
                    database.commit()
            else:
                print('No session selected. Please select a session.')


def show_session_stat_menu(init_info, database, session_idx):
    """
    show the game statistics
    :param init_info: the ui initialization info
    :param database: the database to store the data
    :param session_idx: the session to show statistics
    """
    # show the capture rate using pyplot
    # each spell's capture rate is displayed as sum of individual segments divided by Total

    chapters_list = database.config['Chapters']
    (sessions_cap, sessions_attempt, sessions_rate), (total_cap, total_attempt, total_rate) = database.aggregate_cap_rates()
    im_bytes, width, height = stat_plot.plt_im_bytes_session_capture_rates(chapters_list, sessions_rate[session_idx])

    text_layout = create_session_text_statistics_layout(database, session_idx)

    # reference:https://stackoverflow.com/questions/70474671/pysimplegui-graph-displaying-an-image-directly
    graph = sg.Graph(
        canvas_size=(width, height),
        graph_bottom_left=(0, 0),
        graph_top_right=(width, height),
        background_color='white',
        key='-GRAPH-',
    )
    graph_layout = [[graph],
                    [sg.Button('Back')]]

    layout = [[sg.Column(text_layout), sg.Column(graph_layout)]]

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
    POP_RESULT_STR = 'Pop Last Result'
    continue_flag = True
    chapter_list = database.config['Chapters']
    success_list = [1] * len(chapter_list)
    while continue_flag:
        chapter_buttons = []

        # button list for pass/fail
        pass_fail_layout = []
        for i in range(len(chapter_list)):
            button_text = f'Chapter {i + 1}: {chapter_list[i]}'
            button_key = f'-CHAPTER{i + 1}-'

            if success_list[i] == 1:
                display_text = sg.Text('Passed', text_color='green')
            else:
                display_text = sg.Text('Failed', text_color='red')
            pass_fail_layout.append([sg.Button(button_text, key=button_key), display_text])
            chapter_buttons.append(button_key)
        pass_fail_layout.append([sg.Submit(), sg.Button('Finish')])

        # display the current results in this session
        results = database.data['Data'][session_idx]['Result']
        result_display_strs = [str(result) for result in results]
        listbox = sg.Listbox(values=result_display_strs, size=(40, 20), key='-RESULT-', enable_events=False)
        result_layout = [[sg.Text('Current Results')],
                         [listbox]]
        if len(results) != 0:
            result_layout.append([sg.Button(POP_RESULT_STR)])

        # display the session statistics as well
        text_layout = create_session_text_statistics_layout(database, session_idx)

        layout = [[sg.Column(pass_fail_layout), sg.Column(result_layout), sg.Column(text_layout)]]

        window = sg.Window('thstat', layout)
        while True:
            event, values = window.read()
            if event in [sg.WIN_CLOSED, 'Finish']:  # if user closes window or clicks cancel
                continue_flag = False
                break
            elif event == 'Submit':
                break
            elif event in chapter_buttons:
                chapter_idx = int(event[8:len(event) - 1]) - 1
                success_list[chapter_idx] = 1 - success_list[chapter_idx]
                break  # refresh the window
            elif event == POP_RESULT_STR:
                break
        window.close()

        if event == 'Submit':
            database.add_game_result(session_idx, success_list)
            database.commit()
            success_list = [1] * len(chapter_list)  # don't assume the player still have the same outcome
        elif event == POP_RESULT_STR:
            print('popping result')
            database.pop_game_result(session_idx)
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
