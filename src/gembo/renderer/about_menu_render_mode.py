
from src.gembo.renderer.render_mode import MenuRenderModeBase, EGameMode, EColor, Surface


# about
class AboutMenuRenderMode(MenuRenderModeBase):
    def __init__(self, engine, surface: Surface, mode: EGameMode, render_dict: dict):
        super().__init__(engine, surface, mode, render_dict)
        self.about_menu_font = self.value_or_default('about_menu_font')
        self.homily_font = self.value_or_default('homily_font')

    def render(self):
        self.render_menu_floor_box()
        self.render_ellie_loves_games()
        self.render_homily()

    def render_ellie_loves_games(self):
        ellie = 'ellie'
        loves = 'love\'s'
        games = 'games'

        ellie_renderable_text = self.about_menu_font.render(ellie, True, EColor.WHITE)
        loves_renderable_text = self.about_menu_font.render(loves, True, EColor.PINK)
        games_renderable_text = self.about_menu_font.render(games, True, EColor.LIGHT_BLUE)

        renderable_texts = [ellie_renderable_text, loves_renderable_text, games_renderable_text]

        y_pos = 90
        for renderable_text in renderable_texts:
            text_width, _ = renderable_text.get_size()
            x_pos = (self.surface_width / 2) - (text_width / 2)
            y_pos += 40
            self.render_surface.blit(renderable_text, (x_pos, y_pos))


    def render_homily(self):
        text1 = 'This one\'s for you Greg'
        # text1 = 'For my friend Greg'
        # text2 = 'who wanted to make small games.'

        renderable_text1 = self.homily_font.render(text1, True, EColor.COOL_GREY)
        # renderable_text2 = self.homily_font.render(text2, True, EColor.COOL_GREY)

        renderable_texts = [
            renderable_text1,
            #    renderable_text2
        ]

        y_pos = self.surface_height - 240
        for renderable_text in renderable_texts:
            text_width, _ = renderable_text.get_size()
            x_pos = (self.surface_width / 2) - (text_width / 2)
            y_pos += 30
            self.render_surface.blit(renderable_text, (x_pos, y_pos))


