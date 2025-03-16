
from src.gembo.renderer.render_mode import RenderMenuBase, EUpdateMode, EColor, Surface


# stats
class RenderStatsMenu(RenderMenuBase):
    def __init__(self, engine, surface: Surface, mode: EUpdateMode, render_dict: dict):
        super().__init__(engine, surface, mode, render_dict)

        self.score_font = self.value_or_default('score_font')
        self._statistics = self.value_or_default('statistics')


    def render(self):
        self.render_menu_floor_box()
        self.render_title_text('Stats')
        self.render_stats_menu_stats()

    def render_stats_menu_stats(self):
        assert self._statistics.streak_counts
        streaks = list(
            reversed(
                sorted(
                    [(x, y) for x, y in self._statistics.streak_counts.items()]
                )
            )
        )

        streaks_to_display = streaks[:self._statistics.display_n_top_streaks]

        y_pos = 90

        text = f'Streak        Count'
        renderable_text = self.score_font.render(text, True, EColor.COOL_GREY)
        text_width, _ = renderable_text.get_size()
        x_pos = (self.surface_width / 2) - (text_width / 2)
        self.render_surface.blit(renderable_text, (x_pos, y_pos))

        y_pos += 30
        for streak, count in streaks_to_display:
            y_pos += 30

            streak_text = f'{streak}'
            streak_renderable_text = self.score_font.render(streak_text, True, EColor.COOL_GREY)
            streak_text_width, _ = renderable_text.get_size()
            x_pos = (self.surface_width / 2) - (streak_text_width / 2) + 30
            self.render_surface.blit(streak_renderable_text, (x_pos, y_pos))

            count_text = f'{count}'
            count_renderable_text = self.score_font.render(count_text, True, EColor.COOL_GREY)
            count_text_width, _ = renderable_text.get_size()
            x_pos = (self.surface_width / 1) - (count_text_width / 2)
            self.render_surface.blit(count_renderable_text, (x_pos, y_pos))
