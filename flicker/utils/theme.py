from pydantic import BaseModel


class Theme(BaseModel):
    sidebar_background_color: str
    # sidebar_text_color: str


class DefaultTheme(Theme):
    sidebar_background_color: str = "#F3F3F3"
    # sidebar_text_color: str = "#D8DEE9"


def getCurrentTheme() -> Theme:
    return DefaultTheme()
