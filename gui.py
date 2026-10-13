import sys
import pygame

from game import UnoGame


# ============================================================
# CONSTANTS
# ============================================================
W, H = 1100, 720
CARD_W, CARD_H = 84, 126
FPS = 60

COLOR_RGB = {
    "Red": (206, 45, 45),
    "Green": (46, 160, 74),
    "Blue": (40, 96, 205),
    "Yellow": (236, 192, 30),
}
BG = (22, 92, 62)
BG_DARK = (14, 60, 41)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GOLD = (255, 215, 0)


# ============================================================
# RENDERING HELPERS
# ============================================================
_font_cache = {}


def font(size, bold=True):
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont("arial,helvetica,dejavusans", size, bold=bold)
    return _font_cache[key]


def draw_text(surf, text, size, color, center=None, topleft=None, bold=True):
    img = font(size, bold).render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = center
    elif topleft:
        rect.topleft = topleft
    surf.blit(img, rect)
    return rect


def draw_card(surf, card, rect, face_up=True, dim=False):
    pygame.draw.rect(surf, WHITE, rect, border_radius=10)
    inner = rect.inflate(-8, -8)

    if not face_up:
        pygame.draw.rect(surf, (25, 25, 25), inner, border_radius=8)
        oval = pygame.Rect(0, 0, inner.w * 0.8, inner.h * 0.5)
        oval.center = inner.center
        pygame.draw.ellipse(surf, (206, 45, 45), oval)
        draw_text(surf, "UNO", max(12, rect.w // 4), GOLD, center=inner.center)
        return

    if card.is_wild():
        pygame.draw.rect(surf, BLACK, inner, border_radius=8)
        half_w, half_h = inner.w // 2, inner.h // 2
        quads = list(COLOR_RGB.values())
        centre = pygame.Rect(0, 0, inner.w * 0.78, inner.h * 0.58)
        centre.center = inner.center
        qs = [
            (centre.left, centre.top), (centre.centerx, centre.top),
            (centre.left, centre.centery), (centre.centerx, centre.centery),
        ]
        for (qx, qy), col in zip(qs, quads):
            pygame.draw.rect(surf, col, (qx, qy, centre.w // 2, centre.h // 2))
        text_col = WHITE
        main = card.label()
        draw_text(surf, main, max(14, rect.w // 3 + (6 if len(main) <= 2 else -4)),
                  text_col, center=inner.center)
        draw_text(surf, "+4" if card.value == "Draw Four" else "W", 14, WHITE,
                  topleft=(inner.left + 5, inner.top + 3))
    else:
        base = COLOR_RGB[card.color]
        pygame.draw.rect(surf, base, inner, border_radius=8)
        oval = pygame.Rect(0, 0, inner.w * 0.82, inner.h * 0.58)
        oval.center = inner.center
        pygame.draw.ellipse(surf, WHITE, oval)
        label = card.label()
        size = max(14, rect.w // 2 + 4) if len(label) <= 2 else max(12, rect.w // 4 + 2)
        draw_text(surf, label, size, base, center=inner.center)
        draw_text(surf, label, 13, WHITE, topleft=(inner.left + 5, inner.top + 3))

    if dim:
        shade = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shade, (0, 0, 0, 120), shade.get_rect(), border_radius=10)
        surf.blit(shade, rect.topleft)


# ============================================================
# APP (screens, input, game loop)
# ============================================================
class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("UNO")
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()

        self.state = "menu_players"
        self.total_players = 2
        self.human_count = 1
        self.names = []
        self.name_input = ""
        self.game = None
        self.buttons = []        # (rect, key)
        self.hand_rects = []
        self.draw_pile_rect = pygame.Rect(0, 0, 0, 0)
        self.action_time = 0
        self.flash_msg = ""
        self.flash_until = 0

    # ---------------- helpers ----------------
    def now(self):
        return pygame.time.get_ticks()

    def flash(self, text, ms=1500):
        self.flash_msg = text
        self.flash_until = self.now() + ms

    def add_button(self, rect, text, key, color=(240, 240, 240), text_color=BLACK, enabled=True):
        mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse) and enabled
        col = color
        if hover:
            col = tuple(min(255, c + 25) for c in color)
        if not enabled:
            col = (120, 120, 120)
        pygame.draw.rect(self.screen, col, rect, border_radius=12)
        pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=12)
        draw_text(self.screen, text, 26, text_color, center=rect.center)
        if enabled:
            self.buttons.append((rect, key))

    def human_count_in_game(self):
        return sum(1 for p in self.game.players if p.is_human)

    def viewer(self):
        """Which human's hand is shown at the bottom."""
        g = self.game
        cur = g.players[g.current_player]
        if cur.is_human:
            return cur
        for p in g.players:
            if p.is_human:
                return p
        return g.players[0]

    def hand_visible(self):
        g = self.game
        if self.state == "pass":
            return False
        if self.human_count_in_game() == 1:
            return True
        return g.players[g.current_player].is_human

    # ---------------- game flow ----------------
    def start_game(self):
        self.game = UnoGame(self.names, self.total_players)
        self.game.say("Game starts!")
        self.after_turn(first=True)

    def after_turn(self, first=False):
        g = self.game
        if g.winner:
            self.state = "game_over"
            return
        p = g.players[g.current_player]
        if p.is_human and self.human_count_in_game() > 1:
            self.state = "pass"
        else:
            self.state = "playing"
        self.action_time = self.now() + (500 if first else 1100)

    def finish_turn(self):
        self.game.end_turn()
        self.after_turn()

    def after_play(self):
        if self.game.awaiting_color:
            self.state = "choose_color"
        else:
            self.finish_turn()

    def human_play_index(self, index):
        g = self.game
        player = g.players[g.current_player]
        g.play_card(player, index)
        self.after_play()

    def human_draw(self):
        g = self.game
        player = g.players[g.current_player]
        card = g.draw_card(player)
        if card is None:
            g.say("No cards available.")
            self.finish_turn()
            return
        g.say(f"You drew: {card}")
        if g.can_play(card):
            self.state = "draw_decision"
        else:
            self.finish_turn()

    def update(self):
        if self.state == "playing" and self.game:
            g = self.game
            player = g.players[g.current_player]
            if not player.is_human and self.now() >= self.action_time:
                g.computer_turn(player)
                self.finish_turn()

    # ---------------- events ----------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if self.state == "menu_names" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.confirm_name()
            elif event.key == pygame.K_BACKSPACE:
                self.name_input = self.name_input[:-1]
            elif event.unicode and event.unicode.isprintable() and len(self.name_input) < 14:
                self.name_input += event.unicode
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for rect, key in self.buttons:
                if rect.collidepoint(pos):
                    self.handle_button(key)
                    return

            if self.state == "playing" and self.game:
                g = self.game
                player = g.players[g.current_player]
                if not player.is_human:
                    return
                if self.draw_pile_rect.collidepoint(pos):
                    self.human_draw()
                    return
                playable = g.get_playable_cards(player)
                for i in reversed(range(len(self.hand_rects))):
                    if self.hand_rects[i].collidepoint(pos):
                        if i in playable:
                            self.human_play_index(i)
                        else:
                            self.flash("That card cannot be played.")
                        return

    def confirm_name(self):
        name = self.name_input.strip() or f"Player {len(self.names) + 1}"
        self.names.append(name)
        self.name_input = ""
        if len(self.names) >= self.human_count:
            self.start_game()

    def handle_button(self, key):
        if key.startswith("total:"):
            self.total_players = int(key.split(":")[1])
            self.state = "menu_humans"
        elif key.startswith("humans:"):
            self.human_count = int(key.split(":")[1])
            self.names = []
            self.name_input = ""
            self.state = "menu_names"
        elif key == "back":
            self.state = "menu_players"
        elif key == "pass_ready":
            self.state = "playing"
        elif key.startswith("color:"):
            self.game.set_color(key.split(":")[1])
            self.finish_turn()
        elif key == "play_drawn":
            g = self.game
            self.human_play_index(len(g.players[g.current_player].hand) - 1)
        elif key == "keep_drawn":
            self.finish_turn()
        elif key == "again":
            self.state = "menu_players"
            self.game = None
        elif key == "quit":
            pygame.quit()
            sys.exit()

    # ---------------- drawing ----------------
    def draw(self):
        self.buttons = []
        self.hand_rects = []
        self.screen.fill(BG)

        if self.state == "menu_players":
            self.draw_menu("UNO", "Total number of players", [(f"{n}", f"total:{n}") for n in (2, 3, 4)])
        elif self.state == "menu_humans":
            opts = [(f"{n}", f"humans:{n}") for n in range(1, self.total_players + 1)]
            self.draw_menu("UNO", "How many human players?", opts, back=True)
        elif self.state == "menu_names":
            self.draw_name_entry()
        else:
            self.draw_table()
            if self.state == "pass":
                self.draw_pass_screen()
            elif self.state == "choose_color":
                self.draw_color_picker()
            elif self.state == "draw_decision":
                self.draw_draw_decision()
            elif self.state == "game_over":
                self.draw_game_over()

        pygame.display.flip()

    def draw_menu(self, title, subtitle, options, back=False):
        draw_text(self.screen, title, 110, GOLD, center=(W // 2, 170))
        draw_text(self.screen, subtitle, 38, WHITE, center=(W // 2, 300))
        n = len(options)
        bw, gap = 120, 30
        total = n * bw + (n - 1) * gap
        x = (W - total) // 2
        for label, key in options:
            self.add_button(pygame.Rect(x, 360, bw, 90), label, key)
            x += bw + gap
        if back:
            self.add_button(pygame.Rect(W // 2 - 70, 500, 140, 50), "Back", "back")

    def draw_name_entry(self):
        idx = len(self.names) + 1
        draw_text(self.screen, "UNO", 110, GOLD, center=(W // 2, 170))
        draw_text(self.screen, f"Enter the name of human player {idx}", 38, WHITE, center=(W // 2, 300))
        box = pygame.Rect(W // 2 - 220, 350, 440, 70)
        pygame.draw.rect(self.screen, WHITE, box, border_radius=12)
        cursor = "|" if (self.now() // 500) % 2 == 0 else ""
        draw_text(self.screen, self.name_input + cursor, 36, BLACK, center=box.center)
        draw_text(self.screen, "Press Enter to confirm (leave blank for a default name)",
                  22, (210, 230, 220), center=(W // 2, 460), bold=False)

    def draw_table(self):
        g = self.game
        viewer = self.viewer()
        cur = g.players[g.current_player]

        # Opponents along the top
        others = [p for p in g.players if p is not viewer]
        n = max(1, len(others))
        slot_w = W // n
        for i, p in enumerate(others):
            cx = slot_w * i + slot_w // 2
            self.draw_opponent(p, cx, 20, p is cur)

        # Center: draw pile + discard pile
        cy = 330
        self.draw_pile_rect = pygame.Rect(W // 2 - 130 - CARD_W // 2, cy - CARD_H // 2, CARD_W, CARD_H)
        for off in (4, 2, 0):
            r = self.draw_pile_rect.move(-off, -off)
            draw_card(self.screen, None, r, face_up=False)
        draw_text(self.screen, "DRAW", 18, WHITE, center=(self.draw_pile_rect.centerx, self.draw_pile_rect.bottom + 18))

        top_rect = pygame.Rect(W // 2 + 50 - CARD_W // 2, cy - CARD_H // 2, CARD_W, CARD_H)
        draw_card(self.screen, g.current_card(), top_rect)

        # Current color indicator
        col = COLOR_RGB.get(g.current_color, WHITE)
        pygame.draw.circle(self.screen, col, (W // 2 + 170, cy), 28)
        pygame.draw.circle(self.screen, WHITE, (W // 2 + 170, cy), 28, 3)
        draw_text(self.screen, g.current_color, 18, WHITE, center=(W // 2 + 170, cy + 46))

        arrow = "Clockwise  >>" if g.direction == 1 else "<<  Counter-clockwise"
        draw_text(self.screen, arrow, 22, (210, 230, 220), center=(W // 2, cy + 105), bold=False)

        # Message log
        for i, msg in enumerate(g.log[-5:]):
            draw_text(self.screen, msg, 20, (225, 240, 232), topleft=(20, 190 + i * 26), bold=False)

        # Turn banner
        if self.state != "game_over":
            draw_text(self.screen, f"It's {cur.name}'s turn.", 30, GOLD, center=(W // 2, 215))

        # Player hand
        if self.hand_visible():
            self.draw_hand(viewer, cur)
        else:
            draw_text(self.screen, f"{viewer.name}'s cards: {len(viewer.hand)}", 26, WHITE,
                      center=(W // 2, H - 80))

        if self.now() < self.flash_until:
            draw_text(self.screen, self.flash_msg, 28, (255, 200, 200), center=(W // 2, H - 190))

    def draw_opponent(self, p, cx, top, is_current):
        panel = pygame.Rect(cx - 150, top, 300, 150)
        if is_current:
            pygame.draw.rect(self.screen, GOLD, panel.inflate(8, 8), border_radius=14)
        pygame.draw.rect(self.screen, BG_DARK, panel, border_radius=12)
        draw_text(self.screen, f"{p.name}  ({len(p.hand)})", 24, WHITE, center=(cx, top + 20))
        shown = min(len(p.hand), 8)
        small_w, small_h = 36, 54
        step = 24
        total = small_w + step * (shown - 1) if shown else 0
        x0 = cx - total // 2
        for i in range(shown):
            r = pygame.Rect(x0 + i * step, top + 50, small_w, small_h)
            draw_card(self.screen, None, r, face_up=False)
        if len(p.hand) > 8:
            draw_text(self.screen, f"+{len(p.hand) - 8}", 20, GOLD, center=(cx + 130, top + 80))
        if len(p.hand) == 1:
            draw_text(self.screen, "UNO!", 22, GOLD, center=(cx, top + 130))

    def draw_hand(self, viewer, cur):
        g = self.game
        hand = viewer.hand
        n = len(hand)
        if n == 0:
            return
        avail = W - 120
        step = min(CARD_W + 10, (avail - CARD_W) / (n - 1)) if n > 1 else 0
        total = CARD_W + step * (n - 1)
        x0 = (W - total) / 2
        y = H - CARD_H - 28
        my_turn = (viewer is cur) and self.state == "playing"
        playable = set(g.get_playable_cards(viewer)) if my_turn else set()

        mouse = pygame.mouse.get_pos()
        rects = [pygame.Rect(int(x0 + i * step), y, CARD_W, CARD_H) for i in range(n)]
        hover_idx = None
        if my_turn:
            for i in reversed(range(n)):
                if rects[i].collidepoint(mouse):
                    hover_idx = i
                    break

        for i, r in enumerate(rects):
            lift = 0
            if my_turn and i in playable:
                lift = -14
            if i == hover_idx and i in playable:
                lift = -28
            rr = r.move(0, lift)
            rects[i] = rr
            draw_card(self.screen, hand[i], rr, dim=(my_turn and i not in playable))
        self.hand_rects = rects

        draw_text(self.screen, f"{viewer.name}'s cards", 22, WHITE, topleft=(20, H - 32), bold=False)
        if my_turn:
            draw_text(self.screen, "Click a card to play it, or click the draw pile",
                      20, (210, 230, 220), center=(W // 2, H - 14), bold=False)

    def dim_background(self):
        shade = pygame.Surface((W, H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 170))
        self.screen.blit(shade, (0, 0))

    def draw_pass_screen(self):
        g = self.game
        self.screen.fill((0, 0, 0))
        p = g.players[g.current_player]
        draw_text(self.screen, f"Pass the device to {p.name}", 54, WHITE, center=(W // 2, 300))
        self.add_button(pygame.Rect(W // 2 - 110, 400, 220, 70), "I'm ready", "pass_ready", color=GOLD)

    def draw_color_picker(self):
        self.dim_background()
        draw_text(self.screen, "Choose a color", 48, WHITE, center=(W // 2, 250))
        x = W // 2 - (4 * 130 + 3 * 20) // 2
        for name, rgb in COLOR_RGB.items():
            self.add_button(pygame.Rect(x, 310, 130, 100), name, f"color:{name}", color=rgb,
                            text_color=WHITE if name != "Yellow" else BLACK)
            x += 150

    def draw_draw_decision(self):
        g = self.game
        player = g.players[g.current_player]
        card = player.hand[-1]
        self.dim_background()
        draw_text(self.screen, f"You drew: {card}", 44, WHITE, center=(W // 2, 220))
        draw_card(self.screen, card, pygame.Rect(W // 2 - CARD_W // 2, 260, CARD_W, CARD_H))
        draw_text(self.screen, "Do you want to play it?", 30, WHITE, center=(W // 2, 430))
        self.add_button(pygame.Rect(W // 2 - 170, 470, 150, 60), "Play", "play_drawn", color=GOLD)
        self.add_button(pygame.Rect(W // 2 + 20, 470, 150, 60), "Keep", "keep_drawn")

    def draw_game_over(self):
        self.dim_background()
        draw_text(self.screen, f"{self.game.winner.name} WINS!", 80, GOLD, center=(W // 2, 280))
        self.add_button(pygame.Rect(W // 2 - 190, 400, 170, 70), "Play again", "again", color=GOLD)
        self.add_button(pygame.Rect(W // 2 + 20, 400, 170, 70), "Quit", "quit")

    # ---------------- main loop ----------------
    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.draw()
            self.clock.tick(FPS)
