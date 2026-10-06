"""Rounded blue buttons, using only Tkinter and its native button bindings."""
import math
import tkinter as tk
from tkinter import font as tkfont


BLUE = "#3563e9"
BLUE_HOVER = "#4474f2"
BLUE_SHADOW = "#2445a5"
BLUE_NAV = "#2b50bb"


class _RoundedStyle:
    def __init__(self, master, **options):
        # Keep native Button/Menubutton behavior (invoke, menus, keyboard, state).
        self._face = BLUE
        self._hovered = False
        self._surface = None
        self._source_image = options.pop("image", None)
        self._source_compound = options.pop("compound", "center")
        self._label = options.pop("text", "")
        self._width_chars = options.pop("width", 0)
        self._height_lines = options.pop("height", 0)
        self._pad_x = max(14, int(options.pop("padx", 14)))
        self._pad_y = max(10, int(options.pop("pady", 10)))
        self._button_font = tkfont.Font(master, font=options.pop("font", ("Segoe UI", 10)))
        self._button_font.configure(weight="bold")
        for key in ("bg", "background", "fg", "foreground", "activebackground",
                    "activeforeground", "disabledforeground", "relief", "bd",
                    "borderwidth", "highlightthickness", "anchor", "cursor", "takefocus"):
            options.pop(key, None)
        super().__init__(
            master, **options, bg=master.cget("bg"), fg="white",
            activebackground=master.cget("bg"), activeforeground="white",
            disabledforeground="#edf2ff", relief="flat", borderwidth=0,
            highlightthickness=0, padx=0, pady=0, compound="center",
            font=self._button_font, cursor="hand2", takefocus=True,
            text=self._display_text(),
        )
        self._resize()
        self.bind("<Configure>", self._paint, add="+")
        self.bind("<Enter>", self._enter, add="+")
        self.bind("<Leave>", self._leave, add="+")
        self.bind("<ButtonPress-1>", self._press, add="+")
        self.bind("<ButtonRelease-1>", self._release, add="+")
        self.bind("<KeyPress-space>", self._press, add="+")
        self.bind("<KeyRelease-space>", self._release, add="+")
        self.bind("<FocusIn>", self._paint, add="+")
        self.bind("<FocusOut>", self._paint, add="+")
        self._pressed = False
        self._paint()

    def _resize(self, width=None, height=None):
        lines = str(self._label).split("\n")
        text_width = max((self._button_font.measure(line) for line in lines), default=0)
        wrap = self.winfo_pixels(super().cget("wraplength"))
        line_count = len(lines)
        if wrap:
            line_count = sum(max(1, math.ceil(self._button_font.measure(line) / wrap)) for line in lines)
            text_width = min(text_width, wrap)
        image_width = self._source_image.width() if self._source_image else 0
        image_height = self._source_image.height() if self._source_image else 0
        if self._source_compound == "left" and image_width:
            text_width += image_width + 12
        char_width = self._width_chars * self._button_font.measure("0")
        content_height = max(line_count, self._height_lines) * self._button_font.metrics("linespace")
        super().configure(
            width=max(width, image_width + 14) if width is not None else max(text_width, char_width, image_width) + self._pad_x * 2,
            height=max(height, image_height + 14) if height is not None else max(48, content_height + self._pad_y * 2 + 6, image_height + 14),
        )

    def _display_text(self):
        if self._source_image and self._source_compound == "left":
            spaces = math.ceil((self._source_image.width() + 12) / self._button_font.measure(" "))
            return " " * spaces + self._label
        return self._label

    @staticmethod
    def _blend(background, foreground, coverage):
        return "#" + "".join(
            f"{round(value * (1 - coverage) + int(foreground[i:i + 2], 16) * coverage):02x}"
            for value, i in zip(background, (1, 3, 5))
        )

    def _rounded(self, image, x, y, width, height, radius, color):
        radius = min(radius, width / 2, height / 2)
        for row in range(height):
            distance = max(radius - row - 0.5, row + 0.5 - (height - radius), 0)
            inset = radius - math.sqrt(max(0, radius ** 2 - distance ** 2))
            edge = math.ceil(inset)
            left, right = x + edge, x + width - edge
            if right > left:
                image.put(color, to=(left, y + row, right, y + row + 1))
            if edge:
                for column in (left - 1, right):
                    smooth = self._blend(image.get(column, y + row), color, edge - inset)
                    image.put(smooth, to=(column, y + row))

    def _paint(self, _event=None):
        width = self.winfo_width() if self.winfo_width() > 1 else int(super().cget("width"))
        height = self.winfo_height() if self.winfo_height() > 1 else int(super().cget("height"))
        if width < 8 or height < 8:
            return
        background = self.master.cget("bg")
        background = "#" + "".join(f"{value // 257:02x}" for value in self.winfo_rgb(background))
        disabled = str(super().cget("state")) == "disabled"
        face = "#96afea" if disabled else BLUE_HOVER if self._hovered else self._face
        shadow = "#7189bc" if disabled else BLUE_SHADOW
        pressed = getattr(self, "_pressed", False) and not disabled
        image = tk.PhotoImage(master=self, width=width, height=height)
        image.put(background, to=(0, 0, width, height))
        radius = min(20, (height - 6) * 0.3)
        self._rounded(image, 2, 6, width - 4, height - 8, radius, shadow)
        self._rounded(image, 2, 5 if pressed else 1, width - 4, height - 8, radius, face)
        if self.focus_get() == self:
            # A blue outline outside the face keeps keyboard focus visible.
            self._rounded(image, 0, 0, width, height, radius + 2, "#9ab8ff")
            self._rounded(image, 2, 6, width - 4, height - 8, radius, shadow)
            self._rounded(image, 2, 5 if pressed else 1, width - 4, height - 8, radius, face)
        if self._source_image:
            source = self._source_image
            x = self._pad_x if self._source_compound == "left" else (width - source.width()) // 2
            y = (height - source.height()) // 2
            self.tk.call(str(image), "copy", str(source), "-to", max(2, x), max(2, y))
        self._surface = image
        super().configure(image=image, background=background, activebackground=background)

    def _enter(self, _event):
        self._hovered = True
        self._paint()

    def _leave(self, _event):
        self._hovered = False
        self._pressed = False
        self._paint()

    def _press(self, _event):
        self._pressed = True
        self._paint()

    def _release(self, _event):
        self._pressed = False
        self._paint()

    def configure(self, cnf=None, **options):
        if cnf is not None:
            if not isinstance(cnf, dict):
                return super().configure(cnf, **options)
            options = {**cnf, **options}
        if not options:
            return super().configure()
        resize = "text" in options or "font" in options or "image" in options
        width, height = options.pop("width", None), options.pop("height", None)
        if "image" in options:
            self._source_image = options.pop("image") or None
        if "compound" in options:
            self._source_compound = options.pop("compound")
        if "font" in options:
            self._button_font.configure(**tkfont.Font(self, font=options.pop("font")).actual())
            self._button_font.configure(weight="bold")
        if "text" in options:
            self._label = options.pop("text")
        options["text"] = self._display_text()
        for key in ("bg", "background", "fg", "foreground", "activebackground",
                    "activeforeground", "disabledforeground", "highlightthickness",
                    "highlightbackground", "highlightcolor", "borderwidth", "bd"):
            options.pop(key, None)
        super().configure(**options)
        if resize or width is not None or height is not None:
            self._resize(width, height)
        self._paint()

    config = configure

    def cget(self, key):
        if key == "text":
            return self._label
        if key in ("bg", "background"):
            return self._face
        return super().cget(key)

    def set_selected(self, selected):
        self._face = BLUE if selected else BLUE_NAV
        self._paint()


class RoundedButton(_RoundedStyle, tk.Button):
    pass


class RoundedMenubutton(_RoundedStyle, tk.Menubutton):
    pass
