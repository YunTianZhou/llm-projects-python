# This is a project to test if your llm configuration is correct.
from llm_client import LLMClient

MODEL = "gpt-5-mini"


def main():
    client = LLMClient()

    print("Chatbot: Hello! Type 'exit' to end the chat.")
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye!")
            break
        message = [
            {"role": "user", "content": user_input}
        ]
        response = client.chat(message)
        print(f"Chatbot: {response}")


if __name__ == "__main__":
    main()
