import tkinter.filedialog
import tkinter as tk
from tkinter import ttk

from objects.logfile import LogFile
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from GUI.simpleTable import SimpleTable
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def popup_bonus(message):
    win = tk.Toplevel()
    center(win)
    win.title("Fail salvestatud")
    l = tk.Label(win, text=message)
    l.pack()

    b = ttk.Button(win, text="Ok", command=win.destroy)
    b.pack()


def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.path = None
        self.figure = None
        self.table = None
        self.log = None  # type: LogFile

        self.lbl = tk.Label(parent, text="Faili pole valitud")
        self.lbl.pack()

        choose_button = tk.Button(parent, text="Vali fail", command=self.choose_file)
        choose_button.pack(side="top")

        start_button = tk.Button(parent, text="Demo analüüs", command=self.demo_analysis)
        start_button.pack()

        save_button = tk.Button(parent, text="Salvesta faili", command=self.save_file)
        save_button.pack()

        matplotlib.rc('font', family='Arial')
        matplotlib.rc('font', **{'sans-serif': 'Arial',
                                 'family': 'sans-serif'})

    def choose_file(self):
        self.path = tk.filedialog.askopenfilename(title="Select file",
                                                  filetypes=(("text files", "*.txt"), ("all files", "*.*")))
        if self.path != "":
            self.lbl.configure(text=self.path)
        self.log = LogFile(self.path)
        self.log.get_ngraphs(2)
        self.table = SimpleTable(self.parent, len(self.log.get_ngraphs(2)) + 1, 7)
        self.table.set_header(['Ngraaf', 'n', 'algus aeg', 'lõpp aeg', 'kulunud aeg', 'algus index', 'lõpp index'])
        for i, item in enumerate(self.log.get_ngraphs(2)):
            for j, elem in enumerate(item.to_list()):
                self.table.set(i + 1, j, elem)
        self.table.pack()

        print(self.path)

    def demo_analysis(self):
        if self.path is None:
            self.lbl.configure(text="Faili pole valitud, ei saa analüüsida.")
            return
        self.log.write_to_csv_path("temp.csv", n=2)
        self.table.pack_forget()
        data = pd.read_csv('temp.csv', encoding='utf8')
        figure = plt.Figure(figsize=(20, 20), dpi=100)
        ax = figure.add_subplot(221)
        ax2 = figure.add_subplot(222)

        chart_type = FigureCanvasTkAgg(figure, root)
        chart_type.get_tk_widget().pack()
        data['ngraph'].value_counts().sort_values(ascending=False)[:50].plot(kind='bar', legend=False, ax=ax)

        chart2data = data[['ngraph', 'time_taken']]
        chart2data.groupby(data['ngraph']).mean().sort_values('time_taken', ascending=False)[:50].plot(kind='bar',
                                                                                                       legend=False,
                                                                                                       ax=ax2)
        ax.set_title('Digraafide esinemine')
        ax2.set_title('Digraafide keskmine tippimis aeg')

    def save_file(self):
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension=".csv",
                                        filetypes=(("csv file", "*.csv"), ("all files", "*.*")))
        if self.log is None:
            self.lbl.configure(text="Faili pole valitud, ei saa analüüsida.")
            return
        self.log.write_to_csv_file(f)
        f.close()
        popup_bonus("Fail salvestatud.")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry('1920x1080')
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
