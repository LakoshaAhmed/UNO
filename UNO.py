import random


# ============================================================
# CARD
# ============================================================

class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def __str__(self):
        return f"{self.color} {self.value}"

    def is_wild(self):
        return self.color == "Wild"


# ============================================================
# DECK
# ============================================================

class Deck:
    COLORS = ["Red", "Green", "Blue", "Yellow"]

    def __init__(self):
        self.cards = []
        self.create_deck()
        self.shuffle()

    def create_deck(self):
        # Colored cards
        for color in self.COLORS:

            # One zero
            self.cards.append(Card(color, "0"))

            # Two of each 1-9
            for number in range(1, 10):
                self.cards.append(Card(color, str(number)))
                self.cards.append(Card(color, str(number)))

            # Two of each action card
            for action in ["Skip", "Reverse", "Draw Two"]:
                self.cards.append(Card(color, action))
                self.cards.append(Card(color, action))

        # Four Wild and four Wild Draw Four
        for _ in range(4):
            self.cards.append(Card("Wild", "Wild"))
            self.cards.append(Card("Wild", "Draw Four"))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            return None

        return self.cards.pop()


# ============================================================
# PLAYER
# ============================================================

class Player:
    def __init__(self, name, is_human=True):
        self.name = name
        self.is_human = is_human
        self.hand = []

    def draw_cards(self, deck, amount):
        for _ in range(amount):
            card = deck.draw()

            if card is not None:
                self.hand.append(card)

    def show_hand(self):
        print(f"\n{self.name}'s cards:")

        for i, card in enumerate(self.hand):
            print(f"  [{i}] {card}")

    def has_won(self):
        return len(self.hand) == 0


# ============================================================
# UNO GAME
# ============================================================

