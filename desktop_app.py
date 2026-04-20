import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import time
import math


# ─────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────
BG = "#1e1e2e"
BG2 = "#2a2a3e"
BG3 = "#313145"
ACCENT = "#7c6af7"
ACCENT2 = "#a89afa"
FG = "#cdd6f4"
FG2 = "#a6adc8"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"
BORDER = "#45475a"


def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=[0, 0, 0, 0])
    style.configure(
        "TNotebook.Tab",
        background=BG2,
        foreground=FG2,
        padding=[18, 8],
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", BG3), ("active", BG3)],
        foreground=[("selected", ACCENT2), ("active", FG)],
    )
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
    style.configure(
        "TButton",
        background=BG3,
        foreground=FG,
        font=("Segoe UI", 10),
        borderwidth=0,
        relief="flat",
        padding=[10, 6],
    )
    style.map("TButton", background=[("active", ACCENT), ("pressed", ACCENT)])
    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground="#ffffff",
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
        padding=[12, 7],
    )
    style.map("Accent.TButton", background=[("active", ACCENT2)])
    style.configure("TScrollbar", background=BG2, troughcolor=BG, arrowcolor=FG2, borderwidth=0)
    style.configure("TEntry", fieldbackground=BG2, foreground=FG, insertcolor=FG, borderwidth=0, relief="flat")
    style.configure("TCombobox", fieldbackground=BG2, foreground=FG, background=BG3, borderwidth=0)
    style.map("TCombobox", fieldbackground=[("readonly", BG2)])
    style.configure("TCheckbutton", background=BG, foreground=FG, font=("Segoe UI", 10))
    style.map("TCheckbutton", background=[("active", BG)])
    style.configure("Treeview", background=BG2, foreground=FG, fieldbackground=BG2, rowheight=28, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", background=BG3, foreground=ACCENT2, font=("Segoe UI", 10, "bold"), borderwidth=0)
    style.map("Treeview", background=[("selected", ACCENT)])


# ─────────────────────────────────────────────
# TEXT EDITOR
# ─────────────────────────────────────────────
class TextEditor(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_file = None
        self.modified = False
        self._build()

    def _build(self):
        toolbar = tk.Frame(self, bg=BG2, pady=6, padx=6)
        toolbar.pack(fill="x", side="top")

        def btn(text, cmd, color=BG3):
            b = tk.Button(
                toolbar, text=text, command=cmd, bg=color, fg=FG,
                relief="flat", bd=0, padx=12, pady=5, font=("Segoe UI", 9, "bold"),
                cursor="hand2", activebackground=ACCENT, activeforeground="#fff"
            )
            b.pack(side="left", padx=3)
            return b

        btn("New", self.new_file)
        btn("Open", self.open_file)
        btn("Save", self.save_file, ACCENT)
        btn("Save As", self.save_as)
        btn("Find & Replace", self.find_replace)

        self.status = tk.Label(toolbar, text="New file", bg=BG2, fg=FG2, font=("Segoe UI", 9))
        self.status.pack(side="right", padx=8)

        text_frame = tk.Frame(self, bg=BG)
        text_frame.pack(fill="both", expand=True, padx=10, pady=8)

        self.line_nums = tk.Text(
            text_frame, width=4, bg=BG2, fg=FG2, font=("Consolas", 11),
            state="disabled", padx=6, pady=6, relief="flat", bd=0
        )
        self.line_nums.pack(side="left", fill="y")

        self.text = tk.Text(
            text_frame, bg=BG2, fg=FG, insertbackground=ACCENT2, font=("Consolas", 11),
            wrap="none", padx=8, pady=6, relief="flat", bd=0,
            selectbackground=ACCENT, selectforeground="#fff", undo=True
        )
        vsb = ttk.Scrollbar(text_frame, orient="vertical", command=self._yscroll)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        hsb.pack(fill="x", padx=10)

        self.text.bind("<KeyRelease>", self._on_change)
        self.text.bind("<MouseWheel>", self._on_change)
        self._update_lines()

    def _yscroll(self, *args):
        self.text.yview(*args)
        self._update_lines()

    def _on_change(self, event=None):
        self.modified = True
        self._update_status()
        self._update_lines()

    def _update_lines(self, event=None):
        self.line_nums.config(state="normal")
        self.line_nums.delete("1.0", "end")
        count = int(self.text.index("end-1c").split(".")[0])
        self.line_nums.insert("1.0", "\n".join(str(i) for i in range(1, count + 1)))
        self.line_nums.config(state="disabled")

    def _update_status(self):
        row, col = self.text.index("insert").split(".")
        name = self.current_file or "New file"
        mod = " •" if self.modified else ""
        self.status.config(text=f"{name}{mod}   Ln {row}, Col {int(col)+1}")

    def new_file(self):
        if self.modified and not messagebox.askyesno("Unsaved Changes", "Discard current file?"):
            return
        self.text.delete("1.0", "end")
        self.current_file = None
        self.modified = False
        self._update_status()

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("All Files", "*.*"), ("Text", "*.txt"), ("Python", "*.py")])
        if path:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                self.text.delete("1.0", "end")
                self.text.insert("1.0", f.read())
            self.current_file = path
            self.modified = False
            self._update_status()
            self._update_lines()

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", "end-1c"))
            self.modified = False
            self._update_status()
        else:
            self.save_as()

    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt"), ("Python", "*.py"), ("All", "*.*")])
        if path:
            self.current_file = path
            self.save_file()

    def find_replace(self):
        win = tk.Toplevel(self)
        win.title("Find & Replace")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="Find:", bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        find_var = tk.StringVar()
        tk.Entry(win, textvariable=find_var, bg=BG2, fg=FG, insertbackground=FG, relief="flat", font=("Segoe UI", 10), width=24).grid(row=0, column=1, padx=10, pady=8)

        tk.Label(win, text="Replace:", bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=1, column=0, padx=10, pady=4, sticky="w")
        rep_var = tk.StringVar()
        tk.Entry(win, textvariable=rep_var, bg=BG2, fg=FG, insertbackground=FG, relief="flat", font=("Segoe UI", 10), width=24).grid(row=1, column=1, padx=10, pady=4)

        def do_find():
            self.text.tag_remove("highlight", "1.0", "end")
            word = find_var.get()
            if not word:
                return
            start = "1.0"
            while True:
                pos = self.text.search(word, start, "end")
                if not pos:
                    break
                end = f"{pos}+{len(word)}c"
                self.text.tag_add("highlight", pos, end)
                start = end
            self.text.tag_config("highlight", background=YELLOW, foreground="#1e1e2e")

        def do_replace():
            word = find_var.get()
            rep = rep_var.get()
            content = self.text.get("1.0", "end-1c")
            new = content.replace(word, rep)
            self.text.delete("1.0", "end")
            self.text.insert("1.0", new)
            win.destroy()

        btn_frame = tk.Frame(win, bg=BG)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Find All", command=do_find, bg=BG3, fg=FG, relief="flat", padx=12, pady=5, font=("Segoe UI", 9)).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Replace All", command=do_replace, bg=ACCENT, fg="#fff", relief="flat", padx=12, pady=5, font=("Segoe UI", 9)).pack(side="left", padx=6)


