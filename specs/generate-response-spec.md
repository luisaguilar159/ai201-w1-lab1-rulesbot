# Spec: `generate_response()`

**File:** `generator.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user query and a list of retrieved rule chunks, generate a response that directly answers the question using only the retrieved text as context. The response must be grounded — it should not draw on the model's general knowledge of board games, only on what was retrieved.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's original question |
| `retrieved_chunks` | `list[dict]` | Ranked list of chunks from `retrieve()`, each with `"text"`, `"game"`, and `"distance"` |

**Output:** `str`

A plain string containing the response to show the user. The response should:
- Answer the question using only the retrieved rule text
- Identify which game the answer comes from
- Acknowledge clearly when the answer is not found in the loaded rules

Returns a fallback string (not an error) when `retrieved_chunks` is empty.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Context formatting

*How will you format the retrieved chunks before passing them to the LLM? Describe the structure — not the code. Consider: will you label chunks by game? Include distance scores? Separate chunks with delimiters?*

```
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

<context>
<source rank="1" game="Uno">
Players may draw one card when they cannot play a valid card...
</source>

<source rank="2" game="Uno">
A Wild Draw Four card can only be played when the player has no matching color card...
</source>

<source rank="3" game="Chess">
A king is in check when...
</source>
</context>

---

### RESPONSE BEHAVIOR

- Be concise and factual.
- Do not mention embeddings, retrieval, or system behavior.
- Do not explain missing information unless required by fallback rule.

When answering, include citations in the format:

(Sources: games)

Example:
A Wild Draw Four card can only be played when no matching color card is available. (Sources: Uno)
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
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
```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
When answering, include citations in the format:

(Sources: games)

Example:
A Wild Draw Four card can only be played when no matching color card is available. (Sources: Uno)
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
"I couldn’t find this information in the provided rulebooks for [game(s)]."

Optionally add:
"Please check the official rulebook or provide more context."
```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
I'll pass them all in, and instead of sending the distance, I'll use a rank tag for the XML tags in my context formatted string.
This way the LLM will now which chunk has a higher rank, in other words, the most relevant.
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
In the system message, I put the context: the LLM's role, the grounding instruction, the context formatting, the fallback behavior, and the citation instruction for the sources.
In the user message, I put the user's query.
```

---

## Implementation Notes

*Fill this in after implementing and testing.*

**Test query and response:**

```
Query: How can I win?
Response: To win, you must complete the conditions specific to the game being played. In Risk, the first player to complete their secret mission wins, or in classic play, the last player to hold any territory wins. In Clue, the first player to make a correct Accusation wins. In Catan, the first player to reach 10 Victory Points on their own turn wins immediately. (Sources: Risk, Clue, Catan)
Correctly grounded? Yes
Cited the right game? Yes

Query: I'm with my friends and we were thinking about playing Uno. How many players can play?
Response: Uno is a card game for 2–10 players. (Sources: Uno)
Correctly grounded? Yes
Cited the right game? Yes

Query: Can you tell me how can I pass the Grant Theft Auto San Andreas game?
Response: I couldn’t find this information in the provided rulebooks for Ticket To Ride, Risk.
Please check the official rulebook or provide more context.
Correctly grounded? Yes
Cited the right game? Yes, it was a game not in scope.

```

**One thing you changed from your original spec after seeing the actual output:**

```
How to format the retrieved chunks. I read the LLM prefers structured formats, so I used XML tags for the context.
```
