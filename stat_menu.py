import PySimpleGUI as sg
import time
import stat_plot
import stat_ui_init
import constants
import utilities.popup_menu as popup_menu


def create_session_text_statistics_layout(database, session_idx):
    """
    return a dict of layouts that shows the rates as the following format, one layout per stage:
    session_cap/session_attempt (session_rate%) | total_cap/total_attempt (total_rate%) | chapter_name
    """
    config_stages = database.get_config_stage_dict()

    layouts = {}
    for stage_id in config_stages:
        chapters_list = config_stages[stage_id]
        (sessions_cap, sessions_attempt, sessions_rate), (total_cap, total_attempt, total_rate) = database.aggregate_cap_rates(stage_id)
        stat_layout = []
        for i, chapter in enumerate(chapters_list):
            stat_layout.append([sg.Text(
                f'({sessions_rate[session_idx][i] * 100:.2f}%) '
                f'{sessions_cap[session_idx][i]}/{sessions_attempt[session_idx][i]} | '
                f'total ({total_rate[i] * 100:.2f}%) '
                f'{total_cap[i]}/{total_attempt[i]}')])
        layouts[stage_id] = stat_layout
    return layouts


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
        for i, session in enumerate(database.data[constants.DATA_DATA]):
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
                    if popup_menu.confirm_popup('thstat', 'Are you sure you want to remove this session?'):
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

    layout = []
    stat_layouts = create_session_text_statistics_layout(database, session_idx)

    config_stages = database.get_config_stage_dict()
    # add the stage name to the layout
    for stage_id in config_stages:
        chapters_list = config_stages[stage_id]
        stage_layout = stat_layouts[stage_id]
        for i in range(len(stage_layout)):
            row = stage_layout[i]
            row.append(sg.Text(chapters_list[i]))
    im_data_dict = {}
    for stage_id in config_stages:
        chapters_list = config_stages[stage_id]
        (sessions_cap, sessions_attempt, sessions_rate), (total_cap, total_attempt, total_rate) = database.aggregate_cap_rates(stage_id)
        im_data = stat_plot.plt_im_bytes_session_capture_rates(chapters_list, sessions_rate[session_idx])
        width, height = im_data[1], im_data[2]
        im_data_dict[stage_id] = im_data

        # reference:https://stackoverflow.com/questions/70474671/pysimplegui-graph-displaying-an-image-directly
        graph = sg.Graph(
            canvas_size=(width, height),
            graph_bottom_left=(0, 0),
            graph_top_right=(width, height),
            background_color='white',
            key=f'-GRAPH-{stage_id}-',
        )
        graph_layout = [[graph]]
        horizontal_layout = [[sg.Column(stat_layouts[stage_id]), sg.Column(graph_layout)]]
        layout.append([sg.Tab(stage_id,  horizontal_layout)])

    layout = [[sg.TabGroup(layout)],
              [sg.Button('Back')]]

    window = sg.Window('thstat', layout, finalize=True)
    for stage_id in config_stages:
        graph = window[f'-GRAPH-{stage_id}-']
        im_bytes, width, height = im_data_dict[stage_id]
        graph.draw_image(data=im_bytes, location=(0, height))

    while True:
        event, values = window.read()
        if event in [sg.WIN_CLOSED, 'Back']:
            break
    window.close()


def get_default_success_dict(config_stages):
    """
    get the default success list for a game session
    :return: the default success list
    """
    success_dict = {}
    for stage_id in config_stages:
        success_dict[stage_id] = [1] * len(config_stages[stage_id])
    return success_dict


