import re
import json
from openai import OpenAI

DEFAULT_MODEL = "gpt-5-mini"


class LLMClient:
    def __init__(self):
        self.client = OpenAI()

    def chat(self, messages, model=DEFAULT_MODEL):
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages
            )

            return completion.choices[0].message.content

        except Exception as e:
            print(f"[LLMClient] Error: {str(e)}")
            return ""

    def json(self, messages, model=DEFAULT_MODEL):
        messages.insert(0, {"role": "system", "content": "Respond only in valid JSON format."})
        content = self.chat(messages, model)

        try:
            json_match = re.search(r"({[\s\S]*})", content)
            json_str = json_match.group(1)
            json_obj = json.loads(json_str)
            return json_obj

        except Exception as e:
            print(f"[LLMClient] Error: {str(e)}")
            return None


if __name__ == "__main__":
    llm = LLMClient()
    messages = [
        {"role": "user", "content": "Hello"}
    ]
    response = llm.chat(messages)
    print(f"Response: {response}")
