from tkinter import filedialog

import pandastable


class NGraphTable(pandastable.Table):
    def clearData(self, evt=None):
        if self.allrows:
            self.deleteColumn()
            return
        rows = self.multiplerowlist
        cols = self.multiplecollist
        self.deleteCells(rows, cols, True)
        return

    def doExport(self, filename=None):
        if filename is None:
            filename = filedialog.asksaveasfilename(parent=self.master,
                                                    defaultextension='.csv',
                                                    filetypes=[("csv", "*.csv"),
                                                               ("excel", "*.xlsx"),
                                                               ("All files", "*.*")])
        if filename:
            if filename[-4:] == 'xlsx':
                self.model.df.to_excel(filename, encoding='utf8')
            else:
                self.model.df.to_csv(filename, encoding='utf8', sep=";", index=False)
        else:
            return False
        return True
