import matplotlib
from matplotlib import pyplot as plt
from io import BytesIO
import stat_database


# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus'] = False


def plt_im_bytes_session_capture_rates(chapters_list, session_rate):
    plt.bar(range(1, len(chapters_list) + 1), session_rate)
    plt.xlabel('session')
    plt.ylabel('NN rate')
    plt.ylim(0., 1.)
    with BytesIO() as output:
        plt.savefig(output, format='PNG')
        im_bytes = output.getvalue()
    fig = plt.gcf()
    width, height = fig.get_size_inches() * fig.get_dpi()
    plt.cla()
    return im_bytes, width, height


