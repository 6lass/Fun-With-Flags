import tkinter as tk
from tkinter import messagebox
import os, json, random, urllib.request
from datetime import datetime
from PIL import Image, ImageTk
from flag_data import FLAGS_DB

BG, CARD_BG, BORDER, TEXT, MUTED = "#121214", "#1e1e24", "#2e2e38", "#f3f4f6", "#9ca3af"
BLUE, GREEN, RED, YELLOW = "#0284c7", "#15803d", "#b91c1c", "#d97706"

TRANSLATIONS = {
    "es": {
        "title": "Adivina la Bandera",
        "select_lang": "Selecciona tu Idioma / Select your Language",
        "question": "Pregunta",
        "pts": "pts",
        "next_flag": "Siguiente Bandera ➡️",
        "results": "Resultados 🏁",
        "loading": "Cargando...",
        "game_over": "Partida Terminada",
        "correct": "Aciertos",
        "accuracy": "Precisión",
        "streak": "Racha",
        "player": "Jugador",
        "register": "Registrar",
        "record_title": "Récord",
        "record_saved": "¡Guardado!",
        "high_scores": "Mejores Puntuaciones",
        "no_records": "Sin récords aún. ¡Sé el primero!",
        "col_pos": "Pos",
        "col_name": "Nombre",
        "col_points": "Puntos",
        "col_accuracy": "Precisión",
        "play_again": "🔄 Jugar de Nuevo",
        "exit": "❌ Salir"
    },
    "en": {
        "title": "Guess the Flag",
        "select_lang": "Selecciona tu Idioma / Select your Language",
        "question": "Question",
        "pts": "pts",
        "next_flag": "Next Flag ➡️",
        "results": "Results 🏁",
        "loading": "Loading...",
        "game_over": "Game Over",
        "correct": "Correct",
        "accuracy": "Accuracy",
        "streak": "Streak",
        "player": "Player",
        "register": "Register",
        "record_title": "Record",
        "record_saved": "Saved!",
        "high_scores": "High Scores",
        "no_records": "No records yet. Be the first!",
        "col_pos": "Pos",
        "col_name": "Name",
        "col_points": "Points",
        "col_accuracy": "Accuracy",
        "play_again": "🔄 Play Again",
        "exit": "❌ Exit"
    }
}

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache_banderas")
os.makedirs(CACHE_DIR, exist_ok=True)

def get_flag_path(code):
    path = os.path.join(CACHE_DIR, f"{code}.png")
    if not os.path.exists(path):
        url = f"https://flagcdn.com/w320/{code}.png"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp, open(path, 'wb') as f:
                f.write(resp.read())
        except Exception as e:
            print(e)
            return None
    return path

class Btn(tk.Button):
    def __init__(self, master, hover_bg="#3f3f46", bg="#27272a", fg=TEXT, **kwargs):
        super().__init__(master, bg=bg, fg=fg, bd=1, relief="flat", activebackground=hover_bg, activeforeground=fg, cursor="hand2", **kwargs)
        self.bind("<Enter>", lambda e: self.configure(bg=hover_bg) if self["state"] != "disabled" else None)
        self.bind("<Leave>", lambda e: self.configure(bg=bg) if self["state"] != "disabled" else None)

class GuessTheFlagApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Adivina la Bandera / Guess the Flag")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.w, self.h = 500, 660
        self.geometry(f"{self.w}x{self.h}+{(self.winfo_screenwidth()-self.w)//2}+{(self.winfo_screenheight()-self.h)//2}")
        self.score, self.lives, self.streak, self.max_streak = 0, 3, 0, 0
        self.correct_count, self.incorrect_count, self.total_questions = 0, 0, 0
        self.asked, self.available = [], []
        self.time_left, self.timer_id = 30, None
        self.is_answered = False
        self.lang = "es"
        self.show_language_menu()
        
    def show_screen(self, draw_func):
        if self.timer_id: 
            self.after_cancel(self.timer_id)
            self.timer_id = None
        for w in self.winfo_children(): 
            w.destroy()
        draw_func()

    def show_language_menu(self):
        def draw():
            tk.Label(self, text="Adivina la Bandera\nGuess the Flag", fg=BLUE, bg=BG, font=("Segoe UI", 20, "bold"), justify="center").pack(pady=(40, 20))
            tk.Label(self, text="Selecciona tu Idioma / Select your Language", fg=MUTED, bg=BG, font=("Segoe UI", 11, "italic")).pack(pady=(0, 30))
            
            cards_frame = tk.Frame(self, bg=BG)
            cards_frame.pack(pady=10)
            
            def choose_lang(lang_code):
                self.lang = lang_code
                self.title(TRANSLATIONS[self.lang]["title"])
                self.start_game()
            
            # Spain Card (es)
            card_es = tk.Frame(cards_frame, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1, width=180, height=260)
            card_es.pack(side="left", padx=15)
            card_es.pack_propagate(False)
            
            lbl_flag_es = tk.Label(card_es, bg=CARD_BG)
            lbl_flag_es.pack(pady=(20, 10))
            path_es = get_flag_path("es")
            if path_es and os.path.exists(path_es):
                try:
                    img = Image.open(path_es)
                    w, h = img.size
                    ratio = min(140 / w, 84 / h)
                    img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
                    self.flag_es_photo = ImageTk.PhotoImage(img)
                    lbl_flag_es.configure(image=self.flag_es_photo)
                except Exception:
                    lbl_flag_es.configure(text="🇪🇸", font=("Segoe UI", 24))
            else:
                lbl_flag_es.configure(text="🇪🇸", font=("Segoe UI", 24))
                
            tk.Label(card_es, text="Español", fg=TEXT, bg=CARD_BG, font=("Segoe UI", 14, "bold")).pack(pady=10)
            
            btn_es = Btn(card_es, text="Jugar", bg=GREEN, hover_bg="#16a34a", font=("Segoe UI", 11, "bold"), command=lambda: choose_lang("es"))
            btn_es.pack(fill="x", padx=15, pady=(15, 0), ipady=4)
            
            # USA Card (us)
            card_en = tk.Frame(cards_frame, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1, width=180, height=260)
            card_en.pack(side="left", padx=15)
            card_en.pack_propagate(False)
            
            lbl_flag_us = tk.Label(card_en, bg=CARD_BG)
            lbl_flag_us.pack(pady=(20, 10))
            path_us = get_flag_path("us")
            if path_us and os.path.exists(path_us):
                try:
                    img = Image.open(path_us)
                    w, h = img.size
                    ratio = min(140 / w, 84 / h)
                    img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
                    self.flag_us_photo = ImageTk.PhotoImage(img)
                    lbl_flag_us.configure(image=self.flag_us_photo)
                except Exception:
                    lbl_flag_us.configure(text="🇺🇸", font=("Segoe UI", 24))
            else:
                lbl_flag_us.configure(text="🇺🇸", font=("Segoe UI", 24))
                
            tk.Label(card_en, text="English", fg=TEXT, bg=CARD_BG, font=("Segoe UI", 14, "bold")).pack(pady=10)
            
            btn_en = Btn(card_en, text="Play", bg=BLUE, hover_bg="#0369a1", font=("Segoe UI", 11, "bold"), command=lambda: choose_lang("en"))
            btn_en.pack(fill="x", padx=15, pady=(15, 0), ipady=4)
            
            tk.Label(self, text="Fun With Flags © 2026", fg=MUTED, bg=BG, font=("Segoe UI", 8)).pack(side="bottom", pady=20)
            
        self.show_screen(draw)

    def start_game(self):
        self.score, self.lives, self.streak, self.max_streak = 0, 3, 0, 0
        self.correct_count, self.incorrect_count, self.total_questions = 0, 0, 0
        self.asked = []
        self.available = list(FLAGS_DB.keys())
        random.shuffle(self.available)
        
        def draw():
            t = TRANSLATIONS[self.lang]
            self.hud = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
            self.hud.pack(fill="x", ipady=6, pady=(5, 10))
            
            l_stats = tk.Frame(self.hud, bg=CARD_BG)
            l_stats.pack(side="left", padx=15)
            self.lbl_q_val = tk.Label(l_stats, text=f"{t['question']} 1", fg=TEXT, bg=CARD_BG, font=("Segoe UI", 12, "bold"))
            self.lbl_q_val.pack(anchor="w")
            self.lbl_score_val = tk.Label(l_stats, text=f"0 {t['pts']}", fg=BLUE, bg=CARD_BG, font=("Segoe UI", 11, "bold"))
            self.lbl_score_val.pack(anchor="w")
            
            r_stats = tk.Frame(self.hud, bg=CARD_BG)
            r_stats.pack(side="right", padx=15)
            self.lbl_lives = tk.Label(r_stats, text="❤️ ❤️ ❤️", fg=TEXT, bg=CARD_BG, font=("Segoe UI", 10, "bold"))
            self.lbl_lives.pack(anchor="e")
            self.lbl_streak = tk.Label(r_stats, text="", fg="#f43f5e", bg=CARD_BG, font=("Segoe UI", 11, "bold"))
            self.lbl_streak.pack(anchor="e")
            
            self.lbl_timer = tk.Label(self.hud, text="30s", fg=TEXT, bg=CARD_BG, font=("Segoe UI", 18, "bold"))
            self.lbl_timer.pack(pady=5)
            
            self.flag_f = tk.Frame(self, bg=BG, highlightbackground=BORDER, highlightthickness=1)
            self.flag_f.pack(fill="x", pady=10)
            self.lbl_flag = tk.Label(self.flag_f, bg=BG)
            self.lbl_flag.pack(pady=10)
            
            self.opts_f = tk.Frame(self, bg=BG)
            self.opts_f.pack(fill="x", pady=5)
            self.opt_btns = []
            for i in range(4):
                btn = Btn(self.opts_f, text="", font=("Segoe UI", 11, "bold"), anchor="w", padx=15, command=lambda idx=i: self.evaluate_choice(idx))
                btn.pack(fill="x", pady=4, ipady=6)
                self.opt_btns.append(btn)
                
            self.btn_next = Btn(self, text=t["next_flag"], bg=BLUE, hover_bg="#0369a1", font=("Segoe UI", 12, "bold"), command=self.spawn_question)
            
        self.show_screen(draw)
        self.spawn_question()

    def spawn_question(self):
        t = TRANSLATIONS[self.lang]
        self.is_answered = False
        self.btn_next.pack_forget()
        for b in self.opt_btns: b.configure(state="normal", bg="#27272a")
        if not self.available:
            self.available = [c for c in FLAGS_DB.keys() if c not in self.asked]
            if not self.available: self.asked, self.available = [], list(FLAGS_DB.keys())
            random.shuffle(self.available)
            
        self.current_country = self.available.pop()
        self.asked.append(self.current_country)
        self.total_questions += 1
        
        country_data = FLAGS_DB[self.current_country]
        similar = [c for c in FLAGS_DB.keys() if FLAGS_DB[c]["grupo"] == country_data["grupo"] and c != self.current_country]
        options = [self.current_country]
        if len(similar) >= 3:
            random.shuffle(similar)
            options.extend(similar[:3])
        else:
            options.extend(similar)
            other = [c for c in FLAGS_DB.keys() if c not in options]
            random.shuffle(other)
            options.extend(other[:4 - len(options)])
            
        random.shuffle(options)
        self.current_options = options
        
        self.lbl_q_val.configure(text=f"{t['question']} {self.total_questions}")
        self.lbl_score_val.configure(text=f"{self.score} {t['pts']}")
        self.lbl_lives.configure(text=" ".join(["❤️" for _ in range(max(0, self.lives))]) + " " + " ".join(["🖤" for _ in range(max(0, 3 - self.lives))]))
        self.lbl_streak.configure(text=f"🔥 {self.streak}" if self.streak >= 2 else "", fg="#f43f5e" if self.streak >= 2 else CARD_BG)
        
        self.lbl_flag.configure(image="", text=t["loading"], fg=MUTED)
        self.update_idletasks()
        
        path = get_flag_path(country_data["code"])
        name_key = "nombre" if self.lang == "es" else "nombre_en"
        if path and os.path.exists(path):
            try:
                img = Image.open(path)
                w, h = img.size
                ratio = min(320 / w, 192 / h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
                
                self.flag_photo = ImageTk.PhotoImage(img)
                self.lbl_flag.configure(image=self.flag_photo, text="")
            except Exception:
                self.lbl_flag.configure(image="", text=f"[{country_data[name_key]}]", fg=TEXT)
        else:
            self.lbl_flag.configure(image="", text=f"[{country_data[name_key]}]", fg=TEXT)
            
        for i, b in enumerate(self.opt_btns):
            b.configure(text=f"{i+1}.  {FLAGS_DB[self.current_options[i]][name_key]}")
            
        self.time_left = max(5, 30 - self.streak - ((self.total_questions - 1) // 2))
        self.tick_timer()

    def tick_timer(self):
        if self.time_left > 0 and not self.is_answered:
            self.lbl_timer.configure(text=f"{self.time_left}s", fg=TEXT if self.time_left > 15 else YELLOW if self.time_left > 5 else RED)
            self.time_left -= 1
            self.timer_id = self.after(1000, self.tick_timer)
        elif self.time_left == 0 and not self.is_answered:
            self.evaluate_choice(-1)

    def evaluate_choice(self, idx):
        if self.is_answered: return
        self.is_answered = True
        t = TRANSLATIONS[self.lang]
        correct = (idx != -1 and self.current_options[idx] == self.current_country)
        for i, btn in enumerate(self.opt_btns):
            is_correct = (self.current_options[i] == self.current_country)
            btn.configure(state="disabled", bg=GREEN if is_correct else RED if i == idx else "#27272a", disabledforeground=TEXT if (is_correct or i == idx) else MUTED)
        if correct:
            self.correct_count += 1
            self.streak += 1
            self.max_streak = max(self.max_streak, self.streak)
            self.score += (100 * ((self.correct_count // 5) + 1)) + (20 * (self.streak - 1) if self.streak >= 2 else 0)
            self.lbl_score_val.configure(text=f"{self.score} {t['pts']}")
        else:
            self.incorrect_count += 1
            self.lives -= 1
            self.streak = 0
            self.lbl_lives.configure(text=" ".join(["❤️" for _ in range(max(0, self.lives))]) + " " + " ".join(["🖤" for _ in range(max(0, 3 - self.lives))]))
        self.lbl_streak.configure(text=f"🔥 {self.streak}" if self.streak >= 2 else "", fg="#f43f5e" if self.streak >= 2 else CARD_BG)
        self.btn_next.pack(fill="x", pady=(15, 0), ipady=8)
        self.btn_next.configure(
            text=t["results"] if self.lives <= 0 else t["next_flag"],
            bg=RED if self.lives <= 0 else BLUE, activebackground="#991b1b" if self.lives <= 0 else "#0369a1",
            command=self.end_game if self.lives <= 0 else self.spawn_question
        )

    def end_game(self):
        t = TRANSLATIONS[self.lang]
        def draw():
            total = self.correct_count + self.incorrect_count
            acc = round((self.correct_count / total) * 100) if total > 0 else 0
            tk.Label(self, text=t["game_over"], fg=RED, bg=BG, font=("Segoe UI", 18, "bold")).pack(pady=(15, 5))
            sf = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
            sf.pack(fill="x", padx=20, pady=5, ipady=5)
            tk.Label(sf, text=f"{self.score} {t['pts']}", fg=BLUE, bg=CARD_BG, font=("Segoe UI", 24, "bold")).pack()
            grid = tk.Frame(sf, bg=CARD_BG)
            grid.pack(fill="x", pady=2)
            grid.columnconfigure((0, 1, 2), weight=1)
            stats = [(self.correct_count, t["correct"], 0), (f"{acc}%", t["accuracy"], 1), (f"🔥 {self.max_streak}", t["streak"], 2)]
            for val, label_text, col in stats:
                c = tk.Frame(grid, bg=CARD_BG)
                c.grid(row=0, column=col)
                tk.Label(c, text=str(val), fg=TEXT, bg=CARD_BG, font=("Segoe UI", 12, "bold")).pack()
                tk.Label(c, text=label_text, fg=MUTED, bg=CARD_BG, font=("Segoe UI", 8)).pack()
            if self.score > 0:
                reg = tk.Frame(sf, bg=CARD_BG)
                reg.pack(fill="x", padx=15, pady=5)
                entry = tk.Entry(reg, bg=BG, fg=TEXT, insertbackground=TEXT, font=("Segoe UI", 10), bd=1, relief="solid")
                entry.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 6))
                entry.insert(0, t["player"])
                def save():
                    self.save_record_local(entry.get()[:15].strip() or t["player"], self.score, f"{acc}%")
                    messagebox.showinfo(t["record_title"], t["record_saved"])
                    self.end_game()
                Btn(reg, text=t["register"], bg=BLUE, hover_bg="#0369a1", font=("Segoe UI", 9, "bold"), command=save).pack(side="right")
            lf = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
            lf.pack(fill="both", expand=True, padx=20, pady=5)
            tk.Label(lf, text=t["high_scores"], fg=TEXT, bg=CARD_BG, font=("Segoe UI", 11, "bold")).pack(pady=4)
            records = self.load_records()
            if not records:
                tk.Label(lf, text=t["no_records"], fg=MUTED, bg=CARD_BG, font=("Segoe UI", 9, "italic")).pack(pady=20)
            else:
                hdr = tk.Frame(lf, bg="#27272a")
                hdr.pack(fill="x", ipady=2)
                tk.Label(hdr, text=t["col_pos"], fg=MUTED, bg="#27272a", font=("Segoe UI", 8, "bold"), width=5).pack(side="left")
                tk.Label(hdr, text=t["col_name"], fg=MUTED, bg="#27272a", font=("Segoe UI", 8, "bold"), width=20, anchor="w").pack(side="left")
                tk.Label(hdr, text=t["col_points"], fg=MUTED, bg="#27272a", font=("Segoe UI", 8, "bold"), width=12).pack(side="left")
                tk.Label(hdr, text=t["col_accuracy"], fg=MUTED, bg="#27272a", font=("Segoe UI", 8, "bold"), width=10).pack(side="left")
                for idx, r in enumerate(records[:10]):
                    row = tk.Frame(lf, bg=CARD_BG)
                    row.pack(fill="x", ipady=2, padx=5)
                    rank = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f" {idx+1} "
                    tk.Label(row, text=rank, fg=TEXT, bg=CARD_BG, font=("Segoe UI", 9, "bold"), width=5).pack(side="left")
                    tk.Label(row, text=r["nombre"], fg=TEXT, bg=CARD_BG, font=("Segoe UI", 9), width=20, anchor="w").pack(side="left")
                    tk.Label(row, text=f"{r['puntos']}", fg=BLUE, bg=CARD_BG, font=("Segoe UI", 9, "bold"), width=12).pack(side="left")
                    tk.Label(row, text=r["precision"], fg=YELLOW, bg=CARD_BG, font=("Segoe UI", 9, "italic"), width=10).pack(side="left")
                    tk.Frame(lf, bg=BORDER, height=1).pack(fill="x")
            bf = tk.Frame(self, bg=BG)
            bf.pack(fill="x", padx=20, pady=(5, 15))
            Btn(bf, text=t["play_again"], bg=GREEN, hover_bg="#16a34a", font=("Segoe UI", 11, "bold"), command=self.show_language_menu).pack(fill="x", side="left", expand=True, padx=(0, 5), ipady=6)
            Btn(bf, text=t["exit"], bg="#3f3f46", hover_bg="#52525b", font=("Segoe UI", 11, "bold"), command=self.quit).pack(fill="x", side="left", expand=True, padx=(5, 0), ipady=6)
        self.show_screen(draw)

    def load_records(self):
        path = os.path.join(os.path.dirname(__file__), "records.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f: return json.load(f)
            except Exception: pass
        return []
        
    def save_record_local(self, name, score, acc):
        path = os.path.join(os.path.dirname(__file__), "records.json")
        recs = self.load_records()
        recs.append({"nombre": name or "Jugador", "puntos": score, "precision": acc})
        recs.sort(key=lambda x: x["puntos"], reverse=True)
        try:
            with open(path, "w", encoding="utf-8") as f: json.dump(recs[:10], f, indent=4, ensure_ascii=False)
        except Exception: pass

if __name__ == "__main__":
    app = GuessTheFlagApp()
    app.mainloop()
