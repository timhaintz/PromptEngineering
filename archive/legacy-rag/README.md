# Retired legacy RAG workflow

The owner confirmed on 3 November 2026 that this research RAG workflow is no
longer used. `autogen02_research_assistant.py.txt` preserves the original script
unchanged for historical reference. It is not a supported executable entry point.

ChromaDB and its otherwise unused dependency chain have been removed from the
Python workspace. No database or collection files are changed by this retirement.
The ordinary `autogen02_two_agents.py` chat and current evaluation tooling remain
supported without the legacy retrieval components.

Restoring this example requires a separate dependency and security review; the
historical imports and APIs should not be used as installation instructions.
