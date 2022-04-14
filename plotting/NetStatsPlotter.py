import json
import matplotlib.pyplot as plt

class NetStatsPlotter:
    def __init__(self, save_folder, plot_format):
        self.save_folder = save_folder
        self.plot_format = plot_format

    def plot_net_stats(self, net_data_file):
        x_stats, y_stats = self.__parse_net_stats_file(net_data_file)
        for i in y_stats:
            plt.plot(x_stats, y_stats[i][0], 'k', linewidth=1)
            plt.grid()
            plt.xlim(xmin=0, xmax=x_stats[-1])
            plt.xlabel(y_stats[i][1]["x"])
            plt.ylabel(y_stats[i][1]["y"])
            plt.title(y_stats[i][1]["title"])
            plt.savefig("{}/{}.{}".format(self.save_folder, i, self.plot_format))
            plt.clf()

    def plot_queue_len(self, qlen_data_file):
        x_stats, y_stats = self.__parse_queue_len_data_file(qlen_data_file)
        plt.plot(x_stats, y_stats, 'k', linewidth=1)
        plt.grid()
        plt.xlim(xmin=0, xmax=x_stats[-1])
        plt.xlabel("Время (с)")
        plt.ylabel("Размер очереди (пакеты)")
        plt.title("Размер очереди в течении времени")
        plt.savefig("{}/queue_len.{}".format(self.save_folder, self.plot_format))

    def __parse_net_stats_file(self, net_data_file):
        net_data = open(net_data_file, "r")
        raw_data = json.load(net_data)
        x = []
        y = {
            "bytes": [[], {"title": "Количество переданных байт", "x": "Время (с)", "y": "MB"}],
            "cwnd": [[], {"title": "Окно перегрузки", "x": "Время (с)", "y": "cwnd"}],
            "MTU": [[], {"title": "Максимальный размер пакета", "x": "Время (с)", "y": "B"}],
            "retransmits": [[], {"title": "Повторно переданные пакеты", "x": "Время (с)", "y": "Количество пакетов"}],
            "rtt": [[], {"title": "Круговая задержка", "x": "Время (с)", "y": "ms"}],
            "rttvar": [[], {"title": "Отклонение круговой задержки", "x": "Время (с)", "y": "ms"}],
            "throughput": [[], {"title": "Пропускная способность", "x": "Время (с)", "y": "MBits"}]
        }
        for i in raw_data["intervals"]:
            tmp_data = i["streams"][0]
            x.append(tmp_data["start"])
            y["bytes"][0].append(tmp_data["bytes"] / 1024 / 1024)
            y["cwnd"][0].append(tmp_data["snd_cwnd"] / 1024)
            y["MTU"][0].append(tmp_data["pmtu"])
            y["retransmits"][0].append(tmp_data["retransmits"])
            y["rtt"][0].append(tmp_data["rtt"] / 1000)
            y["rttvar"][0].append(tmp_data["rttvar"] / 1000)
            y["throughput"][0].append(tmp_data["bits_per_second"] / 1000000)
        return [x, y]

    def __parse_queue_len_data_file(self, qlen_data_file):
        qlen_data = open(qlen_data_file, "r")
        x_stats = []
        y_stats = []
        for line in qlen_data:
            line = line.split(" ")
            x_stats.append(float(line[0]))
            y_stats.append(float(line[1]))
        return [x_stats, y_stats]