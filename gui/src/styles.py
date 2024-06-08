COLOR_PALETTE = {
    "primary": "#040F16",
    "primary_light": "#2c373e",

    "secondary": "#005E7C",
    "secondary_light": "#2886a4",
    "secondary_triadic_1": "#5e7c00",
    "secondary_triadic_2": "#7c005e",

    "accent": "#7fc9e2",
    "accent_dark": "#3f6471",
    "accent_triadic_1": "#c9e27f",
    "accent_triadic_2": "#e27fc9",

    "gray": "#808080",
}		

FONT_FAMILY = "Arial"


CHECKBOX_STYLE = {
    "fg_color": COLOR_PALETTE["primary"],
    "bg_color": "transparent",
    "text_color": "white",
}


BUTTON_STYLE = {
    "fg_color": COLOR_PALETTE["primary"],
    "text_color": "white",
    "text_color_disabled": "white",
    "hover_color": COLOR_PALETTE["primary_light"],
}

BUTTON_STYLE_DISABLED = {
    "fg_color": COLOR_PALETTE["gray"],
    "text_color": "white",
    "text_color_disabled": "white",
}


TOOL_BUTTON_STYLE = {
    "fg_color": "transparent",
    "hover_color": COLOR_PALETTE["secondary_light"],
}


ACTION_BUTTON_STYLE = {
    "fg_color": COLOR_PALETTE["accent"],
    "text_color": COLOR_PALETTE["primary"],
    "text_color_disabled": COLOR_PALETTE["primary"],
}


PLACEHOLDER_BUTTON_STYLE = {
    "fg_color": COLOR_PALETTE["secondary"],
    "text_color": "white",
    "hover_color": COLOR_PALETTE["secondary_light"],
    "font": (FONT_FAMILY, 22, "bold"),
}


SLIDER_STYLE = {
    "button_color": COLOR_PALETTE["primary"],
    "progress_color": COLOR_PALETTE["accent"],
}

SLIDER_STYLE_DISABLED = {
    "button_color": COLOR_PALETTE["gray"],
    "progress_color": COLOR_PALETTE["gray"],
}


PROGRESS_BAR_STYLE = {
    "bg_color": COLOR_PALETTE["primary"],
    "progress_color": COLOR_PALETTE["accent"],
}


LABEL_STYLE = {
    "fg_color": "transparent",
    "text_color": "white",
}


ENTRY_STYLE = {
    "fg_color": COLOR_PALETTE["primary"],
    "text_color": "white",
}

OPTION_MENU_STYLE = {
    "fg_color": COLOR_PALETTE["primary"],
    "text_color": "white",
    "button_color": COLOR_PALETTE["primary"],
    "dropdown_fg_color": COLOR_PALETTE["primary"],
    "dropdown_hover_color": COLOR_PALETTE["primary_light"],
}


TOOLTIP_STYLE = {
    "fg_color": COLOR_PALETTE["primary"],
    "text_color": "white",
    "font": (FONT_FAMILY, 11),
}