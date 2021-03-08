import tkinter.filedialog
import tkinter as tk
from tkinter import ttk
from GUI.mypandastable import NGraphTable

from objects.logfile import LogFile
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
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
        self.table = None  # type: NGraphTable
        self.log = None  # type: LogFile
        self.chart = None  # type: FigureCanvasTkAgg
        self.original_data = None
        self.grouped_data = None
        self.chart_frame = None
        self.chart_shown = False

        self.lbl = tk.Label(parent, text="Faili pole valitud")
        self.lbl.pack()

        self.toolbar = tk.Frame(self)
        self.toolbar.pack(side="top", anchor='n', fill='x')

        label = tk.Label(self.toolbar, text="N=")
        label.pack(side='left')
        self.NVar = tk.StringVar(self.toolbar, value='2')
        self.NVar.trace_add("write", lambda name, index, mode: self.change_n())
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
                                  command=self.toggle_grouped_values)
        checkbox.pack(side='left')

        save_button = tk.Button(self.toolbar, text="Salvesta faili", command=self.save_file)
        save_button.pack(side="left")

        self.table_frame = tk.Frame(self)
        self.table_frame.pack(side="left", expand=True, fill='both')




        matplotlib.rc('font', family='Arial')
        matplotlib.rc('font', **{'sans-serif': 'Arial',
                                 'family': 'sans-serif'})

    def choose_file(self):
        self.path = tk.filedialog.askopenfilename(title="Select file",
                                                  filetypes=(("text files", "*.txt"), ("all files", "*.*")))
        if self.path != "":
            self.lbl.configure(text=self.path)
        self.log = LogFile(self.path)
        data = self.log.get_ngraphs(int(self.NVar.get()))
        self.original_data = data
        data = self.group_data(data)
        self.table = NGraphTable(self.table_frame, dataframe=data, editable=False, rows=30)
        self.table.show()
        self.table.redraw()

        print(self.path)

    def group_data(self, data):
        data['n-graph'] = data['n-graph'].str.replace(' ', '⎵')
        data = data[['n-graph', 'time_taken']].groupby(data['n-graph'])
        data = data.agg({
            'n-graph': ['count'],
            'time_taken': ['mean']
        })
        data = data.reset_index()
        data = data.sort_values(('n-graph', 'count'), ascending=False)
        self.grouped_data = data
        return data

    def show_graphs(self):
        if self.path is None:
            self.lbl.configure(text="Faili pole valitud, ei saa analüüsida.")
            return
        if self.chart_shown:
            return

        self.chart_shown = True
        self.chart_frame = tk.Frame(self)
        self.chart_frame.pack(side="right", expand=True, fill='y')
        figure = plt.Figure(figsize=(10, 10), dpi=80)
        ax = figure.add_subplot(211)
        ax2 = figure.add_subplot(212)
        data = self.original_data
        self.chart = FigureCanvasTkAgg(figure, self.chart_frame)
        self.chart.get_tk_widget()
        self.chart.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        data['n-graph'].value_counts().sort_values(ascending=False)[:50].plot(kind='bar', legend=False, ax=ax)
        chart2data = data[['n-graph', 'time_taken']]
        chart2data.groupby(data['n-graph']).mean().sort_values('time_taken', ascending=False)[:50].plot(kind='bar',
                                                                                                        legend=False,
                                                                                                        ax=ax2)
        ax.set_title('N-graafide esinemine')
        ax2.set_title('N-graafide keskmine tippimis aeg')

    def hide_graphs(self):
        if not self.chart_shown:
            return
        if self.chart is not None:
            self.chart_shown = False
            self.chart_frame.destroy()

    def save_file(self):
        self.table.doExport()

    def toggle_grouped_values(self):
        self.table.clearData()
        self.table.destroy()
        if self.is_grouped_values.get():
            self.table = NGraphTable(self.table_frame, dataframe=self.grouped_data, editable=False)
        else:
            self.table = NGraphTable(self.table_frame, dataframe=self.original_data, editable=False)
        self.table.show()
        self.table.redraw()

    def change_n(self):
        try:
            new_n = int(self.NVar.get())
        except ValueError:
            print("invalid number in N field")
            return
        if new_n < 1:
            return
        self.table.clearData()
        self.table.destroy()
        data = self.log.get_ngraphs(new_n)
        data['n-graph'] = data['n-graph'].str.replace(' ', '⎵')
        self.original_data = data
        if self.is_grouped_values.get():
            data = self.group_data(data)
        self.table = NGraphTable(self.table_frame, dataframe=data, editable=False)
        self.table.show()
        self.table.redraw()


def start():
    root = tk.Tk()
    root.geometry('1920x1080')
    MainApplication(root).pack(fill="both", expand=True)
    root.mainloop()
