"""Triqui (tres en raya) con interfaz estilo PlayStation, hecho con tkinter."""

import tkinter as tk
from functools import lru_cache

# --- Paleta -----------------------------------------------------------------
BG = "#070b1f"
PANEL = "#111a3f"
PANEL_LIGHT = "#1b2757"
PS_BLUE = "#0070d1"
PS_BLUE_LIGHT = "#2d9bff"
TEXT = "#e8eeff"
MUTED = "#8b97c7"
COLOR_X = "#4aa8ff"   # cruz azul
COLOR_O = "#ff4d6d"   # círculo rojo
COLOR_TRI = "#2ee6a6"  # triángulo verde
COLOR_SQ = "#ff8fd8"   # cuadrado rosa
GOLD = "#ffd24a"

FONT = "Segoe UI"
MACHINE_NAME = "Máquina"

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
         (0, 3, 6), (1, 4, 7), (2, 5, 8),
         (0, 4, 8), (2, 4, 6)]


# --- Lógica del juego -------------------------------------------------------
def check_winner(board):
    """Devuelve (símbolo, línea) si hay ganador, si no None."""
    for a, b, c in LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
    return None


@lru_cache(maxsize=None)
def _minimax(board, turn, me):
    result = check_winner(board)
    if result:
        return 1 if result[0] == me else -1
    if "" not in board:
        return 0
    other = "O" if turn == "X" else "X"
    scores = []
    for i, cell in enumerate(board):
        if not cell:
            nxt = board[:i] + (turn,) + board[i + 1:]
            scores.append(_minimax(nxt, other, me))
    return max(scores) if turn == me else min(scores)


def best_move(board, me):
    """Mejor jugada para `me` (minimax; la máquina no pierde)."""
    board = tuple(board)
    other = "O" if me == "X" else "X"
    best, best_score = None, -2
    for i, cell in enumerate(board):
        if not cell:
            score = _minimax(board[:i] + (me,) + board[i + 1:], other, me)
            if score > best_score:
                best, best_score = i, score
    return best


