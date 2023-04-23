import matplotlib
from matplotlib import pyplot as plt
from io import BytesIO


plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def plt_im_bytes_session_capture_rates(database, session):
    chapters_list = database.config['Chapters']
    capture_list = [0] * len(chapters_list)
    total_list = [0] * len(chapters_list)
    for i, run in enumerate(session['Result']):
        for j, success in enumerate(run):
            capture_list[j] += success
            total_list[j] += 1
    capture_rate = [capture_list[i] / total_list[i] if total_list[i] > 0 else 0 for i in range(len(capture_list))]
    plt.bar(chapters_list, capture_rate)
    plt.xlabel('section')
    plt.ylabel('NN rate')
    plt.ylim(0., 1.)
    with BytesIO() as output:
        plt.savefig(output, format='PNG')
        im_bytes = output.getvalue()
    fig = plt.gcf()
    width, height = fig.get_size_inches() * fig.get_dpi()
    plt.cla()
    return im_bytes, width, height