class UnoGame:

    def __init__(self, number_of_players):
        self.number_of_players = number_of_players

        self.draw_pile = Deck()
        self.discard_pile = []

        self.players = []

        self.current_player = 0
        self.direction = 1

        self.current_color = None

        self.create_players()

    # --------------------------------------------------------
    # CREATE PLAYERS
    # --------------------------------------------------------

    def create_players(self):
        name = input("Enter your name: ")

        self.players.append(
            Player(name, True)
        )

        for i in range(1, self.number_of_players):
            self.players.append(
                Player(f"Computer {i}", False)
            )

    # --------------------------------------------------------
    # INITIAL DEAL
    # --------------------------------------------------------

    def deal_cards(self):
        print("\nDealing cards...")

        for _ in range(7):
            for player in self.players:
                player.draw_cards(self.draw_pile, 1)

    # --------------------------------------------------------
    # START GAME
    # --------------------------------------------------------

    def start(self):
        print("\n===================================")
        print("          WELCOME TO UNO")
        print("===================================")

        self.deal_cards()

        self.start_discard()

        print("\nGame starts!")

        while True:
            player = self.players[self.current_player]

            self.show_game_state()

            print(
                f"\nIt's {player.name}'s turn."
            )

            if player.is_human:
                self.human_turn(player)
            else:
                self.computer_turn(player)

            # Check winner
            if player.has_won():
                print("\n===================================")
                print(f"       {player.name} WINS!")
                print("===================================")
                break

            self.next_player()

    # --------------------------------------------------------
    # STARTING DISCARD CARD
    # --------------------------------------------------------

    def start_discard(self):

        while True:
            card = self.draw_pile.draw()

            # Do not start with Wild Draw Four
            if card.value == "Draw Four":
                self.draw_pile.cards.insert(0, card)
                self.draw_pile.shuffle()
                continue

            self.discard_pile.append(card)

            if card.is_wild():
                self.current_color = random.choice(
                    Deck.COLORS
                )
            else:
                self.current_color = card.color

            break

    # --------------------------------------------------------
    # CURRENT CARD
    # --------------------------------------------------------

    def current_card(self):
        return self.discard_pile[-1]

    # --------------------------------------------------------
    # SHOW GAME STATE
    # --------------------------------------------------------

    def show_game_state(self):

        print("\n-----------------------------------")
        print(
            f"Top card: {self.current_card()}"
        )

        print(
            f"Current color: {self.current_color}"
        )

        print(
            f"Direction: "
            f"{'clockwise' if self.direction == 1 else 'counter-clockwise'}"
        )

        print("-----------------------------------")

        for player in self.players:
            print(
                f"{player.name}: "
                f"{len(player.hand)} cards"
            )

    # --------------------------------------------------------
    # CAN PLAY CARD
    # --------------------------------------------------------

    def can_play(self, card):

        top = self.current_card()

        # Wild cards can always be played
        if card.color == "Wild":
            return True

        # Same color
        if card.color == self.current_color:
            return True

        # Same value
        if card.value == top.value:
            return True

        return False

    # --------------------------------------------------------
    # FIND PLAYABLE CARDS
    # --------------------------------------------------------

    def get_playable_cards(self, player):

        playable = []

        for i, card in enumerate(player.hand):
            if self.can_play(card):
                playable.append(i)

        return playable

    # --------------------------------------------------------
    # HUMAN TURN
    # --------------------------------------------------------

    def human_turn(self, player):

        while True:

            player.show_hand()

            playable = self.get_playable_cards(player)

            print("\nPlayable cards:")

            if playable:
                for index in playable:
                    print(
                        f"  [{index}] "
                        f"{player.hand[index]}"
                    )
            else:
                print("  No playable cards.")

            print("\nOptions:")
            print("  P - Play a card")
            print("  D - Draw a card")

            choice = input(
                "\nChoose an option: "
            ).strip().lower()

            # ----------------------------------------------
            # DRAW
            # ----------------------------------------------

            if choice == "d":

                card = self.draw_card(player)

                if card is None:
                    print(
                        "No cards available."
                    )
                    continue

                print(
                    f"You drew: {card}"
                )

                # Automatically play if possible
                if self.can_play(card):

                    answer = input(
                        "Do you want to play it? (y/n): "
                    ).strip().lower()

                    if answer == "y":
                        self.play_card(
                            player,
                            len(player.hand) - 1
                        )

                return

            # ----------------------------------------------
            # PLAY
            # ----------------------------------------------

            if choice == "p":

                if not playable:
                    print(
                        "You don't have a playable card."
                    )
                    continue

                try:
                    index = int(
                        input(
                            "Enter card number: "
                        )
                    )
                except ValueError:
                    print(
                        "Please enter a number."
                    )
                    continue

                if index not in playable:
                    print(
                        "That card cannot be played."
                    )
                    continue

                self.play_card(
                    player,
                    index
                )

                return

            print("Invalid option.")

    # --------------------------------------------------------
    # COMPUTER TURN
    # --------------------------------------------------------

    def computer_turn(self, player):

        print(
            f"\n{player.name} is thinking..."
        )

        playable = self.get_playable_cards(player)

        # ----------------------------------------------
        # NO PLAYABLE CARD
        # ----------------------------------------------

        if not playable:

            card = self.draw_card(player)

            if card is None:
                return

            print(
                f"{player.name} drew a card."
            )

            if self.can_play(card):

                print(
                    f"{player.name} plays "
                    f"{card}."
                )

                self.play_card(
                    player,
                    len(player.hand) - 1
                )

            else:

                print(
                    f"{player.name} cannot play "
                    f"the drawn card."
                )

            return

        # ----------------------------------------------
        # CHOOSE CARD
        # ----------------------------------------------

        # Prefer action cards
        action_cards = [
            i for i in playable
            if player.hand[i].value
            in [
                "Skip",
                "Reverse",
                "Draw Two",
                "Draw Four"
            ]
        ]

        if action_cards:
            index = random.choice(
                action_cards
            )
        else:
            index = random.choice(
                playable
            )

        card = player.hand[index]

        print(
            f"{player.name} plays {card}."
        )

        self.play_card(
            player,
            index
        )

    # --------------------------------------------------------
    # DRAW CARD
    # --------------------------------------------------------

    def draw_card(self, player):

        card = self.draw_pile.draw()

        if card is None:

            self.reshuffle_discard()

            card = self.draw_pile.draw()

        if card is not None:
            player.hand.append(card)

        return card

    # --------------------------------------------------------
    # RESHUFFLE DISCARD PILE
    # --------------------------------------------------------

    def reshuffle_discard(self):

        if len(self.discard_pile) <= 1:
            return

        print(
            "\nReshuffling discard pile..."
        )

        top_card = self.discard_pile.pop()

        cards = self.discard_pile

        self.discard_pile = [
            top_card
        ]

        random.shuffle(cards)

        self.draw_pile.cards.extend(
            cards
        )

    # --------------------------------------------------------
    # PLAY CARD
    # --------------------------------------------------------

    def play_card(self, player, index):

        card = player.hand.pop(index)

        self.discard_pile.append(card)

        print(
            f"\n{player.name} played "
            f"{card}."
        )

        # ----------------------------------------------
        # NORMAL CARD
        # ----------------------------------------------

        if card.color != "Wild":
            self.current_color = card.color

        # ----------------------------------------------
        # WILD
        # ----------------------------------------------

        if card.value == "Wild":

            self.choose_color(player)

        # ----------------------------------------------
        # WILD DRAW FOUR
        # ----------------------------------------------

        elif card.value == "Draw Four":

            self.choose_color(player)

            next_index = self.get_next_player_index()

            next_player = self.players[next_index]

            print(
                f"{next_player.name} draws 4 cards."
            )

            for _ in range(4):
                self.draw_card(next_player)

            # Skip next player
            self.current_player = next_index

        # ----------------------------------------------
        # DRAW TWO
        # ----------------------------------------------

        elif card.value == "Draw Two":

            next_index = self.get_next_player_index()

            next_player = self.players[next_index]

            print(
                f"{next_player.name} draws 2 cards."
            )

            for _ in range(2):
                self.draw_card(next_player)

            # Skip next player
            self.current_player = next_index

        # ----------------------------------------------
        # SKIP
        # ----------------------------------------------

        elif card.value == "Skip":

            print(
                "Next player is skipped."
            )

            next_index = self.get_next_player_index()

            self.current_player = next_index

        # ----------------------------------------------
        # REVERSE
        # ----------------------------------------------

        elif card.value == "Reverse":

            print(
                "Direction reversed."
            )

            self.direction *= -1

            # With 2 players, Reverse acts like Skip
            if len(self.players) == 2:

                next_index = (
                    self.get_next_player_index()
                )

                self.current_player = next_index

    # --------------------------------------------------------
    # CHOOSE COLOR
    # --------------------------------------------------------

    def choose_color(self, player):

        if player.is_human:

            print("\nChoose a color:")

            for i, color in enumerate(
                Deck.COLORS,
                start=1
            ):
                print(
                    f"{i}. {color}"
                )

            while True:

                try:
                    choice = int(
                        input(
                            "Enter color number: "
                        )
                    )

                    if 1 <= choice <= 4:

                        self.current_color = (
                            Deck.COLORS[
                                choice - 1
                            ]
                        )

                        break

                except ValueError:
                    pass

                print(
                    "Invalid color."
                )

        else:

            # Computer chooses the color
            color_counts = {
                color: 0
                for color in Deck.COLORS
            }

            for card in player.hand:

                if card.color in color_counts:
                    color_counts[
                        card.color
                    ] += 1

            self.current_color = max(
                color_counts,
                key=color_counts.get
            )

            print(
                f"{player.name} chose "
                f"{self.current_color}."
            )

    # --------------------------------------------------------
    # NEXT PLAYER INDEX
    # --------------------------------------------------------

    def get_next_player_index(self):

        return (
            self.current_player
            + self.direction
        ) % len(self.players)

    # --------------------------------------------------------
    # MOVE TO NEXT PLAYER
    # --------------------------------------------------------

    def next_player(self):

        self.current_player = (
            self.current_player
            + self.direction
        ) % len(self.players)


# ============================================================
# MAIN
# ============================================================

def main():

    print("===================================")
    print("             UNO")
    print("===================================")

    while True:

        try:
            number = int(
                input(
                    "Number of players (2-4): "
                )
            )

            if 2 <= number <= 4:
                break

        except ValueError:
            pass

        print(
            "Please enter a number "
            "between 2 and 4."
        )

    game = UnoGame(number)
    game.start()


if __name__ == "__main__":
    main()

