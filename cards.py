import random


LABELS = {
    "Skip": "SKIP",
    "Reverse": "REV",
    "Draw Two": "+2",
    "Draw Four": "+4",
    "Wild": "WILD",
}


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

    def label(self):
        return LABELS.get(self.value, self.value)


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
        for color in self.COLORS:
            self.cards.append(Card(color, "0"))
            for number in range(1, 10):
                self.cards.append(Card(color, str(number)))
                self.cards.append(Card(color, str(number)))
            for action in ["Skip", "Reverse", "Draw Two"]:
                self.cards.append(Card(color, action))
                self.cards.append(Card(color, action))
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

    def has_won(self):
        return len(self.hand) == 0
