import customtkinter as ctk

class ToolsPanel(ctk.CTkFrame):
    PADDING = (1, 2)

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.buttons_count = 0


    def add_button(self, button):
        column = self.buttons_count % 2
        row = self.buttons_count // 2

        button.grid(row=row,
            column=column,
            padx=self.PADDING[0],
            pady=self.PADDING[1],
            sticky="nsew"
        )

        self.buttons_count += 1