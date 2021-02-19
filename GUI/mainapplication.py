import tkinter.filedialog
import tkinter as tk
from tkinter import ttk
import pandastable

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
        self.table = None  # type: pandastable.Table
        self.log = None  # type: LogFile
        self.chart = None  # type: FigureCanvasTkAgg
        self.origianl_data = None
        self.grouped_data = None

        self.lbl = tk.Label(parent, text="Faili pole valitud")
        self.lbl.pack()

        self.toolbar = tk.Frame(self)
        self.toolbar.pack(side="top", anchor='n', fill='x')

        label = tk.Label(self.toolbar, text="N=")
        label.pack(side='left')
        self.NVar = tk.StringVar(self.toolbar, value='2')
        entryN = tk.Entry(self.toolbar, textvariable=self.NVar)
        entryN.pack(side='left')

        choose_button = tk.Button(self.toolbar, text="Vali fail", command=self.choose_file)
        choose_button.pack(side="left")

        show_graphs_button = tk.Button(self.toolbar, text="Näita graafe", command=self.show_graphs)
        show_graphs_button.pack(side="left")

        hide_graphs_button = tk.Button(self.toolbar, text="Peida graafid", command=self.hide_graphs)
        hide_graphs_button.pack(side="left")

        self.is_grouped_values = tk.IntVar(self.toolbar, 1)
        checkbox = tk.Checkbutton(self.toolbar, text="Grupeeritud tabel", variable=self.is_grouped_values,
                                  command=self.group_values)
        checkbox.pack(side='left')

        save_button = tk.Button(self.toolbar, text="Salvesta faili", command=self.save_file)
        save_button.pack(side="left")

        self.table_frame = tk.Frame(self)
        self.table_frame.pack(expand=False, fill='both')

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
        # self.table = SimpleTable(self.parent, len(self.log.get_ngraphs(2)) + 1, 7)
        # self.table.set_header(['Ngraaf', 'n', 'algus aeg', 'lõpp aeg', 'kulunud aeg', 'algus index', 'lõpp index'])
        # for i, item in enumerate(self.log.get_ngraphs(2)):
        #     for j, elem in enumerate(item.to_list()):
        #         self.table.set(i + 1, j, elem)
        # self.table.pack()

        self.log.write_to_csv_path("temp.csv", n=int(self.NVar.get()))
        data = pd.read_csv('temp.csv', encoding='utf8')
        self.origianl_data = data
        data = data[['ngraph', 'time_taken']].groupby(data['ngraph'])
        data = data.agg({
            'ngraph': ['count'],
            'time_taken': ['mean']
        })
        data = data.reset_index()
        data = data.sort_values(('ngraph', 'count'), ascending=False)
        self.grouped_data = data
        self.table = pandastable.Table(self.table_frame, dataframe=data, editable=False)
        self.table.show()

        print(self.path)

    def show_graphs(self):
        if self.path is None:
            self.lbl.configure(text="Faili pole valitud, ei saa analüüsida.")
            return

        figure = plt.Figure(figsize=(20, 20), dpi=100)
        ax = figure.add_subplot(221)
        ax2 = figure.add_subplot(222)
        data = pd.read_csv('temp.csv', encoding='utf8')
        self.chart = FigureCanvasTkAgg(figure, root)
        self.chart.get_tk_widget().pack()
        data['ngraph'].value_counts().sort_values(ascending=False)[:50].plot(kind='bar', legend=False, ax=ax)
        tk.Frame()
        chart2data = data[['ngraph', 'time_taken']]
        chart2data.groupby(data['ngraph']).mean().sort_values('time_taken', ascending=False)[:50].plot(kind='bar',
                                                                                                       legend=False,
                                                                                                       ax=ax2)
        ax.set_title('Digraafide esinemine')
        ax2.set_title('Digraafide keskmine tippimis aeg')

    def hide_graphs(self):
        if self.chart is not None:
            self.chart.get_tk_widget().pack_forget()

    def save_file(self):
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension=".csv",
                                        filetypes=(("csv file", "*.csv"), ("all files", "*.*")))
        if self.log is None:
            self.lbl.configure(text="Faili pole valitud, ei saa analüüsida.")
            return
        self.log.write_to_csv_file(f)
        f.close()
        popup_bonus("Fail salvestatud.")

    def group_values(self):
        self.table.clearData()
        self.table.destroy()
        if self.is_grouped_values.get():
            self.table = pandastable.Table(self.table_frame, dataframe=self.grouped_data, editable=False)
        else:
            self.table = pandastable.Table(self.table_frame, dataframe=self.origianl_data, editable=False)
        self.table.show()


def start():
    root = tk.Tk()
    root.geometry('1920x1080')
    MainApplication(root).pack(fill="both", expand=True)
    root.mainloop()
