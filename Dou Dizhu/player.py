from sortedcontainers import SortedList
from llm_client import LLMClient
from combination import CombinationGenerator
from constant import *
from tool import *

prompt = {
    "prompt": read_from_file("prompt/prompt.txt"),
    "rules": read_from_file("prompt/rules.txt"),
    "bid": read_from_file("prompt/bid.txt"),
    "play": read_from_file("prompt/play.txt"),
}


class Player:
    def __init__(self, name, model):
        self.name = name
        self.hand = SortedList()
        self.model = model
        self.client = LLMClient()

    def __str__(self):
        return f"[{self.name}] {len(self.hand)} cards left."

    def deal_cards(self, cards):
        self.hand = SortedList(cards, key=lambda x: -card_values[x])

    def bid(self, players_info, record):
        content = [
            {
                "role": "user",
                "content": prompt["prompt"].format(
                    name=self.name,
                    rules=prompt["rules"],
                    players_info=players_info,
                    landlord_name="Undecided",
                    record="\n".join(record),
                    hand=", ".join(self.hand),
                    top="None",
                    task=prompt["bid"].format()
                )
            }
        ]

        return self._send(content)

    def set_landlord(self, extra_cards):
        self.hand.update(extra_cards)

    def play_cards(self, players_info, landlord_name, record, top):
        content = [
            {
                "role": "user",
                "content": prompt["prompt"].format(
                    name=self.name,
                    rules=prompt["rules"],
                    players_info=players_info,
                    landlord_name=landlord_name,
                    record="\n".join(record),
                    hand=", ".join(self.hand),
                    top=", ".join(top) if top else "None",
                    task=prompt["play"].format(
                        valid_combs="\n".join(map(str, CombinationGenerator(self.hand, top)))
                    )
                )
            }
        ]

        data = self._send(content)

        if not data:
            return None

        try:
            if data["comb"] != ["pass"]:
                for card in data["comb"]:
                    self.hand.remove(card)
        except KeyError:
            print(f"{self.name} encountered a KeyError: 'comb' key missing in data.")
        except ValueError:
            print(f"{self.name} plays an invalid combination: {data['comb']}. One or more cards are not in hand.")
        except Exception as e:
            print(e)
            breakpoint()

        return data

    def _send(self, content):
        data = {}
        for i in range(5):
            data = self.client.json(content, model=self.model)
            if data:
                break
            print(f"{self.name} has no response. Retry {i + 1}/5.")

        if not data:
            print(f"{self.name} has no response.")
            return None

        return data
