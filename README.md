# ✨ AO DevBot Knowledge Base

This repository contains a structured collection of **Question & Answer (Q&A)** entries and **Tooltip** entries used to power an AI system backed by Weaviate and RAG (Retrieval-Augmented Generation).

Each commit to this repository automatically syncs new or updated Q&A and Tooltip entries into our vector database using GitHub Actions and OpenAI embeddings. The AI backend uses this data to answer user queries with high relevance.

## 📄 Format Guidelines

All Q&A content should be written in **JSON** files (`.json`) located in the `docs/faq/` directory. Each file contains an array of Q&A entries.

### ✅ Q&A Example Format

```json
[
  {
    "question": "What is AO?",
    "answer": "AO is a decentralized computer network built on top of Arweave that enables developers to create scalable, permanent applications.",
    "tags": ["ao", "arweave", "general"]
  },
  {
    "question": "What is Arweave?",
    "answer": "Arweave is a blockchain-like protocol designed for permanent data storage. It allows users to store data indefinitely by incentivizing miners to maintain the network.",
    "tags": ["arweave", "blockchain", "storage"]
  }
]
```

- Each entry must contain:
  - `"question"`: The question string (required)
  - `"answer"`: The answer string (required)
  - `"tags"`: An array of keywords (optional but recommended)

## 🏷️ Tooltip Format

Tooltip content should be written in a single **JSON** file at `docs/tooltips.json`. This file contains an array of tooltip entries.

### ✅ Tooltip Example Format

```json
[
  {
    "term": "Process",
    "headline": "A process is a smart contract deployed on AO",
    "definition": "Processes hold state, receive messages, and have functions to handle different interactions."
  },
  {
    "term": "Permaweb",
    "headline": "The Permaweb is a decentralized and immutable web built on top of Arweave",
    "definition": "The Permaweb refers to web applications and dApps built on AO and Arweave, accessible just like the normal web - but immutable and long-lasting.",
    "link": "https://arweave.net/0eRcI5PpUQGIDcBGTPCcANkUkgY85a1VGf0o7Y-q01o/#/en/the-permaweb"
  }
]
```

- Each tooltip entry must contain:
  - `"term"`: The glossary term (required)
  - `"headline"`: A short headline or summary (required)
  - `"definition"`: The definition or explanation (required)
  - `"link"`: An external URL for more info (optional)

## 🏷️ Tagging Guidelines

Tags help categorize and filter content. They improve search relevance and allow topic-based filtering in the AI system.

- Use lowercase keywords.
- Keep tags relevant and limited (2–5 tags is ideal).
- Use consistent terminology across entries (e.g., "arweave", not "Arweave").

## DevBot Knowledge Tips & Guidelines:
- Content supports **Markdown**!  
   - You can include images: `![alt text](image-url)` (always use descriptive alt text).  
   - You can add links to videos or other resources. When including videos, use the format: `[Video - Title](video-url)` to ensure proper rendering on the devbot.
   - Use lists, code blocks, and other Markdown features for clarity.
- **Keep answers short and focused** (1–3 paragraphs, ideally 100–300 tokens).
- **Use clear language** — prioritize helpfulness and accuracy.
- Break large concepts into **multiple Q&As** if needed.
- **Do not** write overly long answers (>400 words).
- **Do not** include multiple questions in one entry.
- **Do not** add unrelated metadata or extra fields.