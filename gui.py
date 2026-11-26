"""
Desktop GUI for Automata Simulator: NFA to DFA Conversion
Built with standard Python Tkinter (Zero external dependencies).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
from typing import Set, Dict, Tuple, List, FrozenSet

from simulator import NFA, DFA, convert_nfa_to_dfa


class AutomataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Automata Simulator: NFA to DFA Converter")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.current_nfa = None
        self.current_dfa = None

        self._create_widgets()
        self.load_preset("endsWith01")

    def _create_widgets(self):
        # Top Header
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(top_frame, text="Automata Simulator: NFA → DFA (Subset Construction)", 
                              font=("Helvetica", 16, "bold"))
        title_lbl.pack(side=tk.LEFT)

        # Preset Buttons
        preset_frame = ttk.LabelFrame(self.root, text="Quick Demo Presets", padding=8)
        preset_frame.pack(fill=tk.X, padx=12, pady=4)

        ttk.Button(preset_frame, text="Preset 1: Ends with '01'", 
                   command=lambda: self.load_preset("endsWith01")).pack(side=tk.LEFT, padx=4)
        ttk.Button(preset_frame, text="Preset 2: Contains 'ab'", 
                   command=lambda: self.load_preset("containsAB")).pack(side=tk.LEFT, padx=4)
        ttk.Button(preset_frame, text="Preset 3: With Epsilon (ε)", 
                   command=lambda: self.load_preset("epsilonNFA")).pack(side=tk.LEFT, padx=4)

        # Main Paned Window (Left: Input & Tables, Right: Graph Visualizer)
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        left_frame = ttk.Frame(paned, padding=6)
        right_frame = ttk.Frame(paned, padding=6)
        paned.add(left_frame, weight=1)
        paned.add(right_frame, weight=1)

        # --- LEFT: INPUTS ---
        input_box = ttk.LabelFrame(left_frame, text="1. NFA Configuration", padding=8)
        input_box.pack(fill=tk.X, pady=4)

        grid_f = ttk.Frame(input_box)
        grid_f.pack(fill=tk.X)

        ttk.Label(grid_f, text="States:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ent_states = ttk.Entry(grid_f, width=22)
        self.ent_states.grid(row=0, column=1, sticky=tk.W, padx=4, pady=2)

        ttk.Label(grid_f, text="Alphabet:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.ent_alphabet = ttk.Entry(grid_f, width=15)
        self.ent_alphabet.grid(row=0, column=3, sticky=tk.W, padx=4, pady=2)

        ttk.Label(grid_f, text="Start State:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ent_start = ttk.Entry(grid_f, width=22)
        self.ent_start.grid(row=1, column=1, sticky=tk.W, padx=4, pady=2)

        ttk.Label(grid_f, text="Accept States:").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.ent_accept = ttk.Entry(grid_f, width=15)
        self.ent_accept.grid(row=1, column=3, sticky=tk.W, padx=4, pady=2)

        ttk.Label(input_box, text="Transitions (e.g. q0, 0 -> q0, q1 | q0, e -> q1 for ε):", 
                  font=("Helvetica", 9, "italic")).pack(anchor=tk.W, pady=(6, 2))
        self.txt_transitions = tk.Text(input_box, height=4, font=("Consolas", 10))
        self.txt_transitions.pack(fill=tk.X)

        btn_convert = tk.Button(input_box, text="⚡ Convert NFA to DFA", font=("Helvetica", 10, "bold"),
                                bg="#0284c7", fg="white", activebackground="#0369a1", 
                                cursor="hand2", command=self.convert)
        btn_convert.pack(fill=tk.X, pady=6)

        # Tables Notebook (Tabs)
        self.tabs = ttk.Notebook(left_frame)
        self.tabs.pack(fill=tk.BOTH, expand=True, pady=4)

        # Tab 1: NFA Table
        self.nfa_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.nfa_tab, text="NFA Table")
        self.nfa_tree = ttk.Treeview(self.nfa_tab, show="headings")
        self.nfa_tree.pack(fill=tk.BOTH, expand=True)

        # Tab 2: DFA Table
        self.dfa_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.dfa_tab, text="Generated DFA Table")
        self.dfa_tree = ttk.Treeview(self.dfa_tab, show="headings")
        self.dfa_tree.pack(fill=tk.BOTH, expand=True)

        # --- RIGHT: VISUAL DIAGRAM & STRING TESTER ---
        vis_box = ttk.LabelFrame(right_frame, text="2. Visual State Diagram", padding=8)
        vis_box.pack(fill=tk.BOTH, expand=True)

        # Toggle between NFA and DFA graph
        graph_ctrl = ttk.Frame(vis_box)
        graph_ctrl.pack(fill=tk.X, pady=2)
        self.graph_mode = tk.StringVar(value="DFA")
        ttk.Radiobutton(graph_ctrl, text="Show Generated DFA Graph", variable=self.graph_mode, 
                        value="DFA", command=self.draw_graph).pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(graph_ctrl, text="Show Original NFA Graph", variable=self.graph_mode, 
                        value="NFA", command=self.draw_graph).pack(side=tk.LEFT, padx=8)

        self.canvas = tk.Canvas(vis_box, bg="#1e293b", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=4)

        # --- BOTTOM: STRING TESTER ---
        test_box = ttk.LabelFrame(right_frame, text="3. String Simulation & Verification", padding=8)
        test_box.pack(fill=tk.X, pady=4)

        test_row = ttk.Frame(test_box)
        test_row.pack(fill=tk.X)

        ttk.Label(test_row, text="Input String:").pack(side=tk.LEFT, padx=4)
        self.ent_test_str = ttk.Entry(test_row, width=20, font=("Consolas", 11))
        self.ent_test_str.pack(side=tk.LEFT, padx=4)
        self.ent_test_str.bind("<Return>", lambda e: self.test_string())

        btn_test = tk.Button(test_row, text="Test String", bg="#10b981", fg="white", 
                             font=("Helvetica", 9, "bold"), cursor="hand2", command=self.test_string)
        btn_test.pack(side=tk.LEFT, padx=4)

        btn_batch = ttk.Button(test_row, text="Run Suite (Normal + Edge Cases)", command=self.run_batch_suite)
        btn_batch.pack(side=tk.LEFT, padx=6)

        self.lbl_verdict = tk.Label(test_box, text="Status: Ready", font=("Helvetica", 11, "bold"), 
                                    fg="#64748b", bg="#f1f5f9", padx=8, pady=4)
        self.lbl_verdict.pack(fill=tk.X, pady=4)

        self.lbl_trace = ttk.Label(test_box, text="Path Trace: -", font=("Consolas", 9))
        self.lbl_trace.pack(anchor=tk.W)

    def load_preset(self, key):
        if key == "endsWith01":
            self.ent_states.delete(0, tk.END)
            self.ent_states.insert(0, "q0, q1, q2")
            self.ent_alphabet.delete(0, tk.END)
            self.ent_alphabet.insert(0, "0, 1")
            self.ent_start.delete(0, tk.END)
            self.ent_start.insert(0, "q0")
            self.ent_accept.delete(0, tk.END)
            self.ent_accept.insert(0, "q2")
            self.txt_transitions.delete("1.0", tk.END)
            self.txt_transitions.insert(tk.END, "q0, 0 -> q0, q1\nq0, 1 -> q0\nq1, 1 -> q2")
            self.ent_test_str.delete(0, tk.END)
            self.ent_test_str.insert(0, "1001")
        elif key == "containsAB":
            self.ent_states.delete(0, tk.END)
            self.ent_states.insert(0, "q0, q1, q2")
            self.ent_alphabet.delete(0, tk.END)
            self.ent_alphabet.insert(0, "a, b")
            self.ent_start.delete(0, tk.END)
            self.ent_start.insert(0, "q0")
            self.ent_accept.delete(0, tk.END)
            self.ent_accept.insert(0, "q2")
            self.txt_transitions.delete("1.0", tk.END)
            self.txt_transitions.insert(tk.END, "q0, a -> q0, q1\nq0, b -> q0\nq1, b -> q2\nq2, a -> q2\nq2, b -> q2")
            self.ent_test_str.delete(0, tk.END)
            self.ent_test_str.insert(0, "aab")
        elif key == "epsilonNFA":
            self.ent_states.delete(0, tk.END)
            self.ent_states.insert(0, "A, B, C")
            self.ent_alphabet.delete(0, tk.END)
            self.ent_alphabet.insert(0, "a, b")
            self.ent_start.delete(0, tk.END)
            self.ent_start.insert(0, "A")
            self.ent_accept.delete(0, tk.END)
            self.ent_accept.insert(0, "C")
            self.txt_transitions.delete("1.0", tk.END)
            self.txt_transitions.insert(tk.END, "A, e -> B\nB, a -> B\nB, b -> C")
            self.ent_test_str.delete(0, tk.END)
            self.ent_test_str.insert(0, "b")

        self.convert()

    def convert(self):
        try:
            states = set(s.strip() for s in self.ent_states.get().split(",") if s.strip())
            alphabet = set(s.strip() for s in self.ent_alphabet.get().split(",") if s.strip())
            start = self.ent_start.get().strip()
            accept = set(s.strip() for s in self.ent_accept.get().split(",") if s.strip())

            transitions = {}
            for line in self.txt_transitions.get("1.0", tk.END).splitlines():
                line = line.strip()
                if not line or "->" not in line:
                    continue
                left, right = line.split("->")
                src, sym = [x.strip() for x in left.split(",")]
                dsts = set(x.strip() for x in right.split(",") if x.strip())
                transitions[(src, sym)] = dsts

            self.current_nfa = NFA(states, alphabet, transitions, start, accept)
            self.current_dfa = convert_nfa_to_dfa(self.current_nfa)

            self._populate_nfa_table()
            self._populate_dfa_table()
            self.draw_graph()

            self.lbl_verdict.config(text="✓ Conversion Successful: Ready to test strings", 
                                    bg="#dcfce7", fg="#166534")
        except Exception as e:
            messagebox.showerror("Input Error", f"Failed to parse NFA: {e}")

    def _populate_nfa_table(self):
        for col in self.nfa_tree.get_children():
            self.nfa_tree.delete(col)

        cols = ["State"] + self.current_nfa.alphabet + ["ε"]
        self.nfa_tree["columns"] = cols
        for c in cols:
            self.nfa_tree.heading(c, text=c)
            self.nfa_tree.column(c, width=70, anchor="center")

        for st in self.current_nfa.states:
            prefix = "-> " if st == self.current_nfa.start_state else ""
            if st in self.current_nfa.accept_states:
                prefix += "* "
            row = [f"{prefix}{st}"]
            for sym in self.current_nfa.alphabet:
                nxt = self.current_nfa.get_transitions(st, sym)
                row.append("{" + ", ".join(sorted(nxt)) + "}" if nxt else "Φ")
            
            # Epsilon
            eps_nxt = set()
            for eps in self.current_nfa.epsilon_symbols:
                eps_nxt.update(self.current_nfa.get_transitions(st, eps))
            row.append("{" + ", ".join(sorted(eps_nxt)) + "}" if eps_nxt else "Φ")

            self.nfa_tree.insert("", tk.END, values=row)

    def _populate_dfa_table(self):
        for col in self.dfa_tree.get_children():
            self.dfa_tree.delete(col)

        cols = ["DFA State", "Subset Mapping"] + self.current_dfa.alphabet
        self.dfa_tree["columns"] = cols
        self.dfa_tree.heading("DFA State", text="DFA State")
        self.dfa_tree.column("DFA State", width=80, anchor="center")
        self.dfa_tree.heading("Subset Mapping", text="NFA Subset")
        self.dfa_tree.column("Subset Mapping", width=110, anchor="center")

        for sym in self.current_dfa.alphabet:
            self.dfa_tree.heading(sym, text=f"'{sym}'")
            self.dfa_tree.column(sym, width=65, anchor="center")

        for st in self.current_dfa.states:
            prefix = "-> " if st == self.current_dfa.start_state else ""
            if st in self.current_dfa.accept_states:
                prefix += "* "
            
            sub = self.current_dfa.subset_mapping.get(st, frozenset())
            sub_str = "{" + ", ".join(sorted(sub)) + "}" if sub else "Φ"
            row = [f"{prefix}{st}", sub_str]

            for sym in self.current_dfa.alphabet:
                dst = self.current_dfa.transitions.get((st, sym), "DEAD")
                row.append(dst)

            self.dfa_tree.insert("", tk.END, values=row)

    def draw_graph(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 480
        h = self.canvas.winfo_height() or 340

        is_dfa = (self.graph_mode.get() == "DFA")
        auto = self.current_dfa if is_dfa else self.current_nfa
        if not auto or not auto.states:
            return

        states = auto.states
        n = len(states)
        cx, cy = w / 2, h / 2
        r = min(w, h) * 0.32
        radius = 24

        positions = {}
        for idx, st in enumerate(states):
            if n <= 3:
                # Horizontal line for 2-3 states
                spacing = w / (n + 1)
                positions[st] = (spacing * (idx + 1), cy)
            else:
                ang = 2 * math.pi * idx / n
                positions[st] = (cx + r * math.cos(ang), cy + r * math.sin(ang))

        # Helper to draw edge
        def draw_edge(src, dst, label):
            x1, y1 = positions[src]
            x2, y2 = positions[dst]

            if src == dst:
                # Self-loop
                self.canvas.create_oval(x1 - 12, y1 - radius - 24, x1 + 12, y1 - radius, 
                                        outline="#94a3b8", width=2)
                self.canvas.create_text(x1, y1 - radius - 30, text=label, fill="#38bdf8", 
                                        font=("Helvetica", 10, "bold"))
                return

            dx = x2 - x1
            dy = y2 - y1
            dist = math.hypot(dx, dy)
            if dist == 0:
                return
            nx = dx / dist
            ny = dy / dist

            sx = x1 + nx * radius
            sy = y1 + ny * radius
            ex = x2 - nx * radius
            ey = y2 - ny * radius

            self.canvas.create_line(sx, sy, ex, ey, arrow=tk.LAST, fill="#94a3b8", 
                                    width=2, arrowshape=(10, 12, 5))
            mx = (sx + ex) / 2 - ny * 10
            my = (sy + ey) / 2 + nx * 10
            self.canvas.create_text(mx, my, text=label, fill="#38bdf8", font=("Helvetica", 10, "bold"))

        # Collect edges
        edges = {}
        if is_dfa:
            for st in states:
                for sym in auto.alphabet:
                    dst = auto.transitions.get((st, sym))
                    if dst and dst in positions:
                        key = (st, dst)
                        edges[key] = f"{edges[key]},{sym}" if key in edges else sym
        else:
            for st in states:
                for sym in auto.alphabet:
                    for dst in auto.get_transitions(st, sym):
                        if dst in positions:
                            key = (st, dst)
                            edges[key] = f"{edges[key]},{sym}" if key in edges else sym
                for eps in auto.epsilon_symbols:
                    for dst in auto.get_transitions(st, eps):
                        if dst in positions:
                            key = (st, dst)
                            edges[key] = f"{edges[key]},ε" if key in edges else "ε"

        for (src, dst), lbl in edges.items():
            draw_edge(src, dst, lbl)

        # Draw Nodes
        start_st = auto.start_state
        accept_sts = auto.accept_states

        for st in states:
            x, y = positions[st]
            # Outer circle
            outline_col = "#34d399" if st in accept_sts else "#38bdf8"
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, 
                                    fill="#0f172a", outline=outline_col, width=2.5)

            # Double ring for accept state
            if st in accept_sts:
                self.canvas.create_oval(x - radius + 4, y - radius + 4, x + radius - 4, y + radius - 4, 
                                        outline="#34d399", width=1.5)

            # Start State Arrow
            if st == start_st:
                self.canvas.create_line(x - radius - 26, y, x - radius, y, arrow=tk.LAST, 
                                        fill="#fbbf24", width=3, arrowshape=(8, 10, 4))

            # State label
            self.canvas.create_text(x, y, text=st, fill="white", font=("Helvetica", 10, "bold"))

    def test_string(self):
        if not self.current_dfa:
            return
        s = self.ent_test_str.get().strip()
        accepted, trace = self.current_dfa.simulate(s)

        if accepted:
            self.lbl_verdict.config(text=f"✓ ACCEPTED  (String: '{s}')", bg="#dcfce7", fg="#15803d")
        else:
            self.lbl_verdict.config(text=f"✗ REJECTED  (String: '{s}')", bg="#fee2e2", fg="#b91c1c")

        if not trace:
            trace_str = f"Start at {self.current_dfa.start_state}"
        else:
            trace_str = f"{self.current_dfa.start_state} " + " ".join([f"--({sym})--> {nxt}" for _, sym, nxt in trace])
        self.lbl_trace.config(text=f"Path Trace: {trace_str}")

    def run_batch_suite(self):
        if not self.current_dfa:
            return
        tests = [
            ("01", True), ("1001", True), ("010", False), ("111", False), ("", False)
        ]
        results = []
        for s, exp in tests:
            acc, _ = self.current_dfa.simulate(s)
            status = "PASS" if acc == exp else "FAIL"
            results.append(f"[{status}] '{s}': {'ACCEPTED' if acc else 'REJECTED'}")

        messagebox.showinfo("Automated Test Suite", "\n".join(results))


def main():
    root = tk.Tk()
    app = AutomataGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
