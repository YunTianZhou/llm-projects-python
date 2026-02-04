from collections import Counter
from collections import defaultdict
from constant import *


class CombinationType:
    Unknown = -1
    Empty = 0
    SingleSeq = 1
    PairSeq = 2
    ThreeSeq = 3
    ThreePlusSingle = 4
    ThreePlusPair = 5
    FourPlusSingle = 6
    FourPlusPair = 7
    Bomb = 8


class Combination:
    def __init__(self, cards):
        self.cards = cards
        self.types = [card for card in card_types if self.cards.get(card, 0) > 0]
        self.count = sum(self.cards[card] for card in self.types)
        if self.types:
            self.max_count = max(self.cards[card] for card in self.types)
            self.max_value = max(card_values[card] for card in self.types
                                 if self.cards[card] == self.max_count)
        else:
            self.max_count = self.max_value = 0
        self.type = self._check()
        self._edge_case_check()

    def to_list(self):
        return [card for card in self.types for _ in range(self.cards[card])]

    def _longest_continuous_seq(self, count):
        curr_length = curr_value = 0
        max_length = max_value = 0
        for i, card in enumerate(self.types):
            if (self.cards.get(card, 0) >= count and
                    (curr_length == 0 or
                     (card != "2" and card_values[card] - card_values[self.types[i - 1]] == 1))):
                curr_length += 1
                curr_value = card_values[card]
            else:
                if curr_length > max_length:
                    max_length = curr_length
                    max_value = curr_value
                curr_length = curr_value = 0
        return max((max_length, max_value), (curr_length, curr_value))

    def _check_4(self):
        if self.count == 4:
            return CombinationType.Bomb
        elif self.count == 6:
            return CombinationType.FourPlusSingle
        elif self.count == 8:
            if any(self.cards[card] not in (2, 4) for card in self.types):
                return CombinationType.Unknown
            return CombinationType.FourPlusPair
        return CombinationType.Unknown

    def _check_3(self):
        seq_length, seq_value = self._longest_continuous_seq(3)
        if self.count == seq_length * 3:
            return CombinationType.ThreeSeq
        elif self.count == seq_length * 4:
            self.max_value = seq_value
            return CombinationType.ThreePlusSingle
        elif self.count == seq_length * 5:
            if any(self.cards[card] not in (2, 3, 4) for card in self.types):
                return CombinationType.Unknown
            self.max_value = seq_value
            return CombinationType.ThreePlusPair
        return CombinationType.Unknown

    def _check_2(self):
        if self.count == 2:
            return CombinationType.PairSeq
        if self.count >= 6 and self.count % 2 == 0:
            seq_length, _ = self._longest_continuous_seq(2)
            if self.count == seq_length * 2:
                return CombinationType.PairSeq
            return CombinationType.Unknown
        return CombinationType.Unknown

    def _check_1(self):
        if self.count == 1:
            return CombinationType.SingleSeq
        elif self.count == 2 and self.types == ["Black Joker", "Red Joker"]:
            return CombinationType.Bomb
        elif self.count >= 5:
            seq_length, _ = self._longest_continuous_seq(1)
            if self.count == seq_length:
                return CombinationType.SingleSeq
            return CombinationType.Unknown
        return CombinationType.Unknown

    def _check(self):
        match self.max_count:
            case 4:
                return self._check_4()
            case 3:
                return self._check_3()
            case 2:
                return self._check_2()
            case 1:
                return self._check_1()
            case 0:
                return CombinationType.Empty
            case _:
                raise ValueError("Invalid top count")

    def _edge_case_check(self):
        # AAAA-BBBB Airplane
        if self.count == 8 and self.max_count == 4:
            seq_length, _seq_value = self._longest_continuous_seq(4)
            if seq_length == 2:
                self.type = CombinationType.ThreePlusSingle
        # Undetermined Airplanes (with four(s))
        elif self.type == CombinationType.Unknown and self.max_count == 4:
            self.type = self._check_3()


