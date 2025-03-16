
from src.gembo.renderer.render_mode import RenderMenuBase, EUpdateMode, EColor, Surface


# settings
class RenderSettingsMenu(RenderMenuBase):
    def __init__(self, engine, surface: Surface, mode: EUpdateMode, render_dict: dict):
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
        for settings_property, is_selected, value in options:
            string = settings_property
            color = self.engine.ui.get_highlight_color() if is_selected else self.engine.ui.get_unhighlight_color()
            text = self.selection_font.render(string, True, color)
            self.render_surface.blit(text, (x_pos, y_pos))

            if is_selected:
                if settings_property in ['sfx']:
                    self.render_horizontal_fill_bar(self.selection_font, (x_pos+120, y_pos), value*10, 10)
                elif settings_property in ['mute']:
                    self.render_on_off_toggle(self.selection_font ,(x_pos+150, y_pos), value)
                elif settings_property in ['color']:
                    renderable_text = self.selection_font.render(value, True, self.engine.ui.get_highlight_color())
                    self.render_surface.blit(renderable_text, (x_pos+150, y_pos))

            y_pos += 60
