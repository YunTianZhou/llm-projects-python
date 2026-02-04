card_types = ["3", "4", "5", "6", "7", "8", "9", "10",
              "J", "Q", "K", "A", "2", "Black Joker", "Red Joker"]

card_values = {card: value + 1 for value, card in enumerate(card_types)}

full_deck = [card for card in card_types
             for _ in range(1 if card.endswith("Joker") else 4)]