# ─────────────────────────────────────────────
# CALCULATOR
# ─────────────────────────────────────────────
class Calculator(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.expr = ""
        self.history = []
        self._build()

    def _build(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(expand=True, fill="both", padx=30, pady=20)

        self.display = tk.Label(outer, text="0", bg=BG2, fg=FG, font=("Segoe UI", 28, "bold"),
                                anchor="e", padx=16, pady=16, relief="flat")
        self.display.pack(fill="x", pady=(0, 4))

        self.sub_display = tk.Label(outer, text="", bg=BG2, fg=FG2, font=("Segoe UI", 12),
                                    anchor="e", padx=16, pady=4)
        self.sub_display.pack(fill="x", pady=(0, 10))

        buttons = [
            ["C", "±", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["√", "0", ".", "="],
        ]

        grid = tk.Frame(outer, bg=BG)
        grid.pack(fill="both", expand=True)

        for r, row in enumerate(buttons):
            for c, label in enumerate(row):
                self._make_btn(grid, label, r, c)

        history_frame = tk.Frame(outer, bg=BG)
        history_frame.pack(fill="x", pady=(12, 0))
        tk.Label(history_frame, text="History", bg=BG, fg=FG2, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.history_box = tk.Listbox(
            history_frame, bg=BG2, fg=FG2, font=("Consolas", 10), height=4,
            relief="flat", bd=0, selectbackground=ACCENT, selectforeground="#fff"
        )
        self.history_box.pack(fill="x")

    def _make_btn(self, parent, label, row, col):
        op_color = ACCENT if label in "÷×−+=√" else (RED if label == "C" else BG3)
        eq_color = GREEN if label == "=" else op_color
        if label == "=":
            eq_color = ACCENT

        def cmd(l=label):
            self._press(l)

        btn = tk.Button(
            parent, text=label, command=cmd, bg=eq_color, fg="#fff" if label in "C=" else FG,
            font=("Segoe UI", 14, "bold"), relief="flat", bd=0, cursor="hand2",
            activebackground=ACCENT2, activeforeground="#fff"
        )
        btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew", ipady=10)
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)

    def _press(self, key):
        if key == "C":
            self.expr = ""
            self.display.config(text="0")
            self.sub_display.config(text="")
        elif key == "=":
            try:
                expr = self.expr.replace("÷", "/").replace("×", "*").replace("−", "-")
                result = eval(expr)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                entry = f"{self.expr} = {result}"
                self.history.append(entry)
                self.history_box.insert("end", entry)
                self.history_box.yview("end")
                self.sub_display.config(text=self.expr)
                self.display.config(text=str(result))
                self.expr = str(result)
            except Exception:
                self.display.config(text="Error")
                self.expr = ""
        elif key == "±":
            if self.expr and self.expr[0] == "-":
                self.expr = self.expr[1:]
            elif self.expr:
                self.expr = "-" + self.expr
            self.display.config(text=self.expr or "0")
        elif key == "%":
            try:
                val = eval(self.expr) / 100
                self.expr = str(val)
                self.display.config(text=self.expr)
            except Exception:
                pass
        elif key == "√":
            try:
                val = math.sqrt(float(eval(self.expr)))
                if val.is_integer():
                    val = int(val)
                self.expr = str(val)
                self.display.config(text=self.expr)
            except Exception:
                self.display.config(text="Error")
                self.expr = ""
        else:
            self.expr += key
            self.display.config(text=self.expr)


# ─────────────────────────────────────────────
# TO-DO LIST
# ─────────────────────────────────────────────
class TodoList(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.tasks = []
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG2, pady=10, padx=12)
        top.pack(fill="x", side="top")

        self.entry = tk.Entry(top, bg=BG3, fg=FG, insertbackground=FG, font=("Segoe UI", 11),
                              relief="flat", bd=0)
        self.entry.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.add_task())

        priority_frame = tk.Frame(top, bg=BG2)
        priority_frame.pack(side="left")
        tk.Label(priority_frame, text="Priority:", bg=BG2, fg=FG2, font=("Segoe UI", 9)).pack(side="left")
        self.priority = ttk.Combobox(priority_frame, values=["High", "Medium", "Low"], width=8,
                                     state="readonly", font=("Segoe UI", 9))
        self.priority.set("Medium")
        self.priority.pack(side="left", padx=4)

        tk.Button(top, text="+ Add Task", command=self.add_task, bg=ACCENT, fg="#fff",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=6, cursor="hand2",
                  activebackground=ACCENT2, activeforeground="#fff").pack(side="left", padx=4)

        filter_bar = tk.Frame(self, bg=BG, pady=6, padx=12)
        filter_bar.pack(fill="x")
        for label, cmd_key in [("All", "all"), ("Active", "active"), ("Done", "done")]:
            tk.Button(filter_bar, text=label, command=lambda k=cmd_key: self.filter_tasks(k),
                      bg=BG3, fg=FG2, relief="flat", font=("Segoe UI", 9), padx=10, pady=4,
                      cursor="hand2", activebackground=BG2).pack(side="left", padx=2)

        self.filter = "all"

        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("done", "task", "priority")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("done", text="✓")
        self.tree.heading("task", text="Task")
        self.tree.heading("priority", text="Priority")
        self.tree.column("done", width=40, anchor="center")
        self.tree.column("task", width=350, anchor="w")
        self.tree.column("priority", width=90, anchor="center")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.toggle_done)

        bottom = tk.Frame(self, bg=BG2, pady=6, padx=12)
        bottom.pack(fill="x", side="bottom")
        tk.Button(bottom, text="Mark Done", command=self.toggle_done, bg=GREEN, fg="#1e1e2e",
                  relief="flat", font=("Segoe UI", 9, "bold"), padx=10, pady=4).pack(side="left", padx=4)
        tk.Button(bottom, text="Delete", command=self.delete_task, bg=RED, fg="#1e1e2e",
                  relief="flat", font=("Segoe UI", 9, "bold"), padx=10, pady=4).pack(side="left", padx=4)
        tk.Button(bottom, text="Clear Done", command=self.clear_done, bg=BG3, fg=FG2,
                  relief="flat", font=("Segoe UI", 9), padx=10, pady=4).pack(side="left", padx=4)
        self.count_label = tk.Label(bottom, text="0 tasks", bg=BG2, fg=FG2, font=("Segoe UI", 9))
        self.count_label.pack(side="right", padx=8)

    def add_task(self):
        text = self.entry.get().strip()
        if not text:
            return
        prio = self.priority.get()
        task = {"text": text, "done": False, "priority": prio}
        self.tasks.append(task)
        self.entry.delete(0, "end")
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, t in enumerate(self.tasks):
            if self.filter == "active" and t["done"]:
                continue
            if self.filter == "done" and not t["done"]:
                continue
            mark = "✓" if t["done"] else ""
            tag = "done" if t["done"] else t["priority"].lower()
            iid = self.tree.insert("", "end", iid=str(i),
                                   values=(mark, t["text"], t["priority"]), tags=(tag,))
        self.tree.tag_configure("done", foreground=FG2)
        self.tree.tag_configure("high", foreground=RED)
        self.tree.tag_configure("medium", foreground=YELLOW)
        self.tree.tag_configure("low", foreground=GREEN)
        active = sum(1 for t in self.tasks if not t["done"])
        self.count_label.config(text=f"{active} active / {len(self.tasks)} total")

    def filter_tasks(self, key):
        self.filter = key
        self.refresh()

    def toggle_done(self, event=None):
        sel = self.tree.selection()
        if sel:
            idx = int(sel[0])
            self.tasks[idx]["done"] = not self.tasks[idx]["done"]
            self.refresh()

    def delete_task(self):
        sel = self.tree.selection()
        if sel:
            idx = int(sel[0])
            self.tasks.pop(idx)
            self.refresh()

    def clear_done(self):
        self.tasks = [t for t in self.tasks if not t["done"]]
        self.refresh()


# ─────────────────────────────────────────────
# TIMER / STOPWATCH
# ─────────────────────────────────────────────
class TimerWatch(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        sw_frame = ttk.Frame(nb)
        nb.add(sw_frame, text="  Stopwatch  ")
        self._build_stopwatch(sw_frame)

        t_frame = ttk.Frame(nb)
        nb.add(t_frame, text="  Countdown Timer  ")
        self._build_timer(t_frame)

    def _build_stopwatch(self, parent):
        self.sw_running = False
        self.sw_start = 0
        self.sw_elapsed = 0
        self.laps = []

        center = tk.Frame(parent, bg=BG)
        center.pack(expand=True, fill="both", pady=20)

        self.sw_display = tk.Label(center, text="00:00:00.00", font=("Consolas", 42, "bold"),
                                   bg=BG, fg=ACCENT2)
        self.sw_display.pack(pady=20)

        btn_row = tk.Frame(center, bg=BG)
        btn_row.pack(pady=10)

        def mk(text, cmd, color=BG3):
            return tk.Button(btn_row, text=text, command=cmd, bg=color, fg="#fff" if color != BG3 else FG,
                             font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=10,
                             cursor="hand2", activebackground=ACCENT)

        self.sw_start_btn = mk("Start", self.sw_toggle, GREEN)
        self.sw_start_btn.pack(side="left", padx=6)
        mk("Lap", self.sw_lap).pack(side="left", padx=6)
        mk("Reset", self.sw_reset, RED).pack(side="left", padx=6)

        self.lap_box = tk.Listbox(center, bg=BG2, fg=FG2, font=("Consolas", 10), height=6,
                                  relief="flat", bd=0, selectbackground=ACCENT)
        self.lap_box.pack(fill="x", padx=40, pady=10)
        self._sw_tick()

    def sw_toggle(self):
        if self.sw_running:
            self.sw_elapsed += time.time() - self.sw_start
            self.sw_running = False
            self.sw_start_btn.config(text="Start", bg=GREEN)
        else:
            self.sw_start = time.time()
            self.sw_running = True
            self.sw_start_btn.config(text="Pause", bg=YELLOW)

    def sw_lap(self):
        t = self.sw_elapsed + (time.time() - self.sw_start if self.sw_running else 0)
        self.laps.append(t)
        h, rem = divmod(t, 3600)
        m, s = divmod(rem, 60)
        ms = int((s % 1) * 100)
        self.lap_box.insert("end", f"Lap {len(self.laps):02d}   {int(h):02d}:{int(m):02d}:{int(s):02d}.{ms:02d}")
        self.lap_box.yview("end")

    def sw_reset(self):
        self.sw_running = False
        self.sw_elapsed = 0
        self.sw_start_btn.config(text="Start", bg=GREEN)
        self.sw_display.config(text="00:00:00.00")
        self.laps.clear()
        self.lap_box.delete(0, "end")

    def _sw_tick(self):
        if self.sw_running:
            t = self.sw_elapsed + (time.time() - self.sw_start)
            h, rem = divmod(t, 3600)
            m, s = divmod(rem, 60)
            ms = int((s % 1) * 100)
            self.sw_display.config(text=f"{int(h):02d}:{int(m):02d}:{int(s):02d}.{ms:02d}")
        self.after(50, self._sw_tick)

    def _build_timer(self, parent):
        self.timer_running = False
        self.timer_remaining = 0
        self.timer_end = 0

        center = tk.Frame(parent, bg=BG)
        center.pack(expand=True, fill="both", pady=20)

        input_row = tk.Frame(center, bg=BG)
        input_row.pack(pady=10)

        def spin(lbl, max_val):
            tk.Label(input_row, text=lbl, bg=BG, fg=FG2, font=("Segoe UI", 10)).pack(side="left", padx=(12, 2))
            v = tk.StringVar(value="00")
            s = tk.Spinbox(input_row, from_=0, to=max_val, textvariable=v, width=4,
                           bg=BG2, fg=FG, insertbackground=FG, buttonbackground=BG3,
                           relief="flat", font=("Segoe UI", 14, "bold"), format="%02.0f")
            s.pack(side="left")
            return v

        self.timer_h = spin("h", 23)
        self.timer_m = spin("m", 59)
        self.timer_s = spin("s", 59)

        self.timer_display = tk.Label(center, text="00:00:00", font=("Consolas", 52, "bold"),
                                      bg=BG, fg=ACCENT2)
        self.timer_display.pack(pady=20)

        btn_row = tk.Frame(center, bg=BG)
        btn_row.pack()

        self.timer_btn = tk.Button(btn_row, text="Start", command=self.timer_toggle,
                                   bg=GREEN, fg="#1e1e2e", font=("Segoe UI", 11, "bold"),
                                   relief="flat", padx=20, pady=10, cursor="hand2")
        self.timer_btn.pack(side="left", padx=6)
        tk.Button(btn_row, text="Reset", command=self.timer_reset, bg=RED, fg="#1e1e2e",
                  font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=10,
                  cursor="hand2").pack(side="left", padx=6)
        self._timer_tick()

    def timer_toggle(self):
        if self.timer_running:
            self.timer_remaining = self.timer_end - time.time()
            self.timer_running = False
            self.timer_btn.config(text="Resume", bg=YELLOW)
        else:
            if self.timer_remaining <= 0:
                h = int(self.timer_h.get())
                m = int(self.timer_m.get())
                s = int(self.timer_s.get())
                self.timer_remaining = h * 3600 + m * 60 + s
            if self.timer_remaining <= 0:
                return
            self.timer_end = time.time() + self.timer_remaining
            self.timer_running = True
            self.timer_btn.config(text="Pause", bg=YELLOW)

    def timer_reset(self):
        self.timer_running = False
        self.timer_remaining = 0
        self.timer_display.config(text="00:00:00", fg=ACCENT2)
        self.timer_btn.config(text="Start", bg=GREEN)

    def _timer_tick(self):
        if self.timer_running:
            remaining = max(0, self.timer_end - time.time())
            h, rem = divmod(int(remaining), 3600)
            m, s = divmod(rem, 60)
            self.timer_display.config(text=f"{h:02d}:{m:02d}:{s:02d}")
            if remaining <= 0:
                self.timer_running = False
                self.timer_btn.config(text="Start", bg=GREEN)
                self.timer_display.config(fg=RED)
                messagebox.showinfo("Timer", "Time's up!")
        self.after(500, self._timer_tick)


# ─────────────────────────────────────────────
# UNIT CONVERTER
# ─────────────────────────────────────────────
CONVERSIONS = {
    "Length": {
        "units": ["Meters", "Kilometers", "Miles", "Feet", "Inches", "Centimeters", "Millimeters", "Yards"],
        "to_base": [1, 1000, 1609.344, 0.3048, 0.0254, 0.01, 0.001, 0.9144],
    },
    "Weight": {
        "units": ["Kilograms", "Grams", "Pounds", "Ounces", "Metric Tons", "Stone"],
        "to_base": [1, 0.001, 0.453592, 0.0283495, 1000, 6.35029],
    },
    "Temperature": {
        "units": ["Celsius", "Fahrenheit", "Kelvin"],
        "to_base": None,
    },
    "Speed": {
        "units": ["m/s", "km/h", "mph", "knots", "ft/s"],
        "to_base": [1, 0.277778, 0.44704, 0.514444, 0.3048],
    },
    "Area": {
        "units": ["Square Meters", "Square Km", "Square Miles", "Square Feet", "Acres", "Hectares"],
        "to_base": [1, 1e6, 2589988, 0.092903, 4046.86, 10000],
    },
    "Volume": {
        "units": ["Liters", "Milliliters", "Gallons (US)", "Pints (US)", "Cups", "Fluid Ounces"],
        "to_base": [1, 0.001, 3.78541, 0.473176, 0.236588, 0.0295735],
    },
    "Data": {
        "units": ["Bytes", "Kilobytes", "Megabytes", "Gigabytes", "Terabytes", "Bits"],
        "to_base": [1, 1024, 1048576, 1073741824, 1099511627776, 0.125],
    },
}


class UnitConverter(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG2, pady=10, padx=16)
        top.pack(fill="x")

        tk.Label(top, text="Category:", bg=BG2, fg=FG, font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        self.cat_var = tk.StringVar(value="Length")
        cat_combo = ttk.Combobox(top, textvariable=self.cat_var, values=list(CONVERSIONS.keys()),
                                  state="readonly", width=14, font=("Segoe UI", 10))
        cat_combo.pack(side="left")
        cat_combo.bind("<<ComboboxSelected>>", self._on_cat)

        main = tk.Frame(self, bg=BG)
        main.pack(expand=True, fill="both", padx=30, pady=20)

        row1 = tk.Frame(main, bg=BG)
        row1.pack(fill="x", pady=10)

        self.val1 = tk.StringVar()
        self.val2 = tk.StringVar()
        self.unit1 = tk.StringVar()
        self.unit2 = tk.StringVar()

        def make_col(parent, val_var, unit_var):
            col = tk.Frame(parent, bg=BG)
            col.pack(side="left", expand=True, fill="x", padx=10)
            e = tk.Entry(col, textvariable=val_var, bg=BG2, fg=FG, insertbackground=FG,
                         font=("Segoe UI", 22, "bold"), relief="flat", justify="right")
            e.pack(fill="x", ipady=10, pady=(0, 6))
            c = ttk.Combobox(col, textvariable=unit_var, state="readonly", font=("Segoe UI", 11))
            c.pack(fill="x", ipady=4)
            return e, c

        self.entry1, self.combo1 = make_col(row1, self.val1, self.unit1)
        tk.Label(row1, text="→", bg=BG, fg=ACCENT2, font=("Segoe UI", 24, "bold")).pack(side="left")
        self.entry2, self.combo2 = make_col(row1, self.val2, self.unit2)

        tk.Button(main, text="Convert", command=self.convert, bg=ACCENT, fg="#fff",
                  font=("Segoe UI", 13, "bold"), relief="flat", pady=12, cursor="hand2",
                  activebackground=ACCENT2).pack(fill="x", pady=10)

        self.result_label = tk.Label(main, text="", bg=BG, fg=GREEN, font=("Segoe UI", 12))
        self.result_label.pack()

        self._on_cat()
        self.entry1.bind("<Return>", lambda e: self.convert())

    def _on_cat(self, event=None):
        cat = self.cat_var.get()
        units = CONVERSIONS[cat]["units"]
        self.combo1.config(values=units)
        self.combo2.config(values=units)
        self.unit1.set(units[0])
        self.unit2.set(units[1] if len(units) > 1 else units[0])
        self.result_label.config(text="")

    def convert(self):
        cat = self.cat_var.get()
        try:
            val = float(self.val1.get())
        except ValueError:
            self.result_label.config(text="Invalid input", fg=RED)
            return

        u1 = self.unit1.get()
        u2 = self.unit2.get()
        data = CONVERSIONS[cat]

        if cat == "Temperature":
            units = data["units"]
            i1 = units.index(u1)
            i2 = units.index(u2)
            # Convert to Celsius first
            if i1 == 0:
                c = val
            elif i1 == 1:
                c = (val - 32) * 5 / 9
            else:
                c = val - 273.15
            # Celsius to target
            if i2 == 0:
                result = c
            elif i2 == 1:
                result = c * 9 / 5 + 32
            else:
                result = c + 273.15
        else:
            units = data["units"]
            factors = data["to_base"]
            f1 = factors[units.index(u1)]
            f2 = factors[units.index(u2)]
            result = val * f1 / f2

        if isinstance(result, float) and abs(result) < 1e10:
            result_str = f"{result:.6g}"
        else:
            result_str = f"{result:.4e}"

        self.val2.set(result_str)
        self.result_label.config(
            text=f"{val} {u1}  =  {result_str} {u2}", fg=GREEN
        )


# ─────────────────────────────────────────────
# COLOR PICKER
# ─────────────────────────────────────────────
class ColorPicker(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_color = "#7c6af7"
        self.palette = []
        self._build()

    def _build(self):
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        left = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        self.preview = tk.Label(left, bg=self.current_color, width=20, height=6, relief="flat")
        self.preview.pack(fill="x", pady=(0, 10))

        tk.Button(left, text="Pick Color", command=self.pick, bg=ACCENT, fg="#fff",
                  font=("Segoe UI", 11, "bold"), relief="flat", pady=10, cursor="hand2",
                  activebackground=ACCENT2).pack(fill="x", pady=4)
        tk.Button(left, text="Save to Palette", command=self.save_palette, bg=BG3, fg=FG,
                  font=("Segoe UI", 10), relief="flat", pady=8, cursor="hand2").pack(fill="x", pady=4)

        self.hex_var = tk.StringVar(value=self.current_color)
        hex_entry = tk.Entry(left, textvariable=self.hex_var, bg=BG2, fg=FG, insertbackground=FG,
                             font=("Consolas", 13), relief="flat", justify="center")
        hex_entry.pack(fill="x", ipady=6, pady=6)
        tk.Button(left, text="Apply Hex", command=self.apply_hex, bg=BG3, fg=FG,
                  relief="flat", font=("Segoe UI", 9)).pack(fill="x", pady=2)

        info = tk.Frame(left, bg=BG2, pady=12, padx=12)
        info.pack(fill="x", pady=10)
        self.info_label = tk.Label(info, text="", bg=BG2, fg=FG, font=("Consolas", 10), justify="left")
        self.info_label.pack(anchor="w")
        self._update_info()

        right = tk.Frame(main, bg=BG, padx=20)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="Saved Palette", bg=BG, fg=FG2, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))
        self.palette_frame = tk.Frame(right, bg=BG)
        self.palette_frame.pack(fill="both", expand=True)

        tk.Label(right, text="Harmony", bg=BG, fg=FG2, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 4))
        self.harmony_frame = tk.Frame(right, bg=BG)
        self.harmony_frame.pack(fill="x")

    def pick(self):
        color = colorchooser.askcolor(title="Choose a Color", color=self.current_color)
        if color[1]:
            self.current_color = color[1]
            self.hex_var.set(self.current_color)
            self.preview.config(bg=self.current_color)
            self._update_info()
            self._show_harmony()

    def apply_hex(self):
        h = self.hex_var.get().strip()
        if not h.startswith("#"):
            h = "#" + h
        try:
            self.preview.config(bg=h)
            self.current_color = h
            self._update_info()
            self._show_harmony()
        except Exception:
            self.info_label.config(text="Invalid hex color")

    def save_palette(self):
        self.palette.append(self.current_color)
        swatch = tk.Label(self.palette_frame, bg=self.current_color, width=4, height=2,
                          relief="flat", cursor="hand2")
        c = self.current_color
        swatch.bind("<Button-1>", lambda e, col=c: self._load_color(col))
        swatch.pack(side="left", padx=2, pady=2)

    def _load_color(self, col):
        self.current_color = col
        self.hex_var.set(col)
        self.preview.config(bg=col)
        self._update_info()
        self._show_harmony()

    def _update_info(self):
        h = self.current_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        r_n, g_n, b_n = r / 255, g / 255, b / 255
        cmax = max(r_n, g_n, b_n)
        cmin = min(r_n, g_n, b_n)
        delta = cmax - cmin
        if delta == 0:
            hue = 0
        elif cmax == r_n:
            hue = 60 * (((g_n - b_n) / delta) % 6)
        elif cmax == g_n:
            hue = 60 * ((b_n - r_n) / delta + 2)
        else:
            hue = 60 * ((r_n - g_n) / delta + 4)
        sat = 0 if cmax == 0 else delta / cmax
        val = cmax
        self.info_label.config(
            text=f"HEX:  {self.current_color.upper()}\n"
                 f"RGB:  ({r}, {g}, {b})\n"
                 f"HSV:  ({hue:.0f}°, {sat*100:.0f}%, {val*100:.0f}%)"
        )

    def _show_harmony(self):
        for w in self.harmony_frame.winfo_children():
            w.destroy()
        h = self.current_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        hue = self._rgb_to_hue(r, g, b)
        harmonies = [(hue + d) % 360 for d in [0, 30, 60, 120, 180, 210, 240, 300]]
        sat, val = 200, 200
        for ang in harmonies:
            c = self._hue_to_hex(ang, sat, val)
            tk.Label(self.harmony_frame, bg=c, width=3, height=2, relief="flat").pack(side="left", padx=2)

    def _rgb_to_hue(self, r, g, b):
        r, g, b = r / 255, g / 255, b / 255
        cmax = max(r, g, b)
        cmin = min(r, g, b)
        delta = cmax - cmin
        if delta == 0:
            return 0
        if cmax == r:
            return (60 * ((g - b) / delta)) % 360
        if cmax == g:
            return 60 * ((b - r) / delta + 2)
        return 60 * ((r - g) / delta + 4)

    def _hue_to_hex(self, h, s, v):
        s /= 255
        v /= 255
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        sector = int(h / 60) % 6
        rgb = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][sector]
        r, g, b = [int((ch + m) * 255) for ch in rgb]
        return f"#{r:02x}{g:02x}{b:02x}"


