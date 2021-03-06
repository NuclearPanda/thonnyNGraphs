import tkinter as tk
import tkinter.filedialog
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from gui.ngraphtable import NGraphTable
from objects.logfile import LogFile


def popup_message1(parent, message):
    win = tk.Toplevel(parent)
    center(win)
    win.title(message)
    lbl = tk.Label(win, text=message)
    lbl.pack()

    b = ttk.Button(win, text="Ok", command=win.destroy)
    b.pack()


def popup_msg(msg):
    popup = tk.Tk()
    popup.wm_title("Viga")
    label = ttk.Label(popup, text=msg)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Ok", command=popup.destroy)
    B1.pack()
    center(popup)


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


def group_data(data):
    if data.empty:
        raise Exception("Data empty, should never have gotten this far")
    data = data[['n-graaf', 'aeg']].groupby(data['n-graaf'])
    data = data.agg({
        'n-graaf': ['count'],
        'aeg': ['mean', 'min', 'max']
    })
    data = data.reset_index()
    data = data.sort_values(('n-graaf', 'count'), ascending=False, kind='mergesort')
    return data


def perform_replacements(df):
    df['n-graaf'] = df['n-graaf'].str.replace(' ', '⎵')
    df['n-graaf'] = df['n-graaf'].str.replace('\n', '⏎')
    return df


