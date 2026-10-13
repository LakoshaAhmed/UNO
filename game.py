import random

from cards import Deck, Player


# ============================================================
# UNO GAME (rules / state, no input or output)
# ============================================================
class UnoGame:
    def __init__(self, human_names, number_of_players):
        self.draw_pile = Deck()
        self.discard_pile = []
        self.players = [Player(n, True) for n in human_names]
        for i in range(number_of_players - len(human_names)):
            self.players.append(Player(f"Computer {i + 1}", False))
        self.current_player = 0
        self.direction = 1
        self.current_color = None
        self.awaiting_color = False
        self.winner = None
        self.log = []

        for _ in range(7):
            for p in self.players:
                p.draw_cards(self.draw_pile, 1)
        self.start_discard()

    def say(self, text):
        self.log.append(text)
        self.log = self.log[-6:]

    # ---------------- setup ----------------
    def start_discard(self):
        while True:
            card = self.draw_pile.draw()
            if card.value == "Draw Four":
                self.draw_pile.cards.insert(0, card)
                self.draw_pile.shuffle()
                continue
            self.discard_pile.append(card)
            if card.is_wild():
                self.current_color = random.choice(Deck.COLORS)
            else:
                self.current_color = card.color
            break

    def current_card(self):
        return self.discard_pile[-1]

    # ---------------- rules ----------------
    def can_play(self, card):
        if card.color == "Wild":
            return True
        if card.color == self.current_color:
            return True
        if card.value == self.current_card().value:
            return True
        return False

    def get_playable_cards(self, player):
        return [i for i, c in enumerate(player.hand) if self.can_play(c)]

    def draw_card(self, player):
        card = self.draw_pile.draw()
        if card is None:
            self.reshuffle_discard()
            card = self.draw_pile.draw()
        if card is not None:
            player.hand.append(card)
        return card

    def reshuffle_discard(self):
        if len(self.discard_pile) <= 1:
            return
        self.say("Reshuffling discard pile...")
        top_card = self.discard_pile.pop()
        cards = self.discard_pile
        self.discard_pile = [top_card]
        random.shuffle(cards)
        self.draw_pile.cards.extend(cards)

    def get_next_player_index(self):
        return (self.current_player + self.direction) % len(self.players)

    def play_card(self, player, index):
        """Plays a card. If a human plays a Wild, self.awaiting_color is set
        and the GUI must call set_color() before the turn ends."""
        card = player.hand.pop(index)
        self.discard_pile.append(card)
        self.say(f"{player.name} played {card}.")

        if card.color != "Wild":
            self.current_color = card.color

        if card.value == "Wild":
            self.choose_color(player)

        elif card.value == "Draw Four":
            self.choose_color(player)
            self._make_next_draw(4)

        elif card.value == "Draw Two":
            self._make_next_draw(2)

        elif card.value == "Skip":
            self.say("Next player is skipped.")
            self.current_player = self.get_next_player_index()

        elif card.value == "Reverse":
            self.say("Direction reversed.")
            self.direction *= -1
            if len(self.players) == 2:
                self.current_player = self.get_next_player_index()

    def _make_next_draw(self, amount):
        next_index = self.get_next_player_index()
        victim = self.players[next_index]
        self.say(f"{victim.name} draws {amount} cards.")
        for _ in range(amount):
            self.draw_card(victim)
        self.current_player = next_index  # skip them

    def choose_color(self, player):
        if player.is_human:
            self.awaiting_color = True
        else:
            counts = {c: 0 for c in Deck.COLORS}
            for card in player.hand:
                if card.color in counts:
                    counts[card.color] += 1
            self.current_color = max(counts, key=counts.get)
            self.say(f"{player.name} chose {self.current_color}.")

    def set_color(self, color):
        self.current_color = color
        self.awaiting_color = False
        self.say(f"Color is now {color}.")

    # ---------------- turn flow ----------------
    def computer_turn(self, player):
        playable = self.get_playable_cards(player)
        if not playable:
            card = self.draw_card(player)
            if card is None:
                return
            self.say(f"{player.name} drew a card.")
            if self.can_play(card):
                self.play_card(player, len(player.hand) - 1)
            return

        action_cards = [
            i for i in playable
            if player.hand[i].value in ["Skip", "Reverse", "Draw Two", "Draw Four"]
        ]
        index = random.choice(action_cards if action_cards else playable)
        self.play_card(player, index)

    def end_turn(self):
        """Call after a player's move is completely done."""
        player = self.players[self.current_player]
        if player.has_won():
            self.winner = player
            self.say(f"{player.name} WINS!")
            return
        self.current_player = (self.current_player + self.direction) % len(self.players)
