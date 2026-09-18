from app.graph.state import ChatGraphState
from app.services.bedrock.client import BedrockChatClient

bedrock_client = BedrockChatClient()


async def generate_answer(state: ChatGraphState) -> ChatGraphState:
    if not state["crawled_chunks"]:
        state["answer"] = "I could not extract useful website content for this query. Try a different page URL or a more specific question."
        return state

    answer = await bedrock_client.answer(state["question"], state["crawled_chunks"])
    state["answer"] = answer
    return state