def gameplay_session_creation_menu(init_info, database, session_idx):
    """
    the menu for a game session
    :param init_info: the ui initialization info
    :param database: the database to store the data
    :param session_idx: the index of the session
    """
    POP_RESULT_STR = 'Pop Last Result'
    config_stages = database.get_config_stage_dict()
    config_stages_list = list(config_stages.keys())
    default_tab_key = f'-{config_stages_list[0]}-'

    CHAPTER_NAME_SIZE = (22, 1)

    continue_flag = True
    success_dict = get_default_success_dict(config_stages)
    quit_location = (len(success_dict), 0)  # initially assume the player does not quit
    while continue_flag:
        stat_layouts = create_session_text_statistics_layout(database, session_idx)

        # create tab group
        tab_group_layout = []
        for stage_id in config_stages:
            # button list for pass/fail
            chapters_list = config_stages[stage_id]
            success_list = success_dict[stage_id]
            pass_fail_layout = []
            for i in range(len(chapters_list)):
                chapter_text = f'Chapter {i + 1}: {chapters_list[i]}'
                button_key = f'-{stage_id}-{i}-'

                stage_idx = database.get_stage_idx_from_id(stage_id)
                if stage_idx > quit_location[0] or (stage_idx == quit_location[0] and i >= quit_location[1]):
                    display_text = sg.Text('ESC', text_color='green', size=(6, 1))
                    pass_fail_layout.append([sg.Button('Re-add', key=button_key, size=(6, 1)),
                                             sg.Text(chapter_text, size=CHAPTER_NAME_SIZE, text_color='white'),
                                             display_text])
                else:
                    # display the pass/fail button
                    if success_list[i] == 1:
                        display_text = sg.Text('Passed', text_color='green', size=(6, 1))
                    else:
                        display_text = sg.Text('Failed!', text_color='red', size=(6, 1))
                    pass_fail_layout.append([sg.Button('Change', key=button_key, size=(6, 1)),
                                             sg.Text(chapter_text, size=CHAPTER_NAME_SIZE),
                                             display_text])

            # display the session statistics as well
            stat_layout = stat_layouts[stage_id]

            # merge pass_fail_layout and stat_layout
            new_layout = []
            for i in range(len(pass_fail_layout)):
                new_layout.append(pass_fail_layout[i] + stat_layout[i])

            tab_key = f'-{stage_id}-'
            row = [sg.Tab(stage_id, new_layout, key=tab_key)]
            tab_group_layout.append(row)

        # display the current results in this session
        results = database.data[constants.DATA_DATA][session_idx][constants.DATA_RESULT]
        result_display_strs = [str(result) for result in results]
        listbox = sg.Listbox(values=result_display_strs, size=(40, 20), key='-RESULT-', enable_events=False)
        result_layout = [[sg.Text('Current Results')],
                         [listbox]]
        if len(results) != 0:
            result_layout.append([sg.Button(POP_RESULT_STR)])

        tab_group = sg.TabGroup(tab_group_layout, enable_events=True, key='-TABGROUP-')
        layout = [[sg.Column(result_layout),
                   sg.Column([[tab_group],
                              [sg.Button('Submit'), sg.Button('Finish')]])]]

        window = sg.Window('thstat', layout, finalize=True)
        window[f'{default_tab_key}'].select()

        while True:
            event, values = window.read()
            if event in [sg.WIN_CLOSED, 'Finish']:  # if user closes window or clicks cancel
                continue_flag = False
                break
            elif event == 'Submit':
                break
            elif event == '-TABGROUP-':
                default_tab_key = values['-TABGROUP-']
                continue
            elif event.startswith('-') and event.endswith('-'):
                substrs = event.split('-')
                stage_id, chapter_idx = substrs[1:3]
                stage_idx = database.get_stage_idx_from_id(stage_id)
                chapter_idx = int(chapter_idx)

                if stage_idx > quit_location[0] or (stage_idx == quit_location[0] and chapter_idx >= quit_location[1]):
                    # if a button on a quitted stage is pressed, then unquit the stage
                    quit_location = (stage_idx, chapter_idx + 1)
                    success_dict[stage_id][chapter_idx] = 1
                elif success_dict[stage_id][chapter_idx] == 1:
                    success_dict[stage_id][chapter_idx] = 0
                else:  # success_dict[stage_id][chapter_idx] == 0
                    quit_location = (stage_idx, chapter_idx)
                    success_dict[stage_id][chapter_idx] = 1
                break  # refresh the window
            elif event == POP_RESULT_STR:
                break
        window.close()

        if event == 'Submit':
            truncated_dict = {}  # handle the case where the player quits in the middle of a game
            for stage_id in success_dict:
                stage_idx = database.get_stage_idx_from_id(stage_id)
                if stage_idx > quit_location[0]:
                    truncated_dict[stage_id] = []
                elif stage_idx == quit_location[0]:
                    truncated_dict[stage_id] = success_dict[stage_id][:quit_location[1]]
                else:
                    truncated_dict[stage_id] = success_dict[stage_id].copy()

            database.add_game_result(session_idx, truncated_dict)
            database.commit()
            success_dict = get_default_success_dict(config_stages)  # don't assume the player still have the same outcome
            quit_location = (len(success_dict), 0)  # reset the quit location
        elif event == POP_RESULT_STR:
            database.pop_game_result(session_idx)
            database.commit()


def main_menu(init_info, database):
    # reference: https://www.pysimplegui.org/en/latest/

    continue_flag = True
    while continue_flag:
        date_str = time.strftime("%Y-%m-%d", time.localtime())
        CREATE_STR = 'Create a new game session'
        STAT_STR = 'See game statistics'
        layout = [[sg.Text(f'Current date is {date_str}')]]

        legal_values_dict = {}
        for key in database.get_all_dropdown_attribute_name():
            attr = database.config[key]
            ui_save_key = attr['SaveKey']
            legal_values_dict[key] = attr['Values']

            if init_info.has(ui_save_key):
                default_value = init_info.get(ui_save_key)
            else:
                default_value = legal_values_dict[key][0]
            layout.append([sg.Text(attr['DisplayText']),
                           sg.DropDown(legal_values_dict[key], key=f'-dropdown-{key}-',
                                       default_value=default_value, enable_events=True, readonly=True)])

        layout.append([[sg.Button(CREATE_STR)],
                       [sg.Text('OR')],
                       [sg.Button(STAT_STR)]])

        window = sg.Window('thstat', layout)
        while True:
            event, values = window.read()
            if event in [sg.WIN_CLOSED, 'Cancel']:  # if user closes window or clicks cancel
                continue_flag = False
                break
            if event in [CREATE_STR, STAT_STR]:
                attributes = {}
                for key in database.get_all_dropdown_attribute_name():
                    attr = database.config[key]
                    ui_save_key = attr['SaveKey']
                    init_info.set(ui_save_key, values[f'-dropdown-{key}-'])
                    attributes[key] = values[f'-dropdown-{key}-']
                database.set_current_dropdown_attributes(attributes)
                break
        window.close()

        if event == CREATE_STR:
            session_idx = database.add_game_session(date_str)
            database.commit()
            gameplay_session_creation_menu(init_info, database, session_idx)
            # if the session is empty, pop it
            if len(database.data[constants.DATA_DATA][session_idx][constants.DATA_RESULT]) == 0:
                database.remove_game_session(session_idx)
                database.commit()
        elif event == STAT_STR:
            select_session_menu(init_info, database)