class CombinationGenerator:
    _seq_require = [0, 4, 2, 1, 1]

    def __init__(self, cards, top):
        self.cards = defaultdict(int)
        for card in cards:
            self.cards[card] += 1
        self.top = Combination(Counter(top))

    @staticmethod
    def _get_all_sequences(cards, count):
        _Self = CombinationGenerator

        for i in range(len(card_types)):
            j = i
            curr = defaultdict(int)
            while j >= 0 and cards[card_types[j]] >= count:
                curr[card_types[j]] += count
                if i == j or (i - j) >= _Self._seq_require[count]:
                    yield curr.copy()
                if count == 4 or card_types[j] in ("2", "Black Joker", "Red Joker"):
                    break
                j -= 1

    @staticmethod
    def _take_off(seq1, seq2):
        new_seq = seq1.copy()
        for card in seq2:
            new_seq[card] -= seq2[card]
        return new_seq

    @staticmethod
    def _combine(seq1, seq2):
        new_seq = seq1.copy()
        for card in seq2:
            new_seq[card] += seq2[card]
        return new_seq

    @staticmethod
    def _get_single_combs(cards, k):
        def dfs(i, remaining, current):
            if remaining == 0:
                yield current
                return
            if i == len(card_types):
                return

            card = card_types[i]

            for count in range(0, min(cards[card], remaining) + 1):
                current[card] = count
                yield from dfs(i + 1, remaining - count, current)
                current[card] = 0

        yield from dfs(0, k, {})

    @staticmethod
    def _get_pair_combs(cards, k):
        def dfs(i, remaining, current):
            if remaining == 0:
                yield current
                return
            if i == len(card_types):
                return

            card = card_types[i]

            for count in (0, 2, 4):
                if count > cards[card] or remaining < count // 2:
                    break
                current[card] = count
                yield from dfs(i + 1, remaining - count // 2, current)
                current[card] = 0

        yield from dfs(0, k, {})

    def _generate_bombs(self):
        _Self = CombinationGenerator

        # Bomb
        yield from (
            comb.to_list()
            for comb in map(Combination, _Self._get_all_sequences(self.cards, 4))
            if self.top.type != CombinationType.Bomb or self.top.max_value < comb.max_value
        )

        # Rocket
        if self.cards["Red Joker"] and self.cards["Black Joker"]:
            yield ["Black Joker", "Red Joker"]

    def _generate_seqs(self):
        _Self = CombinationGenerator

        for i, comb_type in enumerate((CombinationType.SingleSeq, CombinationType.PairSeq)):
            if self.top.type == CombinationType.Empty:
                yield from map(lambda x: Combination(x).to_list(),
                               _Self._get_all_sequences(self.cards, i + 1))
            elif self.top.type == comb_type:
                yield from (comb.to_list()
                            for comb in map(Combination, _Self._get_all_sequences(self.cards, i + 1))
                            if comb.count == self.top.count and comb.max_value > self.top.max_value)

    def _generate_three_pluses(self):
        _Self = CombinationGenerator
        _Type = CombinationType

        if self.top.type not in (_Type.Empty, _Type.ThreePlusSingle, _Type.ThreePlusPair):
            return

        # Three plus Single & Pair
        required_length = {
            _Type.Empty: -1,
            _Type.ThreePlusSingle: self.top.count // 4,
            _Type.ThreePlusPair: self.top.count // 5,
        }.get(self.top.type)

        for three_seq in _Self._get_all_sequences(self.cards, 3):
            length = sum(three_seq.values()) // 3
            max_value = max(card_values[card] for card in three_seq)
            if (required_length != -1 and length != required_length) or max_value <= self.top.max_value:
                continue

            new = _Self._take_off(self.cards, three_seq)
            for _type, _func in ((_Type.ThreePlusSingle, _Self._get_single_combs),
                                 (_Type.ThreePlusPair, _Self._get_pair_combs)):
                if self.top.type != _Type.Empty and self.top.type != _type:
                    continue

                for seq in _func(new, length):
                    comb = Combination(_Self._combine(three_seq, seq))
                    if comb.type == _type and comb.max_value == max_value:
                        yield comb.to_list()

    def _generate_four_pluses(self):
        _Self = CombinationGenerator
        _Type = CombinationType

        if self.top.type not in (_Type.Empty, _Type.FourPlusSingle, _Type.FourPlusPair):
            return

        # Four plus Single & Pair
        for four_seq in _Self._get_all_sequences(self.cards, 4):
            max_value = max(card_values[card] for card in four_seq)
            if max_value <= self.top.max_value:
                continue

            new = _Self._take_off(self.cards, four_seq)
            for _type, _func in ((_Type.FourPlusSingle, _Self._get_single_combs),
                                 (_Type.FourPlusPair, _Self._get_pair_combs)):
                if self.top.type != _Type.Empty and self.top.type != _type:
                    continue

                for seq in _func(new, 2):
                    comb = Combination(_Self._combine(four_seq, seq))
                    if comb.type == _type and comb.max_value == max_value:
                        yield comb.to_list()

    def _generate(self):
        assert self.top.type != CombinationType.Unknown

        if self.top.type != CombinationType.Empty:
            yield ["pass"]
        yield from self._generate_seqs()
        yield from self._generate_three_pluses()
        yield from self._generate_four_pluses()
        yield from self._generate_bombs()

    def __iter__(self):
        return self._generate()

    def __next__(self):
        return next(self._generate())


if __name__ == "__main__":
    def test_combination():
        cases = [
            Counter(["3", "3", "3", "4", "4", "4", "5", "5", "5", "K", "K", "K"]),
            Counter(["Red Joker", "Black Joker"]),
            Counter(["10", "J", "Q", "K", "A", "2"]),
            Counter(["4", "4", "4", "4", "A", "A"]),
            Counter(["4", "4", "4", "4", "A", "A", "A", "A"]),
            Counter(["A", "A", "A", "A"]),
            Counter(["A", "A", "A", "A", "K", "K", "K", "K"]),
            Counter(["A", "A", "A", "A", "2", "2", "2", "2"]),
            Counter(["K", "K", "K", "K", "A", "A", "A", "A", "2", "2", "2", "2"]),
            Counter(["Q", "Q", "Q", "Q", "K", "K", "K", "K", "A", "A", "A", "A"]),
            Counter(["Q", "Q", "Q", "K", "K", "K", "2", "2", "2", "2"]),
        ]

        for case in cases:
            comb = Combination(case)
            print(comb.type, comb.max_value)


    def test_combinations_generator():
        cases = [
            # (full_deck, ["3"]),
            # (full_deck, ["3", "3", "3", "3"]),
            # (full_deck, ["3", "3", "3", "4"]),
            # (full_deck, ["3", "3", "3", "3", "4", "4", "4", "4"]),
            # (full_deck, ["3", "4", "5", "6", "7"]),
            # (full_deck, ["3", "3", "3", "3", "4", "4"]),
            # (full_deck, ["3", "3", "3", "3", "4", "4", "5", "5"]),
            # (full_deck, []),
            # (full_deck[:20], []),
            (["6", "7", "8", "9", "10"], ["3", "4", "5", "6", "7"]),
        ]

        def to_str(cards):
            return " ".join(cards)

        for case in cases:
            # print(f"{len(combs)} combinations")
            seen = set()
            for comb in CombinationGenerator(*case):
                str_comb = to_str(comb)
                print(comb)
                if str_comb in seen:
                    # print(comb)
                    print("Duplicate found")
                else:
                    seen.add(str_comb)


    # test_combination()
    test_combinations_generator()
