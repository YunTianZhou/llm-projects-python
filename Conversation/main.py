import os
import json
import random
import datetime

from llm_client import LLMClient

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

with open("prompt.txt", "r", encoding="utf-8") as f:
    prompt = f.read()


class Member:
    def __init__(self, name, profile, description, model):
        self.name = name
        self.profile = profile
        self.description = description
        self.model = model
        self.client = LLMClient()

    def chat(self, member_info, chat_history):
        if not chat_history:
            chat_history = ["No one has been talking yet"]

        content = [
            {
                "role": "user",
                "content": prompt.format(
                    name=self.name,
                    description=self.description,
                    chatroom_name=config["chatroom_name"],
                    topic=config["topic"],
                    topic_description=config["topic_description"],
                    member_info=member_info,
                    chat_history="\n".join(chat_history[-50:])
                )
            }
        ]

        response = ""
        for _ in range(5):
            response = self.client.chat(content, model=self.model).strip()
            if response != "":
                break

        if response == "":
            print(f"{self.name} has no response, pass.")
            return "pass"

        return response


def main():
    members = [Member(**member) for member in config["members"]]
    member_info = "\n".join([f"[{member.name}] Profile: {member.profile}"
                             for member in members])
    chat_history = []

    print(f"--- Chatroom: {config["chatroom_name"]} ---")

    keep_chatting = True
    while keep_chatting:
        keep_chatting = False
        random.shuffle(members)
        for member in members:
            response = member.chat(member_info, chat_history)
            if response == "pass":
                continue
            print(f"{member.name}: {response}")
            chat_history.append(f"{member.name}: {response}")
            keep_chatting = True

    os.makedirs("history", exist_ok=True)
    date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(f"history/{date_time}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(chat_history))


if __name__ == "__main__":
    main()
