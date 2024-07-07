"""OpenAI API Controller"""
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from enum import Enum
from pydantic import BaseModel


class RoleEnum(str, Enum):
    system = 'system'
    user = 'user'
    assistant = 'assistant'


class MessageContext(BaseModel):
    role: RoleEnum
    content: str


class OpenAIAPI:

    def __init__(
            self,
            api_key: str,
            model: str = "gpt-4o"
    ):
        self.api_key = api_key
        self.openai = OpenAI(api_key=api_key)
        self.model = model

    def set_model(self, model: str):
        self.model = model

    def send_message_contexts(
            self,
            contexts: list[MessageContext],
            json_mode: bool = False
    ) -> ChatCompletion:
        return self.openai.chat.completions.create(
            model=self.model,
            messages=[message.model_dump() for message in contexts],
            response_format={"type": "json_object" if json_mode else "text"}
        )


if __name__ == "__main__":
    from settings import Settings

    config = Settings()

    user_context = MessageContext(role="user", content="I need help with my account.")

    openai_api = OpenAIAPI(api_key=config.openai_api_key)

    response = openai_api.send_message_contexts([user_context])
    print(response.choices[0].message.content)