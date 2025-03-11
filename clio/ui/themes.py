from textual.theme import Theme

THEMES = {
    "dark": Theme(
        name="clio-dark",
        primary="#4c1818",
        secondary="#03DAC6",
        warning="#FAE3B0",
        error="#CF6679",
        success="#ABE9B3",
        accent="#ff0000",
        background="#ff0000",
        surface="#1E1E1E",
        panel="#292929",
        variables={
            "input-cursor-foreground": "#E0E0E0",
            "input-selection-background": "#575757",
            "border": "#757575",
            "footer-background": "#292929",
        },
    ),
    "light": Theme(
        name="clio-light",
        primary="#F5C2E7",
        secondary="#cba6f7",
        warning="#FAE3B0",
        error="#F28FAD",
        success="#ABE9B3",
        accent="#fab387",
        background="#181825",
        surface="#313244",
        panel="#45475a",
        variables={
            "input-cursor-foreground": "#11111b",
            "input-selection-background": "#9399b2 30%",
            "border": "#b4befe",
            "footer-background": "#45475a",
        },
    ),
}

def get_theme(name: str) -> Theme:
    """Return a Theme object based on name, defaults to 'dark'."""
    return THEMES.get(name, THEMES["dark"])