# ─────────────────────────────────────────────
# NOTES / JOURNAL
# ─────────────────────────────────────────────
class Notes(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.notes = {}
        self.current = None
        self._build()

    def _build(self):
        left = tk.Frame(self, bg=BG2, width=180)
        left.pack(side="left", fill="y", padx=(0, 0))
        left.pack_propagate(False)

        tk.Label(left, text="Notes", bg=BG2, fg=ACCENT2, font=("Segoe UI", 11, "bold"), pady=10).pack(fill="x", padx=8)

        tk.Button(left, text="+ New Note", command=self.new_note, bg=ACCENT, fg="#fff",
                  relief="flat", font=("Segoe UI", 9, "bold"), pady=6, cursor="hand2",
                  activebackground=ACCENT2).pack(fill="x", padx=8, pady=4)

        self.note_listbox = tk.Listbox(left, bg=BG2, fg=FG, font=("Segoe UI", 10), selectbackground=ACCENT,
                                        relief="flat", bd=0, activestyle="none", cursor="hand2")
        self.note_listbox.pack(fill="both", expand=True, padx=4, pady=4)
        self.note_listbox.bind("<<ListboxSelect>>", self.load_note)

        tk.Button(left, text="Delete", command=self.delete_note, bg=RED, fg="#1e1e2e",
                  relief="flat", font=("Segoe UI", 9, "bold"), pady=5).pack(fill="x", padx=8, pady=4)

        right = tk.Frame(self, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        title_bar = tk.Frame(right, bg=BG3, pady=6, padx=10)
        title_bar.pack(fill="x")
        tk.Label(title_bar, text="Title:", bg=BG3, fg=FG2, font=("Segoe UI", 9)).pack(side="left")
        self.title_var = tk.StringVar()
        self.title_entry = tk.Entry(title_bar, textvariable=self.title_var, bg=BG3, fg=FG,
                                    insertbackground=FG, relief="flat", font=("Segoe UI", 11, "bold"),
                                    width=30)
        self.title_entry.pack(side="left", padx=6, ipady=4)
        self.title_entry.bind("<KeyRelease>", self.save_current)
        tk.Button(title_bar, text="Save", command=self.save_current, bg=ACCENT, fg="#fff",
                  relief="flat", font=("Segoe UI", 9, "bold"), padx=10, pady=4).pack(side="right", padx=4)

        self.note_text = tk.Text(right, bg=BG2, fg=FG, insertbackground=ACCENT2, font=("Segoe UI", 11),
                                 wrap="word", padx=12, pady=12, relief="flat", bd=0,
                                 selectbackground=ACCENT, selectforeground="#fff")
        vsb = ttk.Scrollbar(right, orient="vertical", command=self.note_text.yview)
        self.note_text.config(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.note_text.pack(fill="both", expand=True, padx=6, pady=6)
        self.note_text.bind("<KeyRelease>", self.save_current)

        self.new_note()

    def new_note(self):
        import datetime
        key = datetime.datetime.now().strftime("Note %Y-%m-%d %H:%M:%S")
        self.notes[key] = {"title": key, "content": ""}
        self.note_listbox.insert("end", key)
        self.note_listbox.selection_clear(0, "end")
        self.note_listbox.selection_set("end")
        self.current = key
        self.title_var.set(key)
        self.note_text.delete("1.0", "end")

    def load_note(self, event=None):
        sel = self.note_listbox.curselection()
        if not sel:
            return
        key = self.note_listbox.get(sel[0])
        self.current = key
        note = self.notes.get(key, {})
        self.title_var.set(note.get("title", key))
        self.note_text.delete("1.0", "end")
        self.note_text.insert("1.0", note.get("content", ""))

    def save_current(self, event=None):
        if not self.current:
            return
        self.notes[self.current]["title"] = self.title_var.get()
        self.notes[self.current]["content"] = self.note_text.get("1.0", "end-1c")

    def delete_note(self):
        sel = self.note_listbox.curselection()
        if not sel:
            return
        key = self.note_listbox.get(sel[0])
        if messagebox.askyesno("Delete", f"Delete '{key}'?"):
            del self.notes[key]
            self.note_listbox.delete(sel[0])
            self.current = None
            self.title_var.set("")
            self.note_text.delete("1.0", "end")


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Desktop Suite")
        self.geometry("1100x700")
        self.minsize(800, 550)
        self.configure(bg=BG)
        apply_theme(self)

        header = tk.Frame(self, bg=BG, pady=10, padx=16)
        header.pack(fill="x")
        tk.Label(header, text="Desktop Suite", bg=BG, fg=ACCENT2,
                 font=("Segoe UI", 16, "bold")).pack(side="left")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tabs = [
            ("  Text Editor  ", TextEditor),
            ("  Calculator  ", Calculator),
            ("  To-Do  ", TodoList),
            ("  Timer  ", TimerWatch),
            ("  Converter  ", UnitConverter),
            ("  Color Picker  ", ColorPicker),
            ("  Notes  ", Notes),
        ]

        for label, cls in tabs:
            frame = cls(nb)
            nb.add(frame, text=label)


if __name__ == "__main__":
    app = App()
    app.mainloop()
