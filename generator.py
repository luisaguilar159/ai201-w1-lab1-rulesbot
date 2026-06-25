from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL
from typing import List
from retriever import ReturnedChunk
import html

_client = Groq(api_key=GROQ_API_KEY)


def format_chunks_to_xml(chunks: List[ReturnedChunk]) -> str:
    xml_parts = ["<context>"]

    for idx, chunk in enumerate(chunks, start=1):
        text = html.escape(chunk["text"].strip())
        game = html.escape(chunk["game"].strip())

        xml_parts.append(
            f'<source rank="{idx}" game="{game}">\n{text}\n</source>'
        )
      
    xml_parts.append("</context>")
    return "\n\n".join(xml_parts)

def generate_response(query: str, retrieved_chunks: List[ReturnedChunk]) -> str:
    """
    Generate a grounded answer from retrieved rule chunks.

    TODO — Milestone 3:

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "game"     : the game name
      - "distance" : similarity score (you can use this to filter weak matches)

    Before writing code, talk through these with your group:
      - How will you format the chunks into a context block for the prompt?
      - What instructions will stop the model from answering beyond what the
        rules say? (Grounding is the whole point — a confident wrong answer
        is worse than an honest "I don't know.")
      - How will you surface which game each answer comes from?

    Your response should:
      1. Answer using only the retrieved context — not the model's general knowledge
      2. Make clear which game the answer comes from
      3. Say so clearly when the answer isn't in the loaded rules

    Return the response as a plain string.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded rule books. "
            "Try rephrasing your question — or check that your ingestion pipeline is working."
        )

    # Your implementation here.
    formatted_chunks: str = format_chunks_to_xml(retrieved_chunks)

    final_system_prompt = f"""
    You are a retrieval-based assistant for board game rules. Your job is to help players understand and clarify rules using only the provided context from official rulebooks.

    You do not have access to external knowledge or any information outside the retrieved context.

    You are given retrieved context from a custom board-game knowledge base.
    Each source may come from a different game.

    ---

    ### RULES

    1. Answer using ONLY the information inside the provided context.
    2. Treat the context as the only source of truth.
    3. Do NOT use prior knowledge, training data, or assumptions.
    4. Do NOT infer, guess, or complete missing information.
    5. If the answer is not explicitly contained in the context, respond exactly with:

    "I couldn’t find this information in the provided rulebooks for [game(s)]."

    Optionally add:
    "Please check the official rulebook or provide more context."

    6. When referencing information, you may include the game name(s) from the source metadata.

    ---

    ### CONTEXT FORMAT

    {formatted_chunks}

    ---

    ### RESPONSE BEHAVIOR

    - Be concise and factual.
    - Do not mention embeddings, retrieval, or system behavior.
    - Do not explain missing information unless required by fallback rule.

    When answering, include citations in the format:

    (Sources: games)

    Example:
    A Wild Draw Four card can only be played when no matching color card is available. (Sources: Uno)

  """

    chat_completion = _client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"{final_system_prompt}"
            },
            {
                "role": "user",
                "content": f"{query}"
            }
        ],
        # specific model
        model=LLM_MODEL
    )

    if chat_completion:
        if chat_completion.choices[0].message.content is not None:
          # print("reply from LLM:\n", chat_completion.choices[0].message.content)
          return chat_completion.choices[0].message.content

    return "⚙️ Response generation not yet implemented. Complete Milestone 3 to activate answers."
