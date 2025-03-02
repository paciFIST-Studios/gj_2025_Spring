
from src.gembo.renderer.render_mode import MenuRenderModeBase, EGameMode, EColor, Surface

# demo
class DemoRenderMode(MenuRenderModeBase):
    def __init__(self, engine, surface: Surface, mode: EGameMode, render_dict: dict):
        super().__init__(engine, surface, mode, render_dict)
        self.demo_title_font = self.value_or_default('demo_title_font')
        self.window_title = self.value_or_default('window_title')

    def render(self):
        self.render_menu_floor_box()
        self.render_demo_title()

    def render_demo_title(self):
        demo_mode_title_string = self.window_title
        demo_mode_title_renderable_text = self.demo_title_font.render(demo_mode_title_string, True,
                                                                    EColor.HIGHLIGHT_YELLOW)

        # calculate centered on screen position
        text_width, _ = demo_mode_title_renderable_text.get_size()

        pos_y = 120
        pos_x = (self.surface_width / 2) - (text_width / 2)

        # blit
        self.render_surface.blit(demo_mode_title_renderable_text, (pos_x, pos_y))

