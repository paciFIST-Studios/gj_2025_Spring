
from src.gembo.renderer.render_mode import MenuRenderModeBase, EGameMode, EColor, Surface


# settings
class SettingsMenuRenderMode(MenuRenderModeBase):
    def __init__(self, engine, surface: Surface, mode: EGameMode, render_dict: dict):
        super().__init__(engine, surface, mode, render_dict)
        self.settings = self.value_or_default('settings')
        self.selection_font = self.value_or_default('selection_font')

    def render(self):
        self.render_menu_floor_box()
        self.render_title_text('Settings')
        self.render_settings_mode_options_text()

    def render_settings_mode_options_text(self):
        options = self.settings.get_settings_options()

        x_pos, y_pos = 60, 90
        for settings_property, is_selected in options:
            string = settings_property
            color = EColor.HIGHLIGHT_YELLOW if is_selected else EColor.COOL_GREY
            text = self.selection_font.render(string, True, color)
            self.render_surface.blit(text, (x_pos, y_pos))
            y_pos += 60

