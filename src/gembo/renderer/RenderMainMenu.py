
from pygame.surface import Surface

from src.gembo.update_modes import EUpdateMode
from src.gembo.game_data import EColor
from src.gembo.game_data import MenuData

from src.gembo.renderer.render_mode import RenderMenuBase

# main menu
class RenderMainMenu(RenderMenuBase):
    def __init__(self, engine, surface: Surface, mode: EUpdateMode, render_dict: dict):
        super().__init__(engine, surface, mode, render_dict)
        self.menu = self.value_or_default('menu_data', [])


    def render(self):
        """  """
        self.render_menu_floor_box()
        self.render_title_text('Menu')
        self.render_menu_mode_options_text()


    def render_menu_mode_options_text(self):
        options_enums = self.menu.get_menu_options()
        options_strs = [MenuData.EMenuOptions.to_string(x) for x in options_enums]
        options = zip(options_enums, options_strs)

        y_pos = 90
        for option_enum, option_str in options:
            y_pos += 60
            color = EColor.COOL_GREY
            if option_enum == self.menu.selected_option:
                color = EColor.HIGHLIGHT_YELLOW
            renderable_text = self.title_font.render(option_str, True, color)
            text_width, _ = renderable_text.get_size()
            x_pos = (self.surface_width/2) - 90
            self.render_surface.blit(renderable_text, (x_pos, y_pos))

