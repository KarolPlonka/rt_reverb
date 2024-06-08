import customtkinter as ctk

from styles import COLOR_PALETTE, TOOL_BUTTON_STYLE, TOOLTIP_STYLE
from PIL import Image


class ToolButton(ctk.CTkButton):
    ACTIVE_COLOR = COLOR_PALETTE['accent']

    ICON_SIZE = (30, 30)    

    PADDING = (3, 0)

    def __init__(self, panel, command, icon_path, tool_name, set_status_bar_text):
        self.command = command
        self.panel = panel

        self.icon = ctk.CTkImage(Image.open(icon_path), size=self.ICON_SIZE)

        super().__init__(
            self.panel,
            command=self.command,
            image=self.icon,
            text=None,
            width=self.ICON_SIZE[0],
            **TOOL_BUTTON_STYLE,
        )

        self.bind("<Enter>", lambda event, tool_name=tool_name: set_status_bar_text(tool_name))
        self.bind("<Leave>", lambda event: set_status_bar_text(""))

        self.panel.add_button(self)


    def tool_active(self):
        self.configure(
            fg_color=ToolButton.ACTIVE_COLOR,
            hover_color=ToolButton.ACTIVE_COLOR,
        )


    def tool_inactive(self):
        self.configure(
            fg_color=TOOL_BUTTON_STYLE['fg_color'],
            hover_color=TOOL_BUTTON_STYLE['hover_color'],
        )
