import pygame

def draw_checkbox(screen, rect, checked, label_surf, font, colors):
    WHITE, BLACK = colors["WHITE"], colors["BLACK"]
    pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    if checked:
        pygame.draw.line(screen, BLACK, rect.topleft, rect.bottomright, 2)
        pygame.draw.line(screen, BLACK, rect.topright, rect.bottomleft, 2)
    screen.blit(label_surf, (rect.right + 10, rect.top - 4))


class MethodPopup:
    def __init__(self, screen, font, title, options, colors):
        self.screen = screen
        self.font = font
        self.title = title
        self.options = options
        self.colors = colors

        self.visible = False
        self.selected = 0
        self.show_plot = False
        self.show_gui = False
        self.on_ok = None  # callback (example_str, show_plot: bool)

        width, height = screen.get_size()
        w, h = 500, 300
        self.rect = pygame.Rect((width - w)//2, (height - h)//2, w, h)

        # rects para opciones
        self.option_rects = []
        top = self.rect.top + 70
        for i in range(len(self.options)):
            r = pygame.Rect(self.rect.left + 25, top + i*40, self.rect.width - 50, 30)
            self.option_rects.append(r)

        # checkbox y botón OK
        self.chk_rect = pygame.Rect(self.rect.left + 25, self.rect.bottom - 100, 40, 40)
        self.gui_chk_rect = pygame.Rect(self.rect.left + 25, self.rect.bottom - 70, 40, 40)
        self.ok_rect = pygame.Rect(0, 0, 120, 40)
        self.ok_rect.centerx = self.rect.centerx
        self.ok_rect.bottom = self.rect.bottom - 20

        self._label_show = self.font.render("Mostrar plt.show()", True, colors["BLACK"])

    def open(self, on_ok):
        self.on_ok = on_ok
        self.show_plot = False
        self.show_gui = False
        self.visible = True

    def close(self):
        self.visible = False
        self.on_ok = None

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Si el clic es FUERA del popup, cerrarlo y devolver False
            if not self.rect.collidepoint(event.pos):
                self.close()
                return False

            # OK dentro del popup -> consumir evento
            if self.ok_rect.collidepoint(event.pos):
                if self.on_ok is not None:
                    example = self.options[self.selected]
                    self.on_ok(example, self.show_plot, True)
                self.close()
                return True

            # checkbox dentro -> consumir
            if self.chk_rect.collidepoint(event.pos):
                self.show_plot = not self.show_plot
                return True

            # selección de opción -> consumir
            for i, r in enumerate(self.option_rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    return True

            # clic dentro del popup pero en vacío -> consumir
            return True

        return False

    def draw(self):
        if not self.visible:
            return

        screen = self.screen
        GREY = self.colors["GREY"]
        BLACK = self.colors["BLACK"]
        BLUE = self.colors["BLUE"]
        YELLOW = self.colors["YELLOW"]
        WHITE = self.colors["WHITE"]

        # fondo popup
        pygame.draw.rect(screen, GREY, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)

        # título
        title_surf = self.font.render(self.title, True, BLACK)
        screen.blit(title_surf, (self.rect.left + 20, self.rect.top + 20))

        # opciones
        for i, r in enumerate(self.option_rects):
            pygame.draw.rect(screen, (230, 230, 230), r, border_radius=5)
            pygame.draw.rect(screen, BLACK, r, 1, border_radius=5)
            if i == self.selected:
                pygame.draw.rect(screen, BLUE, r, 3, border_radius=5)
            txt = self.font.render(self.options[i], True, BLACK)
            screen.blit(txt, txt.get_rect(midleft=(r.left + 10, r.centery)))

        # checkbox plt.show
        draw_checkbox(screen, self.chk_rect, self.show_plot,
                  self._label_show, self.font,
                  {"WHITE": WHITE, "BLACK": BLACK})


        # botón OK
        pygame.draw.rect(screen, YELLOW, self.ok_rect, border_radius=6)
        pygame.draw.rect(screen, BLACK, self.ok_rect, 2, border_radius=6)
        ok_txt = self.font.render("OK", True, BLACK)
        screen.blit(ok_txt, ok_txt.get_rect(center=self.ok_rect.center))