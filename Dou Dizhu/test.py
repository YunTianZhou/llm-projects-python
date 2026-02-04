from collections import Counter
from collections import defaultdict
from constant import *

seq_require = [0, 4, 2, 1, 1]


class Combination:
    def __init__(self, cards, length=0):
        self.cards = cards
        self.length = length

    def combine(self, other):
        for card in other:
            self.cards[card] += other[card]
        return self

    def get_all_sequences(self, count):
        seqs = []
        for i in range(len(card_types)):
            j = i
            curr = defaultdict(int)
            while j >= 0 and self.cards[card_types[j]] >= count:
                curr[card_types[j]] += count
                if i == j or (i - j) >= seq_require[count]:
                    seqs.append(Combination(curr.copy(), length=i - j + 1))
                if count == 4 or card_types[j] in ("2", "Black Joker", "Red Joker"):
                    break
                j -= 1
        return seqs

    def take_off(self, other):
        copy = self.cards.copy()
        for card in other.cards:
            copy[card] -= other.cards[card]
        return Combination(copy)

    def get_single_combs(self, k, limit=4):
        def dfs(i, remaining, current):
            if remaining == 0:
                yield current
                return
            if i == len(card_types):
                return

            card = card_types[i]
            max_available = self.cards[card]

            for count in range(0, min(max_available, remaining) + 1):
                if count > limit:
                    break
                current[card] = count
                yield from dfs(i + 1, remaining - count, current)
                current[card] = 0

        yield from dfs(0, k, {})

    def get_pair_combs(self, k, limit=4):
        def dfs(i, remaining, current):
            if remaining == 0:
                yield current
                return
            if i == len(card_types):
                return

            card = card_types[i]

            for count in (0, 2, 4):
                if count > limit or count > self.cards[card] or remaining < count // 2:
                    break
                current[card] = count
                yield from dfs(i + 1, remaining - count // 2, current)
                current[card] = 0

        yield from dfs(0, k, {})

    def get_valid_combs(self, top):
        if not top:
            res = []

            # Rocket
            if "Red Joker" in self.cards and "Black Joker" in self.cards:
                res.append(Combination({"Red Joker": 1, "Black Joker": 1}))

            # Single, Pair, Triplet, and Bomb
            combs = [self.get_all_sequences(i) for i in range(1, 5)]
            for i, comb in enumerate(combs[:-1]):
                for seq in comb:
                    res.append(seq)

            # Triplets and Single, Pair
            for triplet in combs[2]:
                new = self.take_off(triplet)
                for comb in new.get_single_combs(triplet.length):
                    res.append(Combination(triplet.cards.copy()).combine(comb))
                for comb in new.get_pair_combs(triplet.length):
                    res.append(Combination(triplet.cards.copy()).combine(comb))

            # Quadruple and Single, Pair
            for quadruple in combs[3]:
                new = self.take_off(quadruple)
                for comb in new.get_single_combs(2, limit=3):
                    res.append(Combination(quadruple.cards.copy()).combine(comb))
                for comb in new.get_pair_combs(2, limit=3):
                    res.append(Combination(quadruple.cards.copy()).combine(comb))

            return res

        res = [["pass"]]

    def __hash__(self):
        return hash(tuple(self.cards.get(card, 0) for card in card_types))

    def __eq__(self, other):
        return all(self.cards.get(card, 0) == other.cards.get(card, 0) for card in card_types)


# i = 0
# a = Combination(Counter(full_deck)).get_valid_combs([])
# print(len(a))
# print(len(set(a)))
# for comb in a[-5000:]:
#     for card in card_types:
#         if comb.cards.get(card, 0) > 0:
#             print(card * comb.cards[card], end=" ")
#     print()
#     i += 1

s = set()
i = 0
for comb in Combination(Counter(full_deck)).get_valid_combs([]):
    if comb in s and i < 100:
        for card in card_types:
            if comb.cards.get(card, 0) > 0:
                print(card * comb.cards[card], end=" ")
        print()
        i += 1
    s.add(comb)
