import customtkinter as ctk
from styles import COLOR_PALETTE, ACTION_BUTTON_STYLE, LABEL_STYLE, ENTRY_STYLE

class SettingsPopUp(ctk.CTkToplevel):
    PADDING = 10

    def __init__(self, window_title, settings):
        self.settings = settings
        self.window_title = window_title


    def open(self, *args, **kwargs):
        super().__init__(
            fg_color=COLOR_PALETTE["primary"],
            *args, **kwargs
        )

        self.title(self.window_title)

        self.load_widgets()

        self.grab_set()

        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()

        x = self.master.winfo_rootx() + parent_width // 2 - self.winfo_width() // 2
        y = self.master.winfo_rooty() + parent_height // 2 - self.winfo_height() // 2

        self.geometry(f"+{x}+{y}")

        self.wait_window()


    def load_widgets(self):
        for i, (key, value) in enumerate(self.settings.items()):
            label = ctk.CTkLabel(self, text=f"{key.replace('_', ' ').capitalize()}:", **LABEL_STYLE)
            label.grid(column=0, row=i, sticky="w", padx=self.PADDING, pady=self.PADDING)
            
            entry = ctk.CTkEntry(self, textvariable=value, **ENTRY_STYLE)
            entry.grid(column=1, row=i, sticky="e", padx=self.PADDING, pady=self.PADDING)

        button = ctk.CTkButton(self, text="Close", command=self.on_close, **ACTION_BUTTON_STYLE)
        button.grid(column=0, row=len(self.settings), columnspan=2, padx=self.PADDING, pady=self.PADDING)

    
    def on_close(self):
        self.destroy()

