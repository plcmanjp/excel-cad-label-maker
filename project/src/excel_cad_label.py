"""Windows label utility. Original developer: 직장인. Continuing developer: plcmanjp."""
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD
from label_ui import App, APP_TITLE


def main():
    root = TkinterDnD.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
