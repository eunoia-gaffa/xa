from tkinter import *
from tkinter import ttk

from dotenv import dotenv_values

from xero.automator import XeroAutomator

if __name__ == "__main__":
    root = Tk()
    root.title("XerAutomator")
    root.iconbitmap('xero.ico')

    def fill_timesheets_wrapper():
        print("Fill timesheets")
        config = dotenv_values()
        xa = XeroAutomator(config)

        xa.login()
        xa.go_to_time_entries()
        xa.eight_hours_today()

        del xa
        root.destroy()

    frm = ttk.Frame(root, padding=10)
    frm.grid()
    ttk.Label(frm, text="Fill today's timesheet?").grid(
        column=0, row=0, padx=5, pady=5)
    ttk.Button(frm, text="Yes", command=fill_timesheets_wrapper).grid(
        column=0, row=1, padx=5, pady=5)
    ttk.Button(frm, text="No", command=root.destroy).grid(
        column=1, row=1, padx=5, pady=5)

    root.mainloop()
