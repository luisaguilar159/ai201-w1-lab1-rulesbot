# Spec: `retrieve()`

**File:** `retriever.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user's natural language query, find the most relevant chunks from the vector store using semantic similarity search. Return them ranked by relevance so that `generate_response()` can use them as context.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's natural language question |
| `n_results` | `int` | Maximum number of chunks to return (default: `N_RESULTS` from `config.py`) |

**Output:** `list[dict]`

Each dict in the returned list must contain exactly these keys:

| Key | Type | Description |
|-----|------|-------------|
| `"text"` | `str` | The chunk text |
| `"game"` | `str` | The game name this chunk came from |
| `"distance"` | `float` | Cosine distance score — lower means more similar to the query |

Results should be ordered from most to least relevant (lowest to highest distance). Returns an empty list `[]` if the collection contains no documents.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Query approach

*Describe how you will use `_collection.query()` to find relevant chunks. What arguments will you pass, and why?*

```
I'll use the _collection.query() method to find relevant chunks in ChromaDB. For this, I'll set 3 arguments.
- query_texts: I'll initialize an array of strings with the query from the user.
- n_results: I'll use the default value from `config.py`, which is 3 results
- include: I'll specify what data I want ChromaDB to return. I'll put `documents` for the chunk texts, `metadatas` for the game name, and `distances` for the distance score to rank each chunk.
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
[
    {
        "text": "When you play your second-to-last card and have only one card remaining",
        "game": "uno",
        "distance": 0.2
    }
]
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
Since I'm sending just one query, I'll access the 0 index.
Nesting exists because we could be sending multiple queries to ChromaDB.
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
Well, if I don't get any good distance score from my chunks, like a ton of 0.8 scores, I'll need to review my chunking strategy.
Maybe the semantic value within each chunk is bad, so I'll need to change the chunking strategy.
I was planning to return al "n_results" and sort them by distance score on DESC order to get the most relevant on index 0.
```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
(a) Is its empty, it returns an empty list []
(b) If no matches are found, it returns an empty list []
(c) It matches for multiple games only if I send a general question. Like "How do I win?"
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```
Query: How many players can play a Uno game?
Top result game: Uno
Distance score: 0.275
Does it make sense? Yes, because the chunk contains that Uno is a card game for 2-10 players.
```

**One thing about the query results that surprised you:**

```
The format they came in. I thought it would return a nice list format, but it gave us nested lists.
```
