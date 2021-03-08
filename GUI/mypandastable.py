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
                                                               ("excel", "*.xls"),
                                                               ("html", "*.html"),
                                                               ("All files", "*.*")])
        if filename:
            self.model.save(filename)
        return
