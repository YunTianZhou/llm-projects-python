from player import Player
from logger import Logger
from constant import *
from tool import *

config = read_config("config.json")


def game(players):
    players = shuffled(players)
    logger = Logger()

    # Dealing cards
    cards = shuffled(full_deck)
    stacks = [cards[i: min(54, i + 17)] for i in range(0, 54, 17)]
    logger.log_public("---------- Dealing cards ----------")
    for i, player in enumerate(players):
        player.deal_cards(stacks[i])
        logger.log_private(f"{player.name}'s cards: {", ".join(player.hand)}")

    # Bidding
    player_bid = {}
    logger.log_public("---------- Bidding the Landlord ----------")
    for i, player in enumerate(players):
        data = player.bid("\n".join(map(str, players)), logger.record)
        if not data:
            return None
        player_bid[player] = (data["bidding"], 3 - i)
        logger.log_public(f"{player.name} bids {data['bidding']}.")
        logger.log_private(f"{player.name}'s thinking: {data["reason"]}")
        if data["bidding"] == 3:
            break

    landlord = max(player_bid.keys(), key=player_bid.get)
    landlord.set_landlord(stacks[3])
    logger.log_public(f"The landlord is {landlord.name}.")
    logger.log_public(f"The landlord cards are {", ".join(stacks[3])}.")

    # Playing cards
    top = []
    last_play = None
    logger.log_public("---------- Playing cards ----------")
    curr_player = landlord
    while True:
        if curr_player == last_play:
            top = []
        print(f"{curr_player.name}'s turn, his hand is: {", ".join(curr_player.hand)}.")
        data = curr_player.play_cards("\n".join(map(str, players)), landlord.name, logger.record, top)
        if not data:
            return None
        if data["comb"] == ["pass"]:
            logger.log_public(f"{curr_player.name} passes.")
        else:
            logger.log_public(f"{curr_player.name} plays {", ".join(data["comb"])}.")
            top = data["comb"]
            last_play = curr_player
        logger.log_private(f"{curr_player.name}'s thinking: {data["reason"]}")
        if not curr_player.hand:
            break
        curr_player = players[(players.index(curr_player) + 1) % 3]

    # Ending the game
    logger.log_public("---------- Ending the game ----------")
    logger.log_public(f"{curr_player.name} finishes all cards.")
    if curr_player == landlord:
        logger.log_public("Landlord wins the game.")
    else:
        logger.log_public("Farmer wins the game.")

    return logger


def main():
    logger = Logger()
    players = [Player(**player) for player in config["players"]]
    assert len(players) == 3, "Only 3 players are supported"

    for i in range(config["rounds"]):
        logger.log_private(f"********** Dou Dizhu (Round {i + 1}) **********")
        if not (curr_logger := game(players)):
            logger.log_private("Something went wrong...")
        else:
            logger.extend(curr_logger)
        logger.log_private("")
    logger.save()


if __name__ == "__main__":
    main()
