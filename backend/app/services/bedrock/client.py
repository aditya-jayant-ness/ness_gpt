from typing import Iterable

from langchain_aws import ChatBedrock

from app.core.settings import get_settings


class BedrockChatClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = ChatBedrock(
            model_id=settings.bedrock_model_id,
            region_name=settings.aws_region,
            credentials_profile_name=None,
        )

    async def answer(self, question: str, context_chunks: Iterable[str]) -> str:
        context = "\n\n".join(context_chunks)
        prompt = (
            "You are a website-grounded assistant. Use only the provided context to answer. "
            "If context is insufficient, say what is missing.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}"
        )
        response = await self.model.ainvoke(prompt)
        return response.content if isinstance(response.content, str) else str(response.content)
