from langgraph.graph import END, START, StateGraph

from app.graph.nodes.crawl_node import crawl_website
from app.graph.nodes.generate_node import generate_answer
from app.graph.state import ChatGraphState


def build_chat_graph():
    graph = StateGraph(ChatGraphState)
    graph.add_node("crawl_website", crawl_website)
    graph.add_node("generate_answer", generate_answer)

    graph.add_edge(START, "crawl_website")
    graph.add_edge("crawl_website", "generate_answer")
    graph.add_edge("generate_answer", END)

    return graph.compile()


chat_graph = build_chat_graph()