def get_with_default(var, func, default):
    try:
        out = func(var.get())
    except Exception as e:
        print(e, ", error in getting value, using default")
        out = default
    return out


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
        self.controls = []

        self.lbl = tk.Label(parent, text="Faili pole valitud")
        self.lbl.pack()

        self.toolbar = tk.Frame(self)
        self.toolbar.pack(side="top", anchor='n', fill='x')

        choose_button = tk.Button(self.toolbar, text="Vali fail", command=self.choose_file)
        choose_button.pack(side="left")

        show_graphs_button = tk.Button(self.toolbar, text="Näita/peida graafikud", command=self.toggle_graphs,
                                       state="disabled")
        show_graphs_button.pack(side="left")
        self.controls.append(show_graphs_button)

        group_table_button = tk.Button(self.toolbar, text="Grupeeri tabel", command=self.toggle_grouped_values,
                                       state="disabled")
        group_table_button.pack(side="left")
        self.controls.append(group_table_button)

        save_button = tk.Button(self.toolbar, text="Salvesta faili", command=self.save_file, state="disabled")
        save_button.pack(side="left")
        self.controls.append(save_button)

        self.is_grouped = True

        label = tk.Label(self.toolbar, text="N=")
        label.pack(side='left')
        self.NVar = tk.StringVar(self.toolbar, value='2')
        self.NVar.trace_add("write", lambda name, index, mode: self.change_n())
        entryN = tk.Entry(self.toolbar, textvariable=self.NVar, width=5, state="disabled")
        entryN.pack(side='left')
        self.controls.append(entryN)

        label = tk.Label(self.toolbar, text="Min aeg:")
        label.pack(side='left')
        self.time_cutoff_min_var = tk.DoubleVar(self.toolbar, value=0)
        self.time_cutoff_min_var.trace_add("write", lambda name, index, mode: self.filter_table())
        time_cutoff_min_entry = tk.Entry(self.toolbar, textvariable=self.time_cutoff_min_var, width=5, state="disabled")
        time_cutoff_min_entry.pack(side='left')
        self.controls.append(time_cutoff_min_entry)

        self.time_cutoff_max_var = tk.DoubleVar(self.toolbar, value=100)
        self.time_cutoff_max_var.trace_add("write", lambda name, index, mode: self.filter_table())
        label = tk.Label(self.toolbar, text="Max aeg:")
        label.pack(side='left')
        time_cutoff_max_entry = tk.Entry(self.toolbar, textvariable=self.time_cutoff_max_var, width=5, state="disabled")
        time_cutoff_max_entry.pack(side='left')
        self.controls.append(time_cutoff_max_entry)

        label = tk.Label(self.toolbar, text="Otsing:")
        label.pack(side='left')
        self.filter_var = tk.StringVar(self.toolbar, value='')
        self.filter_var.trace_add("write", lambda name, index, mode: self.filter_table())
        filter_entry = tk.Entry(self.toolbar, textvariable=self.filter_var, width=10, state="disabled")
        filter_entry.pack(side='left')
        self.controls.append(filter_entry)

        self.table_frame = tk.Frame(self)
        self.table_frame.pack(side="left", expand=True, fill='both')

    def enable_buttons(self):
        for item in self.controls:
            item["state"] = "normal"

    def choose_file(self):
        old_path = self.path
        self.path = tk.filedialog.askopenfilename(title="Select file",
                                                  filetypes=(("text files", "*.txt"), ("all files", "*.*")))
        self.log = LogFile(self.path)
        try:
            data = self.log.get_ngraphs(get_with_default(self.NVar, int, 2))
        except Exception as e:
            print(e)
            popup_msg("Failis pole n-graafe või faili vorming on oodatust erinev")
            self.path = old_path
            return
        if data.empty:
            popup_msg("Failis pole n-graafe või faili vorming on oodatust erinev")
            self.path = old_path
            return

        self.lbl.configure(text=self.path)
        data = perform_replacements(data)
        self.original_data = data
        data = self.get_filtered_data()
        data = group_data(data)
        self.grouped_data = data
        self.table = NGraphTable(self.table_frame, dataframe=data, editable=False, rows=30)
        self.table.show()
        self.table.redraw()
        self.enable_buttons()
        self.redraw_graphs()

    def toggle_graphs(self):
        if self.path is None:
            self.lbl.configure(text="Faili pole valitud, ei saa analüüsida.")
            return
        if self.chart_shown:
            self.chart_shown = False
            self.chart_frame.destroy()
            return

        self.chart_shown = True
        self.chart_frame = tk.Frame(self)
        self.chart_frame.pack(side="right", expand=True,
                              fill='y')  # TODO could probably not do this every time and get better responsiveness
        figure = plt.Figure(figsize=(10, 10), dpi=80)
        ax = figure.add_subplot(211)
        ax2 = figure.add_subplot(212)
        data = self.get_filtered_data()
        self.chart = FigureCanvasTkAgg(figure, self.chart_frame)
        self.chart.get_tk_widget()
        self.chart.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        data['n-graaf'].groupby(data['n-graaf']).count().sort_values(ascending=False, kind='mergesort')[:25][::-1].plot(kind='barh', legend=False, ax=ax)
        chart2data = data[['n-graaf', 'aeg']]
        chart2data.groupby(data['n-graaf']).mean().sort_values('aeg', ascending=False, kind='mergesort')[:25][::-1].plot(kind='barh', legend=False, ax=ax2)
        ax.set_title('N-graafide esinemine')
        ax2.set_title('N-graafide keskmine tippimise aeg')

    def redraw_graphs(self):
        if self.chart_shown:
            self.toggle_graphs()
            self.toggle_graphs()

    def hide_graphs(self):
        if not self.chart_shown:
            return
        if self.chart is not None:
            self.chart_shown = False
            self.chart_frame.destroy()

    def save_file(self):
        if self.table.doExport():
            popup_msg("Fail salvestatud")

    def toggle_grouped_values(self):
        self.is_grouped = not self.is_grouped
        self.filter_table()

    def change_n(self):
        new_n = get_with_default(self.NVar, int, 0)
        if new_n < 1:
            return
        data = self.log.get_ngraphs(new_n)
        data = perform_replacements(data)
        self.original_data = data
        self.filter_table()

    def change_time_cutoff(self, data):
        min_cutoff = get_with_default(self.time_cutoff_min_var, float, 0)
        max_cutoff = get_with_default(self.time_cutoff_max_var, float, 100)
        data = data.loc[(data['aeg'] >= min_cutoff) & (data['aeg'] <= max_cutoff)]
        return data

    def filter_table_by_str(self, data):
        filter_str = self.filter_var.get()
        filter_str = filter_str.replace(' ', '⎵')
        if filter_str == '':
            return data
        filtered_data = data[data['n-graaf'].str.contains(filter_str, regex=False)]
        return filtered_data

    def filter_table(self):
        data = self.get_filtered_data()
        if self.is_grouped:
            data = group_data(data)
            self.grouped_data = data
        self.table.model.df = data
        self.table.redraw()
        self.table.autoResizeColumns()
        self.redraw_graphs()

    def get_filtered_data(self):
        data = self.original_data
        data = self.change_time_cutoff(data)
        data = self.filter_table_by_str(data)
        return data

    def get_current_data(self):
        if self.is_grouped:
            return self.grouped_data
        else:
            return self.original_data


def start():
    root = tk.Tk()
    root.geometry('1200x800')
    root.title('N-graafide analüsaator')
    MainApplication(root).pack(fill="both", expand=True)
    root.mainloop()
