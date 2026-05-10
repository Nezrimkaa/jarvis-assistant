"""GUI J.A.R.V.I.S. — интерфейс в стиле Железного Человека."""
import queue
import tkinter as tk
from tkinter import font as tkfont
from threading import Thread
from typing import Callable, Optional

from config import Config
from settings import SettingsWindow


class JarvisGUI:
    """Графический интерфейс в стиле Железного Человека (Iron Man HUD)."""

    # Цвета интерфейса Железного Человека
    BG = "#000000"
    BG_DARK = "#0a0e17"
    ACCENT = "#00d4ff"        # Голубой неон
    ACCENT_GLOW = "#00ffff"   # Яркое свечение
    ACCENT_DIM = "#0088aa"    # Тусклый голубой
    TEXT_PRIMARY = "#e0f7ff"  # Белый с голубым оттенком
    TEXT_SECONDARY = "#5a7a8a" # Тускло-голубой
    TEXT_GLOW = "#00d4ff"     # Светящийся текст
    BOT_BUBBLE = "#0d1b2a"    # Темно-синий пузырь
    USER_BUBBLE = "#003d5c"   # Синий пузырь
    INPUT_BG = "#0d1b2a"
    DIVIDER = "#1a3a4a"
    BORDER = "#00d4ff"
    BORDER_GLOW = "#00ffff"

    def __init__(
        self,
        on_text_message: Callable[[str], None],
        on_voice_button: Callable,
        on_settings_button: Callable = None,
        on_minimize_to_tray: Callable = None,
    ):
        self.on_text_message = on_text_message
        self.on_voice_button = on_voice_button
        self.on_settings_button = on_settings_button
        self.on_minimize_to_tray = on_minimize_to_tray
        self.msg_queue: queue.Queue = queue.Queue()
        self.typing_after_id = None
        self._is_listening = False

        self._build_window()
        self._check_queue()

    # ------------------------------------------------------------------
    # Сборка окна
    # ------------------------------------------------------------------
    def _build_window(self):
        self.root = tk.Tk()
        self.root.title(Config.BOT_NAME)
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.configure(bg=self.BG)
        self.root.minsize(Config.WINDOW_MIN_WIDTH, Config.WINDOW_MIN_HEIGHT)

        # Убираем стандартные границы Windows
        self.root.overrideredirect(True)
        
        # Центрируем окно
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - Config.WINDOW_WIDTH) // 2
        y = (screen_height - Config.WINDOW_HEIGHT) // 2
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}+{x}+{y}")

        # Шрифты
        self.font_main = tkfont.Font(family="Segoe UI", size=11)
        self.font_header = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        self.font_small = tkfont.Font(family="Segoe UI", size=9)
        self.font_mono = tkfont.Font(family="Consolas", size=10)

        # Главный контейнер с голубой рамкой
        main_container = tk.Frame(self.root, bg=self.BG, highlightbackground=self.ACCENT, highlightthickness=1)
        main_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Верхняя панель (стиль Железного Человека)
        self._build_header(main_container)

        # Область сообщений
        self._build_chat_area(main_container)

        # Нижняя панель ввода
        self._build_input_area(main_container)

        # Приветствие
        self._add_system_bubble("J.A.R.V.I.S. система активна")
        self._add_system_bubble("Скажите 'Джарвис' для голосовой активации")

        # Запускаем анимацию статуса
        self._pulse_status()
        
        # Обработка закрытия
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_header(self, parent):
        """Построить верхнюю панель."""
        header = tk.Frame(parent, bg=self.BG_DARK, height=70)
        header.pack(fill=tk.X, padx=2, pady=(2, 0))
        header.pack_propagate(False)

        # Анимированный аватар J.A.R.V.I.S.
        self.avatar_canvas = tk.Canvas(header, width=50, height=50, bg=self.BG_DARK, highlightthickness=0)
        self.avatar_canvas.pack(side=tk.LEFT, padx=(20, 15), pady=10)
        
        # Create animated rings
        self.avatar_items = []
        center = 25
        
        # Outer pulsing ring
        self.ring1 = self.avatar_canvas.create_oval(
            center-23, center-23, center+23, center+23,
            outline=self.ACCENT, width=2, fill=""
        )
        
        # Middle ring
        self.ring2 = self.avatar_canvas.create_oval(
            center-18, center-18, center+18, center+18,
            outline=self.ACCENT_GLOW, width=1, fill=""
        )
        
        # Inner solid circle
        self.circle = self.avatar_canvas.create_oval(
            center-12, center-12, center+12, center+12,
            fill=self.ACCENT, outline=""
        )
        
        # Letter J
        self.j_letter = self.avatar_canvas.create_text(
            center, center, text="J",
            font=tkfont.Font(family="Segoe UI", size=18, weight="bold"),
            fill=self.BG_DARK
        )

        # Имя и статус
        name_frame = tk.Frame(header, bg=self.BG_DARK)
        name_frame.pack(side=tk.LEFT, pady=15)
        
        tk.Label(
            name_frame,
            text="J.A.R.V.I.S.",
            font=self.font_header,
            fg=self.ACCENT,
            bg=self.BG_DARK,
        ).pack(anchor="w")
        
        # Статус с фиксированной высотой и отступами
        status_frame = tk.Frame(name_frame, bg=self.BG_DARK, height=20)
        status_frame.pack(anchor="w", pady=(2, 0))
        status_frame.pack_propagate(False)
        
        self.status_dot = tk.Label(
            status_frame,
            text="●",
            font=tkfont.Font(size=8),
            fg=self.ACCENT,
            bg=self.BG_DARK,
        )
        self.status_dot.pack(side=tk.LEFT, padx=(0, 3))
        
        self.status_label = tk.Label(
            status_frame,
            text="ONLINE",
            font=tkfont.Font(family="Segoe UI", size=8, weight="bold"),
            fg=self.ACCENT_DIM,
            bg=self.BG_DARK,
        )
        self.status_label.pack(side=tk.LEFT)

        # Кнопки управления окном
        controls_frame = tk.Frame(header, bg=self.BG_DARK)
        controls_frame.pack(side=tk.RIGHT, padx=20)

        for symbol, action, color in [
            ("−", self._minimize_to_tray, self.TEXT_SECONDARY),
            ("⚙", self._show_settings, self.ACCENT),
            ("×", self._on_close, "#ff4444"),
        ]:
            btn = tk.Label(
                controls_frame,
                text=symbol,
                font=tkfont.Font(size=18, weight="bold"),
                fg=color,
                bg=self.BG_DARK,
                cursor="hand2",
                width=3,
            )
            btn.pack(side=tk.LEFT, padx=(0, 10))
            btn.bind("<Button-1>", lambda e, a=action: a())
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(fg=self.ACCENT_GLOW))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(fg=c))

        # Start animations after all widgets are created
        self._animate_avatar()
        self._pulse_status_dot()

    def _build_chat_area(self, parent):
        """Построить область чата."""
        chat_container = tk.Frame(parent, bg=self.BG)
        chat_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.canvas = tk.Canvas(chat_container, bg=self.BG, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(
            chat_container,
            orient="vertical",
            command=self.canvas.yview,
            bg=self.BG,
            troughcolor=self.BG_DARK,
            activebackground=self.ACCENT_DIM,
            highlightthickness=0,
            bd=0,
            width=8,
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.BG)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5))
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _build_input_area(self, parent):
        """Построить панель ввода."""
        input_container = tk.Frame(parent, bg=self.BG_DARK, padx=15, pady=12)
        input_container.pack(fill=tk.X, padx=2, pady=(0, 2))

        input_row = tk.Frame(input_container, bg=self.BG_DARK)
        input_row.pack(fill=tk.X)

        # Кнопка микрофона с тултипом
        self.mic_btn = tk.Label(
            input_row,
            text="●",
            font=tkfont.Font(size=20),
            fg=self.ACCENT,
            bg=self.BG_DARK,
            cursor="hand2",
        )
        self.mic_btn.pack(side=tk.LEFT, padx=(0, 15))
        self.mic_btn.bind("<Button-1>", lambda e: self._voice())
        self.mic_btn.bind("<Enter>", lambda e: (self.mic_btn.config(fg=self.ACCENT_GLOW), self._show_tooltip(e, "Голосовой ввод")))
        self.mic_btn.bind("<Leave>", lambda e: (self.mic_btn.config(fg=self.ACCENT), self._hide_tooltip()))

        # Поле ввода с голубой рамкой и тенью
        entry_frame = tk.Frame(input_row, bg=self.INPUT_BG, padx=15, pady=10,
                              highlightbackground=self.ACCENT, highlightthickness=1)
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.entry = tk.Entry(
            entry_frame,
            font=self.font_main,
            bg=self.INPUT_BG,
            fg=self.TEXT_PRIMARY,
            insertbackground=self.ACCENT,
            relief=tk.FLAT,
            bd=0,
        )
        self.entry.pack(fill=tk.X, expand=True)
        self.entry.bind("<Return>", lambda e: self._send())
        
        # Copy-Paste support for chat input
        def paste_to_entry(event=None):
            try:
                text = self.entry.clipboard_get()
                self.entry.insert(tk.INSERT, text)
                return "break"
            except tk.TclError:
                pass
        
        def copy_from_entry(event=None):
            try:
                if self.entry.selection_present():
                    selected = self.entry.selection_get()
                    self.entry.clipboard_clear()
                    self.entry.clipboard_append(selected)
                    return "break"
            except tk.TclError:
                pass
        
        self.entry.bind("<Control-v>", paste_to_entry)
        self.entry.bind("<Control-V>", paste_to_entry)
        self.entry.bind("<Control-c>", copy_from_entry)
        self.entry.bind("<Control-C>", copy_from_entry)
        self.entry.bind("<Button-3>", lambda e: self._show_entry_context_menu(e))
        
        self.entry.focus()

        # Кнопка отправки с тултипом
        send_btn = tk.Label(
            input_row,
            text="➤",
            font=tkfont.Font(size=22, weight="bold"),
            fg=self.ACCENT,
            bg=self.BG_DARK,
            cursor="hand2",
        )
        send_btn.pack(side=tk.RIGHT, padx=(15, 0))
        send_btn.bind("<Button-1>", lambda e: self._send())
        send_btn.bind("<Enter>", lambda e: (send_btn.config(fg=self.ACCENT_GLOW), self._show_tooltip(e, "Отправить сообщение")))
        send_btn.bind("<Leave>", lambda e: (send_btn.config(fg=self.ACCENT), self._hide_tooltip()))

    def _update_bubble_wraplengths(self, max_width: int):
        """Обновить wraplength для всех существующих пузырей."""
        # Обновляем пользовательские пузыри
        for widget in self.scrollable_frame.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, tk.Label) and child.cget("bg") in (self.USER_BUBBLE, self.BOT_BUBBLE):
                    child.config(wraplength=max_width)
    
    def _on_canvas_configure(self, event):
        """Обновить ширину scrollable_frame и wraplength пузырей."""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width - 20)
        # Обновляем wraplength для всех пузырей
        self._update_bubble_wraplengths(canvas_width - 60)

    # ------------------------------------------------------------------
    # Публичные методы
    # ------------------------------------------------------------------
    def add_user_message(self, text: str):
        self.msg_queue.put(("user", text))

    def add_bot_message(self, text: str):
        self.msg_queue.put(("bot", text))

    def add_system_message(self, text: str):
        self.msg_queue.put(("system", text))

    def set_listening_status(self, listening: bool):
        self._is_listening = listening
        if listening:
            self.status_label.config(text="LISTENING...", fg=self.ACCENT_GLOW)
            self.status_dot.config(fg="#ff9500")
            self.mic_btn.config(fg="#ff9500")
        else:
            self.status_label.config(text="ONLINE", fg=self.ACCENT_DIM)
            self.status_dot.config(fg=self.ACCENT)
            self.mic_btn.config(fg=self.ACCENT)

    def _pulse_status(self):
        """Анимация пульсации статусного индикатора."""
        if not self._is_listening:
            # Мягкая пульсация для ONLINE
            import math
            import time
            # Меняем прозрачность цвета (через яркость)
            current_fg = self.status_dot.cget("fg")
            if current_fg == self.ACCENT:
                self.status_dot.config(fg=self.ACCENT_DIM)
            else:
                self.status_dot.config(fg=self.ACCENT)
        
        # Повторяем каждые 1.5 секунды
        self.root.after(1500, self._pulse_status)

    def run(self):
        self.root.mainloop()

    def destroy(self):
        if self.root:
            try:
                self.root.destroy()
            except tk.TclError:
                pass

    def hide(self):
        if self.root:
            try:
                self.root.withdraw()
            except tk.TclError:
                pass

    def show(self):
        if self.root:
            try:
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
            except tk.TclError:
                pass

    def is_visible(self) -> bool:
        if self.root:
            try:
                return self.root.winfo_viewable()
            except tk.TclError:
                return False
        return False

    # ------------------------------------------------------------------
    # Внутренние
    # ------------------------------------------------------------------
    def _show_entry_context_menu(self, event):
        """Показать контекстное меню для поля ввода."""
        menu = tk.Menu(self.root, tearoff=0)
        
        def paste():
            try:
                text = self.entry.clipboard_get()
                self.entry.insert(tk.INSERT, text)
            except tk.TclError:
                pass
        
        def copy():
            try:
                if self.entry.selection_present():
                    selected = self.entry.selection_get()
                    self.entry.clipboard_clear()
                    self.entry.clipboard_append(selected)
            except tk.TclError:
                pass
        
        def cut():
            copy()
            if self.entry.selection_present():
                self.entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
        
        menu.add_command(label="Копировать", command=copy)
        menu.add_command(label="Вырезать", command=cut)
        menu.add_command(label="Вставить", command=paste)
        menu.post(event.x_root, event.y_root)

    def _send(self):
        text = self.entry.get().strip()
        if text:
            self.entry.delete(0, tk.END)
            self.add_user_message(text)
            Thread(target=self.on_text_message, args=(text,), daemon=True).start()

    def _voice(self):
        Thread(target=self.on_voice_button, daemon=True).start()

    def _minimize_to_tray(self):
        if self.on_minimize_to_tray:
            self.on_minimize_to_tray()
        else:
            self.hide()

    def _show_settings(self):
        if self.on_settings_button:
            self.on_settings_button()

    def _on_close(self):
        self._minimize_to_tray()

    def _check_queue(self):
        while not self.msg_queue.empty():
            sender, text = self.msg_queue.get()
            if sender == "user":
                self._add_user_bubble(text)
            elif sender == "bot":
                self._add_bot_bubble(text)
            else:
                self._add_system_bubble(text)
        self.root.after(100, self._check_queue)

    # ------------------------------------------------------------------
    # Пузыри сообщений в стиле Железного Человека
    # ------------------------------------------------------------------
    def _get_bubble_max_width(self) -> int:
        """Получить максимальную ширину пузыря."""
        try:
            return max(250, self.canvas.winfo_width() - 80)
        except:
            return 300

    def _add_user_bubble(self, text: str):
        """Пузырь пользователя (справа, синий) с улучшенным дизайном."""
        row = tk.Frame(self.scrollable_frame, bg=self.BG, pady=5)
        row.pack(fill=tk.X, padx=10)

        spacer = tk.Frame(row, bg=self.BG)
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Контейнер с закруглением
        bubble_container = tk.Frame(
            row,
            bg=self.USER_BUBBLE,
            highlightbackground=self.ACCENT_DIM,
            highlightthickness=1,
        )
        bubble_container.pack(side=tk.RIGHT, padx=(0, 5))

        max_width = self._get_bubble_max_width()
        bubble = tk.Label(
            bubble_container,
            text=text,
            font=self.font_main,
            fg=self.TEXT_PRIMARY,
            bg=self.USER_BUBBLE,
            padx=14,
            pady=8,
            wraplength=max_width,
            justify=tk.LEFT,
        )
        bubble.pack()
        
        # Right-click to copy
        bubble.bind("<Button-3>", lambda e, t=text: self._copy_bubble_text(t))
        
        # Ctrl+C to copy bubble text
        bubble.bind("<Control-c>", lambda e, t=text: self._copy_bubble_text(t))
        bubble.bind("<Control-C>", lambda e, t=text: self._copy_bubble_text(t))

        self._scroll_to_bottom()

    def _copy_bubble_text(self, text: str):
        """Копировать текст пузыря в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.add_system_message("Текст скопирован в буфер обмена")

    def _add_bot_bubble(self, text: str):
        """Пузырь бота (слева, темный с голубым свечением) с улучшенным дизайном."""
        row = tk.Frame(self.scrollable_frame, bg=self.BG, pady=5)
        row.pack(fill=tk.X, padx=10)

        bubble_container = tk.Frame(
            row,
            bg=self.BOT_BUBBLE,
            highlightbackground=self.ACCENT,
            highlightthickness=1,
        )
        bubble_container.pack(side=tk.LEFT, padx=(5, 0))

        max_width = self._get_bubble_max_width()
        bubble = tk.Label(
            bubble_container,
            text="",
            font=self.font_main,
            fg=self.TEXT_PRIMARY,
            bg=self.BOT_BUBBLE,
            padx=14,
            pady=8,
            wraplength=max_width,
            justify=tk.LEFT,
        )
        bubble.pack()
        
        # Store text for copy
        bubble.full_text = text
        bubble.bind("<Button-3>", lambda e, b=bubble: self._copy_bubble_text(b.full_text))
        
        # Ctrl+C to copy bot bubble text
        bubble.bind("<Control-c>", lambda e, b=bubble: self._copy_bubble_text(b.full_text))
        bubble.bind("<Control-C>", lambda e, b=bubble: self._copy_bubble_text(b.full_text))

        typing_row = tk.Frame(self.scrollable_frame, bg=self.BG, pady=2)
        typing_row.pack(fill=tk.X, padx=10)
        typing_label = tk.Label(
            typing_row,
            text="◆ обрабатываю...",
            font=self.font_small,
            fg=self.ACCENT_DIM,
            bg=self.BG,
        )
        typing_label.pack(side=tk.LEFT, padx=(10, 0))

        self._scroll_to_bottom()
        self._typewriter_effect(bubble, typing_row, text)

    def _add_system_bubble(self, text: str):
        """Системное сообщение (по центру, голубое)."""
        row = tk.Frame(self.scrollable_frame, bg=self.BG, pady=8)
        row.pack(fill=tk.X, padx=10)

        label = tk.Label(
            row,
            text=f"◆ {text} ◆",
            font=self.font_small,
            fg=self.ACCENT_DIM,
            bg=self.BG,
        )
        label.pack(expand=True)

        self._scroll_to_bottom()

    # ------------------------------------------------------------------
    # Эффект печати
    # ------------------------------------------------------------------
    def _typewriter_effect(self, label: tk.Label, typing_frame: tk.Frame, full_text: str, idx: int = 0):
        if idx == 0:
            label.config(text="")

        if idx < len(full_text):
            current = full_text[: idx + 1]
            label.config(text=current)
            self._scroll_to_bottom()
            self.typing_after_id = self.root.after(12, lambda: self._typewriter_effect(label, typing_frame, full_text, idx + 1))
        else:
            typing_frame.destroy()
            self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    # ------------------------------------------------------------------
    # Анимация аватара
    # ------------------------------------------------------------------
    def _animate_avatar(self, frame: int = 0):
        """Анимация пульсации аватара J.A.R.V.I.S."""
        import math
        
        center = 25
        # Pulsing effect using sine wave
        pulse = math.sin(frame * 0.1) * 3
        
        # Update outer ring
        r1 = 23 + pulse
        self.avatar_canvas.coords(self.ring1, center-r1, center-r1, center+r1, center+r1)
        
        # Update middle ring (opposite phase)
        r2 = 18 - pulse * 0.5
        self.avatar_canvas.coords(self.ring2, center-r2, center-r2, center+r2, center+r2)
        
        # Update color intensity
        intensity = int(128 + 127 * math.sin(frame * 0.05))
        color = f"#{intensity:02x}{intensity:02x}ff"
        self.avatar_canvas.itemconfig(self.ring1, outline=color)
        self.avatar_canvas.itemconfig(self.ring2, outline=color)
        
        # Schedule next frame
        self.root.after(50, lambda: self._animate_avatar(frame + 1))
    
    def _pulse_status_dot(self, frame: int = 0):
        """Пульсация статусной точки."""
        import math
        
        # Pulsing opacity effect
        alpha = abs(math.sin(frame * 0.08))
        
        # Change color brightness
        if alpha > 0.7:
            self.status_dot.config(fg=self.ACCENT_GLOW)
        else:
            self.status_dot.config(fg=self.ACCENT_DIM)
        
        self.root.after(100, lambda: self._pulse_status_dot(frame + 1))

    def _show_tooltip(self, event, text: str):
        """Показать тултип."""
        if hasattr(self, '_tooltip') and self._tooltip:
            self._tooltip.destroy()
        
        x = event.widget.winfo_rootx() + event.widget.winfo_width() // 2
        y = event.widget.winfo_rooty() - 25
        
        self._tooltip = tk.Toplevel(self.root)
        self._tooltip.wm_overrideredirect(True)
        self._tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self._tooltip,
            text=text,
            font=tkfont.Font(family="Segoe UI", size=8),
            bg=self.BG_DARK,
            fg=self.ACCENT,
            padx=6,
            pady=2,
        )
        label.pack()

    def _hide_tooltip(self):
        """Скрыть тултип."""
        if hasattr(self, '_tooltip') and self._tooltip:
            self._tooltip.destroy()
            self._tooltip = None
