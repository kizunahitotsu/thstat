import matplotlib
from matplotlib import pyplot as plt
from io import BytesIO
import stat_database
import math
import PySimpleGUI as sg
import matplotlib.ticker as ticker


# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus'] = False


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


def plt_im_bytes_session_capture_rates(chapters_list, session_rate):
    plt.xlabel('chapter')
    plt.ylabel('danger')
    plt.ylim(0., 1.02)
    fig, ax = plt.gcf(), plt.gca()
    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)
    ax.set_facecolor('white')
    ax.yaxis.set_ticks([0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1])
    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
    plt.bar(range(1, len(chapters_list) + 1), [1 - rate for rate in session_rate], color='red')
    with BytesIO() as output:
        plt.savefig(output, format='PNG')
        im_bytes = output.getvalue()
    width, height = fig.get_size_inches() * fig.get_dpi()
    plt.cla()
    return im_bytes, width, height


def plt_im_bytes_moving_average(chapters_list, stage_id, results, sigma, chapter_idx):
    """
    plot the moving average of NN rate
    :param chapters_list: a list of chapter names
    :param stage_id: the id of the stage
    :param results: a list of game results (an array of dictionaries of arrays of 0s and 1s)
    :param sigma: the sigma of the Gaussian distribution
    :param chapter_idx: the index of the chapter to plot, if -1, then plot the NN rate of the entire level
    :return:
    """
    averaged_rates_per_chapter = []
    for i in range(len(results)):
        # for each chapter, loop over all chapters to calculate weighted average with Gaussian filter
        total_cap = 0.
        total_attempt = 0.

        if chapter_idx != -1:
            for j in range(len(results)):
                weight = math.exp(-((i - j) ** 2) / (2 * sigma ** 2))
                stage_result = results[j][stage_id]  # now comes down to a single array
                if len(stage_result) > chapter_idx:  # ignore the case when player quits the game before finishing the chapter
                    result = stage_result[chapter_idx]
                    total_cap += result * weight
                    total_attempt += weight
        else:
            for j in range(len(results)):
                weight = math.exp(-((i - j) ** 2) / (2 * sigma ** 2))
                stage_result = results[j][stage_id]
                if len(stage_result) < len(chapters_list):
                    result = 0
                else:
                    result = 1
                    for k in range(len(chapters_list)):
                        if stage_result[k] == 0:
                            result = 0
                            break
                total_cap += result * weight
                total_attempt += weight
        averaged_rates = 0.
        if total_attempt > 0:
            averaged_rates = total_cap / total_attempt
        averaged_rates_per_chapter.append(averaged_rates)

    # reference: https://stackoverflow.com/questions/12608788/changing-the-tick-frequency-on-the-x-or-y-axis
    plt.xlabel('Time')
    plt.ylabel('cap rate')
    plt.ylim(0., 10.2)
    fig, ax = plt.gcf(), plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_facecolor('black')
    ax.yaxis.set_ticks([0, .5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9.5, 10])
    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
    plt.plot(range(len(results)), [rate * 10 for rate in averaged_rates_per_chapter], color='yellow')
    with BytesIO() as output:
        plt.savefig(output, format='PNG')
        im_bytes = output.getvalue()
    width, height = fig.get_size_inches() * fig.get_dpi()
    plt.cla()
    return im_bytes, width, height


def get_graph_layout(database, results, graph_option):
    """
    get the PySimpleGUI layout, sg.Graph objects and serialized image data array for each level
    :param database: the database storing the data
    :param results: the results to summarize over
    :param graph_option:
    :return: a tuple (layout_dict, graph_arr_dict), the latter contains one element for each graph for each stage
    """
    config_stages = database.get_config_stage_dict()
    layout_dict, graph_arr_dict = {}, {}
    graph_option_idx = graph_option[0]
    if graph_option_idx == 0:
        sigma = graph_option[2]
        for stage_id in config_stages:
            chapters_list = config_stages[stage_id]
            tab_layout = []
            graph_arr = []
            for i in range(-1, len(chapters_list)):
                graph_key = f'-GRAPH-{stage_id}-{i}-'
                im_data = plt_im_bytes_moving_average(chapters_list, stage_id, results, sigma, i)
                width, height = im_data[1], im_data[2]
                graph = sg.Graph(
                    canvas_size=(width, height),
                    graph_bottom_left=(0, 0),
                    graph_top_right=(width, height),
                    background_color='white',
                    key=graph_key,
                )
                tab_text = 'NMNB' if i == -1 else f'ch.{i}'
                tab_layout.append([sg.Tab(tab_text, [[graph]])])
                graph_arr.append((graph, graph_key, im_data))

            graph_layout = [[sg.TabGroup(tab_layout)]]

            graph_arr_dict[stage_id] = graph_arr
            layout_dict[stage_id] = graph_layout
    else:
        for stage_id in config_stages:
            chapters_list = config_stages[stage_id]
            cap, attempt, rate = database.cap_rates_from_results(results, stage_id)
            im_data = plt_im_bytes_session_capture_rates(chapters_list, rate)
            width, height = im_data[1], im_data[2]

            # reference:https://stackoverflow.com/questions/70474671/pysimplegui-graph-displaying-an-image-directly
            graph_key = f'-GRAPH-{stage_id}-'
            graph = sg.Graph(
                canvas_size=(width, height),
                graph_bottom_left=(0, 0),
                graph_top_right=(width, height),
                background_color='white',
                key=graph_key,
            )
            graph_layout = [[graph]]

            graph_arr_dict[stage_id] = [(graph, graph_key, im_data)]
            layout_dict[stage_id] = graph_layout
    return layout_dict, graph_arr_dict


def show_session_stat_menu(init_info, database, session_idx, graph_option):
    """
    show the game statistics
    :param init_info: the ui initialization info
    :param database: the database to store the data
    :param session_idx: the session to show statistics
    :param graph_option: information about what graph to show and how to show it
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

    stages_cap_rates = database.get_stages_cap_rates()
    (level_misses_arr, total_misses), (level_nn_rate_arr, total_nn_rate) = \
        database.compute_advanced_summary_statistics(stages_cap_rates)

    results = database.filter_results_by_attributes(graph_option[1])
    layout_dict, graph_arr_dict = get_graph_layout(database, results, graph_option)
    for stage_id in config_stages:
        stage_idx = database.get_stage_idx_from_id(stage_id)
        stat_layout = [[sg.Text(f'Average misses: {level_misses_arr[stage_idx]}')],
                       [sg.Text(f'Level NN rate: {level_nn_rate_arr[stage_idx]}')]] + \
            stat_layouts[stage_id]

        horizontal_layout = [[sg.Column(stat_layout), sg.Column(layout_dict[stage_id])]]
        layout.append([sg.Tab(stage_id,  horizontal_layout)])

    layout = [[sg.TabGroup(layout)],
              [sg.Text(f'Full game average misses: {total_misses}')],
              [sg.Text(f'NN rate: {total_nn_rate}')],
              [sg.Button('Back')]]

    window = sg.Window('thstat', layout, finalize=True)
    for stage_id in config_stages:
        for graph_info in graph_arr_dict[stage_id]:
            graph, graph_key, (im_bytes, width, height) = graph_info
            window[graph_key].draw_image(data=im_bytes, location=(0, height))

    while True:
        event, values = window.read()
        if event in [sg.WIN_CLOSED, 'Back']:
            break
    window.close()


