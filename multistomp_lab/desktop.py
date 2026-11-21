"""Desktop prototype: inspect six ZDL slots. Does NOT execute DSP or process audio.

Run on Windows 10: python -m multistomp_lab.desktop
Python 3.10+ with Tkinter required.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .zdl_cli import inspect_file


class MultiStompDesktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Zezo HxCx MultiStomp Lab — ZDL inspector (no audio)")
        self.geometry("850x520")
        self.minsize(700, 420)
        self.slots = [None] * 6
        self.buttons = []
        self.labels = []
        ttk.Label(self, text="MultiStomp Lab — 6-slot ZDL inspector",
                  font=("Segoe UI", 16, "bold")).pack(pady=(16, 4))
        ttk.Label(self, text="INSPECTION ONLY: no DSP emulation, ASIO, or audio output.",
                  foreground="#a33").pack(pady=(0, 12))
        strip = ttk.Frame(self)
        strip.pack(fill="x", padx=12)
        for index in range(6):
            frame = ttk.LabelFrame(strip, text=f"Slot {index + 1}")
            frame.grid(row=0, column=index, sticky="nsew", padx=3)
            strip.columnconfigure(index, weight=1)
            label = ttk.Label(frame, text="Empty", wraplength=110)
            label.pack(padx=5, pady=6)
            ttk.Button(frame, text="Load .ZDL",
                       command=lambda i=index: self.load_slot(i)).pack(padx=5, pady=3)
            ttk.Button(frame, text="Clear",
                       command=lambda i=index: self.clear_slot(i)).pack(padx=5, pady=(0, 8))
            self.labels.append(label)
        ttk.Label(self, text="Inspection details").pack(anchor="w", padx=14, pady=(14, 3))
        self.details = tk.Text(self, wrap="word", state="disabled")
        self.details.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.show("Select a slot and load a legally obtained .ZDL file.\n"
                  "The program checks the container and embedded ELF without executing code.")

    def show(self, content):
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", content)
        self.details.configure(state="disabled")

    def clear_slot(self, index):
        self.slots[index] = None
        self.labels[index].configure(text="Empty")
        self.show(f"Slot {index + 1} cleared.")

    def load_slot(self, index):
        path = filedialog.askopenfilename(title=f"Slot {index + 1}: choose ZDL",
                                          filetypes=[("Zoom ZDL", "*.zdl *.ZDL"),
                                                     ("All files", "*.*")])
        if not path:
            return
        try:
            import json
            report = inspect_file(path)
        except (OSError, ValueError, Exception) as exc:
            # Malformed/untrusted files must not terminate the desktop UI.
            messagebox.showerror("ZDL inspection failed", str(exc))
            return
        self.slots[index] = report
        self.labels[index].configure(text=report["file_name"])
        self.show(json.dumps({"slot": index + 1, **report},
                             ensure_ascii=False, indent=2, default=str))


def main():
    MultiStompDesktop().mainloop()


if __name__ == "__main__":
    main()
