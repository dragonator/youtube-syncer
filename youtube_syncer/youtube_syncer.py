from gui import Application

try:
    import tkinter as tk
except:
    import Tkinter as tk


def main():
    parent = tk.Tk()
    app = Application(parent)

    app.mainloop()

if __name__ == '__main__':
    main()