# --- Widgets ----------------------------------------------------------------
def round_rect(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
           x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
           x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class PSButton(tk.Canvas):
    def __init__(self, parent, text, command, width=320, height=56,
                 color=PS_BLUE, hover=PS_BLUE_LIGHT, font_size=14):
        super().__init__(parent, width=width, height=height, bg=parent["bg"],
                         highlightthickness=0, cursor="hand2")
        self.command, self.color, self.hover = command, color, hover
        self.shape = round_rect(self, 2, 2, width - 2, height - 2, 18,
                                fill=color, outline=PS_BLUE_LIGHT, width=2)
        self.label = self.create_text(width // 2, height // 2, text=text, fill="white",
                                      font=(FONT, font_size, "bold"))
        self.bind("<Enter>", lambda e: self.itemconfig(self.shape, fill=self.hover))
        self.bind("<Leave>", lambda e: self.itemconfig(self.shape, fill=self.color))
        self.bind("<Button-1>", lambda e: self.command())


def draw_symbol(canvas, symbol, cx, cy, size, width=10, tag=None, glow=False):
    """Dibuja ✕ (azul) u ○ (rojo) al estilo PlayStation."""
    color = COLOR_X if symbol == "X" else COLOR_O
    layers = [(width + 10, "#1c2a5c"), (width, color)] if glow else [(width, color)]
    for w, col in layers:
        if symbol == "X":
            canvas.create_line(cx - size, cy - size, cx + size, cy + size, fill=col,
                               width=w, capstyle="round", tags=tag)
            canvas.create_line(cx - size, cy + size, cx + size, cy - size, fill=col,
                               width=w, capstyle="round", tags=tag)
        else:
            canvas.create_oval(cx - size, cy - size, cx + size, cy + size, outline=col,
                               width=w, tags=tag)


# --- Aplicación -------------------------------------------------------------
class TriquiApp(tk.Tk):
    CELL = 150
    PAD = 20

    def __init__(self):
        super().__init__()
        self.title("TRIQUI  -  PlayStation Edition")
        self.configure(bg=BG)
        self.geometry("640x780")
        self.resizable(False, False)
        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.show_mode_screen()

    # ---- utilidades de pantalla
    def clear(self):
        self._cancel_pending()
        for w in self.container.winfo_children():
            w.destroy()

    def _cancel_pending(self):
        if getattr(self, "_after_id", None):
            self.after_cancel(self._after_id)
            self._after_id = None

    def header(self, subtitle):
        top = tk.Frame(self.container, bg=BG)
        top.pack(pady=(40, 10))
        shapes = tk.Frame(top, bg=BG)
        shapes.pack()
        for ch, col in (("△", COLOR_TRI), ("○", COLOR_O), ("✕", COLOR_X), ("□", COLOR_SQ)):
            tk.Label(shapes, text=ch, fg=col, bg=BG, font=(FONT, 34, "bold")).pack(side="left", padx=8)
        tk.Label(top, text="TRIQUI", fg=TEXT, bg=BG, font=(FONT, 44, "bold")).pack(pady=(4, 0))
        tk.Label(top, text=subtitle, fg=MUTED, bg=BG, font=(FONT, 14)).pack(pady=(4, 0))

    # ---- 1. modo de juego
    def show_mode_screen(self):
        self.clear()
        self.header("Selecciona el modo de juego")
        box = tk.Frame(self.container, bg=BG)
        box.pack(pady=40)
        PSButton(box, "2 JUGADORES", lambda: self.show_names_screen(False)).pack(pady=10)
        PSButton(box, "CONTRA LA MÁQUINA", lambda: self.show_names_screen(True)).pack(pady=10)

    # ---- 2. nombres
    def show_names_screen(self, vs_machine):
        self.vs_machine = vs_machine
        self.clear()
        self.header("Escribe el nombre de los jugadores")
        box = tk.Frame(self.container, bg=PANEL, padx=30, pady=24)
        box.pack(pady=30)

        def field(label, default, disabled=False):
            tk.Label(box, text=label, fg=MUTED, bg=PANEL, font=(FONT, 11)).pack(anchor="w")
            var = tk.StringVar(value=default)
            ent = tk.Entry(box, textvariable=var, width=26, font=(FONT, 15), bg=PANEL_LIGHT,
                           fg=TEXT, insertbackground=TEXT, relief="flat",
                           disabledbackground=PANEL_LIGHT, disabledforeground=MUTED)
            if disabled:
                ent.configure(state="disabled")
            ent.pack(ipady=6, pady=(2, 14))
            return var

        self.name1_var = field("Jugador 1", "Jugador 1")
        if vs_machine:
            self.name2_var = field("Jugador 2", MACHINE_NAME, disabled=True)
        else:
            self.name2_var = field("Jugador 2", "Jugador 2")

        PSButton(self.container, "CONTINUAR", self._names_done).pack(pady=(10, 6))
        PSButton(self.container, "VOLVER", self.show_mode_screen, width=200, height=44,
                 color=PANEL_LIGHT, hover=PANEL, font_size=11).pack()

    def _names_done(self):
        n1 = self.name1_var.get().strip() or "Jugador 1"
        n2 = MACHINE_NAME if self.vs_machine else (self.name2_var.get().strip() or "Jugador 2")
        if n1.lower() == n2.lower():
            n2 += " (2)"
        self.names = [n1, n2]
        self.show_symbol_screen()

    # ---- 3. elegir símbolo
    def show_symbol_screen(self):
        self.clear()
        self.header(f"{self.names[0]}, elige tu símbolo")
        row = tk.Frame(self.container, bg=BG)
        row.pack(pady=40)
        for sym in ("X", "O"):
            cv = tk.Canvas(row, width=170, height=170, bg=PANEL, highlightthickness=2,
                           highlightbackground=PS_BLUE, cursor="hand2")
            cv.pack(side="left", padx=18)
            draw_symbol(cv, sym, 85, 85, 42, width=12)
            cv.bind("<Button-1>", lambda e, s=sym: self._start_match(s))
            cv.bind("<Enter>", lambda e, c=cv: c.configure(bg=PANEL_LIGHT))
            cv.bind("<Leave>", lambda e, c=cv: c.configure(bg=PANEL))
        PSButton(self.container, "VOLVER", self.show_mode_screen, width=200, height=44,
                 color=PANEL_LIGHT, hover=PANEL, font_size=11).pack()

    def _start_match(self, symbol1):
        self.symbols = [symbol1, "O" if symbol1 == "X" else "X"]
        self.scores = [0, 0]
        self.starter = 0
        self.show_game_screen()

    # ---- 4. juego
    def show_game_screen(self):
        self.clear()
        self.board = [""] * 9
        self.turn = self.starter           # índice del jugador en turno
        self.game_over = False
        self.hover_cell = None

        # marcador
        score = tk.Frame(self.container, bg=BG)
        score.pack(pady=(26, 8))
        self.score_labels = []
        for i in range(2):
            card = tk.Frame(score, bg=PANEL, padx=18, pady=8,
                            highlightthickness=2, highlightbackground=PANEL)
            card.pack(side="left", padx=10)
            col = COLOR_X if self.symbols[i] == "X" else COLOR_O
            glyph = "✕" if self.symbols[i] == "X" else "○"
            tk.Label(card, text=f"{glyph}  {self.names[i]}", fg=col, bg=PANEL,
                     font=(FONT, 13, "bold")).pack()
            lbl = tk.Label(card, text=str(self.scores[i]), fg=TEXT, bg=PANEL, font=(FONT, 30, "bold"))
            lbl.pack()
            tk.Label(card, text="victorias", fg=MUTED, bg=PANEL, font=(FONT, 9)).pack()
            self.score_labels.append((card, lbl))

        self.status = tk.Label(self.container, text="", fg=TEXT, bg=BG, font=(FONT, 18, "bold"))
        self.status.pack(pady=(10, 6))

        size = self.CELL * 3 + self.PAD * 2
        self.canvas = tk.Canvas(self.container, width=size, height=size, bg=PANEL,
                                highlightthickness=2, highlightbackground=PS_BLUE, cursor="hand2")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda e: self._set_hover(None))

        self.end_box = tk.Frame(self.container, bg=BG)
        self.end_box.pack(pady=14)

        self._redraw()
        self._update_status()
        self._maybe_machine_move()

    def _cell_center(self, i):
        r, c = divmod(i, 3)
        return (self.PAD + c * self.CELL + self.CELL // 2,
                self.PAD + r * self.CELL + self.CELL // 2)

    def _redraw(self, win_line=None):
        cv = self.canvas
        cv.delete("all")
        # cuadrícula
        for k in (1, 2):
            p = self.PAD + k * self.CELL
            cv.create_line(p, self.PAD + 10, p, self.PAD + 3 * self.CELL - 10,
                           fill=PS_BLUE_LIGHT, width=4, capstyle="round")
            cv.create_line(self.PAD + 10, p, self.PAD + 3 * self.CELL - 10, p,
                           fill=PS_BLUE_LIGHT, width=4, capstyle="round")
        # resaltado de celda bajo el cursor
        if self.hover_cell is not None and not self.game_over and not self.board[self.hover_cell]:
            cx, cy = self._cell_center(self.hover_cell)
            h = self.CELL // 2 - 8
            round_rect(cv, cx - h, cy - h, cx + h, cy + h, 14, fill=PANEL_LIGHT, outline="")
        # símbolos
        for i, sym in enumerate(self.board):
            if sym:
                cx, cy = self._cell_center(i)
                draw_symbol(cv, sym, cx, cy, 38, width=12, glow=bool(win_line and i in win_line))
        # línea ganadora
        if win_line:
            x1, y1 = self._cell_center(win_line[0])
            x2, y2 = self._cell_center(win_line[2])
            cv.create_line(x1, y1, x2, y2, fill=GOLD, width=8, capstyle="round")

    def _update_status(self):
        if self.game_over:
            return
        i = self.turn
        col = COLOR_X if self.symbols[i] == "X" else COLOR_O
        self.status.configure(text=f"Turno de {self.names[i]}", fg=col)
        for k, (card, _) in enumerate(self.score_labels):
            card.configure(highlightbackground=col if k == i else PANEL)

    def _cell_at(self, x, y):
        c, r = (x - self.PAD) // self.CELL, (y - self.PAD) // self.CELL
        return int(r * 3 + c) if 0 <= c < 3 and 0 <= r < 3 else None

    def _is_human_turn(self):
        return not (self.vs_machine and self.turn == 1)

    def _on_motion(self, e):
        self._set_hover(self._cell_at(e.x, e.y) if self._is_human_turn() else None)

    def _set_hover(self, cell):
        if cell != self.hover_cell:
            self.hover_cell = cell
            if not self.game_over:
                self._redraw()

    def _on_click(self, e):
        if self.game_over or not self._is_human_turn():
            return
        cell = self._cell_at(e.x, e.y)
        if cell is not None and not self.board[cell]:
            self._play(cell)

    def _play(self, cell):
        self.board[cell] = self.symbols[self.turn]
        result = check_winner(self.board)
        if result:
            self._finish(winner=self.turn, line=result[1])
        elif "" not in self.board:
            self._finish(winner=None)
        else:
            self.turn = 1 - self.turn
            self._redraw()
            self._update_status()
            self._maybe_machine_move()

    def _maybe_machine_move(self):
        if self.vs_machine and self.turn == 1 and not self.game_over:
            self._after_id = self.after(650, self._machine_move)

    def _machine_move(self):
        self._after_id = None
        if not self.game_over:
            self._play(best_move(self.board, self.symbols[1]))

    # ---- fin de la ronda
    def _finish(self, winner, line=None):
        self.game_over = True
        self.hover_cell = None
        self._redraw(win_line=line)
        for card, _ in self.score_labels:
            card.configure(highlightbackground=PANEL)
        if winner is None:
            self.status.configure(text="¡EMPATE!", fg=GOLD)
        else:
            self.scores[winner] += 1
            self.score_labels[winner][1].configure(text=str(self.scores[winner]))
            self.score_labels[winner][0].configure(highlightbackground=GOLD)
            self.status.configure(text=f"¡GANÓ {self.names[winner].upper()}!", fg=GOLD)

        self.starter = 1 - self.starter  # la siguiente ronda empieza el otro jugador
        label = "DESEMPATE" if winner is None else "JUGAR DE NUEVO"
        PSButton(self.end_box, label, self.show_game_screen, width=250).pack(side="left", padx=8)
        PSButton(self.end_box, "NUEVO JUEGO", self.show_mode_screen, width=200,
                 color=PANEL_LIGHT, hover=PANEL).pack(side="left", padx=8)


if __name__ == "__main__":
    TriquiApp().mainloop()
