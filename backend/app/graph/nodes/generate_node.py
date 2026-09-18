from app.graph.state import ChatGraphState
from app.services.bedrock.client import BedrockChatClient

bedrock_client = BedrockChatClient()


async def generate_answer(state: ChatGraphState) -> ChatGraphState:
    answer = await bedrock_client.answer(state["question"], state["crawled_chunks"])
    state["answer"] = answer
    return state
