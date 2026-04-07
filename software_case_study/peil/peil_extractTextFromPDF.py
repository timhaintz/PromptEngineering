"""
PDF Text Extraction and Azure OpenAI Processing Pipeline.

Extracts text from research paper PDFs page-by-page, constructs structured
prompts for Azure OpenAI, and saves categorised responses to timestamped
JSON files. Supports multiple extraction modes (prompt pattern extraction,
summarisation, keypoint extraction, free-form questions) with optional
few-shot prompting.

Author: Tim Haintz
Created: 20/8/2023
Version: 0.2

References:
    https://pypi.org/project/PyMuPDF/
    https://learn.microsoft.com/en-us/azure/cognitive-services/openai/chatgpt-quickstart

Example Usage:
    python extractTextFromPDF.py -filename "Test.pdf"
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -extractexamples True
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -extractexamples True -use_few_shot True
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -summary True
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -keypoints True
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -prompt "YOUR QUESTION"
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -prompt "YOUR QUESTION" -printtoscreen True
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from dotenv import load_dotenv
from openai import AzureOpenAI, APIError, APIConnectionError, RateLimitError

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment & Configuration
# ---------------------------------------------------------------------------
load_dotenv()


@dataclass(frozen=True)
class AzureOpenAIConfig:
    """Immutable configuration for the Azure OpenAI client."""

    model: str
    api_version: str
    api_key: str
    azure_endpoint: str
    temperature: float = 0.0
    pages_per_set: int = 200
    output_root: str = "extractedPromptPatternsFromPDF"

    @classmethod
    def from_env(cls) -> "AzureOpenAIConfig":
        """Build configuration from environment variables.

        Raises:
            SystemExit: If any required environment variable is missing.
        """
        required_vars = {
            "model": "AZUREVSEASTUS2_OPENAI_GPT41_MODEL",
            "api_version": "AZUREVSEASTUS2_OPENAI_GPT41_API_VERSION",
            "api_key": "AZUREVSEASTUS2_OPENAI_KEY",
            "azure_endpoint": "AZUREVSEASTUS2_OPENAI_ENDPOINT",
        }
        values: dict[str, str] = {}
        missing: list[str] = []
        for field, env_var in required_vars.items():
            val = os.getenv(env_var)
            if not val:
                missing.append(env_var)
            else:
                values[field] = val

        if missing:
            logger.error(
                "Missing required environment variables: %s", ", ".join(missing)
            )
            sys.exit(1)

        return cls(**values)


# ---------------------------------------------------------------------------
# Extraction mode enum-like constants
# ---------------------------------------------------------------------------
MODE_EXTRACT = "extractexamples"
MODE_SUMMARY = "summary"
MODE_KEYPOINTS = "keypoints"
MODE_PROMPT = "prompt"

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------
SYSTEM_PROMPTS: dict[str, str] = {
    MODE_EXTRACT: (
        "# INSTRUCTIONS\n"
        "You are a PhD student collecting prompt engineering examples from "
        "research papers. Provide the prompt examples only, I don't need the "
        "response from the paper.\n"
        "ONLY use the provided input text to extract the examples.\n"
        "Reflect on the input data to confirm all the prompt examples are "
        "complete and correct before providing the output. Let's think "
        "step-by-step.\n"
        "If no examples are found, provide the output in JSON format "
        "{<<Error or No Examples>>}.\n"
        "OUTPUT\n"
        "{\n"
        '    "CategoriesAndPatterns": [\n'
        "        {\n"
        '            "PatternCategory": "Category 1",\n'
        '            "PromptPatterns": [\n'
        '                {"PatternName": "Pattern 1", "ExamplePrompts": []},\n'
        '                {"PatternName": "Pattern 2", "ExamplePrompts": []}\n'
        "            ]\n"
        "        },\n"
        "        {\n"
        '            "PatternCategory": "Category 2",\n'
        '            "PromptPatterns": [\n'
        '                {"PatternName": "Pattern 3", "ExamplePrompts": []},\n'
        '                {"PatternName": "Pattern 4", "ExamplePrompts": []}\n'
        "            ]\n"
        "        }\n"
        "    ]\n"
        "}\n"
    ),
    MODE_SUMMARY: (
        "# INSTRUCTIONS You are a PhD student summarising research papers.\n"
        "ONLY use the provided input text to summarise the paper.\n"
        "Check the input data twice to confirm the summary is complete and "
        "correct before providing the output. Let's think step-by-step.\n"
        "OUTPUT\n"
        "{\n"
        '    "Title": "<TITLE OF THE PAPER>",\n'
        '    "Summary": "This is an example summary."\n'
        "}\n"
    ),
    MODE_KEYPOINTS: (
        "# INSTRUCTIONS\n"
        "You are a PhD student extracting keypoints from research papers.\n"
        "ONLY use the provided input text to extract the keypoints.\n"
        "Check the input data twice to confirm the keypoints are complete and "
        "correct before providing the output. Let's think step-by-step.\n"
        "OUTPUT\n"
        "{\n"
        '    "Title": "<TITLE OF THE PAPER>",\n'
        '    "KeyPoints": [\n'
        '        "- Key point 1",\n'
        '        "- Key point 2",\n'
        '        "- Key point 3"\n'
        "    ]\n"
        "}\n"
    ),
    MODE_PROMPT: (
        "# INSTRUCTIONS\n"
        "You are a PhD student reading research papers. You will be asked "
        "questions about the paper.\n"
        "Check the input data twice to confirm the answer is complete and "
        "correct before providing the output. Let's think step-by-step.\n"
        "Add the Title of the paper as the value for the Title key.\n"
        "Add the answer to the question as the value for the Answer key.\n"
        'If you don\'t know the answer, say "I don\'t know" as the value '
        "for the Answer key.\n"
        "OUTPUT\n"
        "{\n"
        '    "Title": "<TITLE OF THE PAPER>",\n'
        '    "Answer": "Answer."\n'
        "}\n"
    ),
}

FEW_SHOT_USER: dict[str, str] = {
    MODE_EXTRACT: (
        "Please find examples of a prompt category, prompt pattern, and "
        "prompt example in the following:\n\n"
        "Q: There are 15 trees in the grove. Grove workers will plant trees "
        "in the grove today. After they are done, there will be 21 trees. "
        "How many trees did the grove workers plant today?\n\n"
        "Q: John found that the average of 15 numbers is 40. If 10 is added "
        "to each number then the mean of the numbers is? Answer Choices: "
        "(a) 50 (b) 45 (c) 65 (d) 78 (e) 64\n\n"
        'Q: Take the last letters of the words in "Elon Musk" and '
        "concatenate them.\n"
    ),
}

FEW_SHOT_ASSISTANT: dict[str, str] = {
    MODE_EXTRACT: json.dumps(
        {
            "CategoriesAndPatterns": [
                {
                    "PatternCategory": "AQuA Dataset",
                    "PromptPatterns": [
                        {
                            "PatternName": "Math Word Problems",
                            "ExamplePrompts": [
                                "There are 15 trees in the grove. Grove workers "
                                "will plant trees in the grove today. After they "
                                "are done, there will be 21 trees. How many trees "
                                "did the grove workers plant today?"
                            ],
                        },
                        {
                            "PatternName": "Algebraic Word Problems",
                            "ExamplePrompts": [
                                "John found that the average of 15 numbers is 40. "
                                "If 10 is added to each number then the mean of "
                                "the numbers is? Answer Choices: (a) 50 (b) 45 "
                                "(c) 65 (d) 78 (e) 64"
                            ],
                        },
                    ],
                },
                {
                    "PatternCategory": "Last Letter Concatenation Task",
                    "PromptPatterns": [
                        {
                            "PatternName": "Last Letter Concatenation",
                            "ExamplePrompts": [
                                'Take the last letters of the words in "Elon Musk" '
                                "and concatenate them."
                            ],
                        }
                    ],
                },
            ]
        },
        indent=4,
    ),
}

USER_PROMPTS: dict[str, str] = {
    MODE_EXTRACT: (
        "Please extract the prompt categories and prompt patterns from the "
        "following text:\n\n"
    ),
    MODE_SUMMARY: "Please summarise the following paper:\n\n",
    MODE_KEYPOINTS: "Please extract the keypoints from the following paper:\n\n",
}


# ---------------------------------------------------------------------------
# PDF text extraction
# ---------------------------------------------------------------------------
@dataclass
class PageText:
    """A single page of extracted text."""

    page_number: int
    text: str


_ESCAPE_TABLE: list[tuple[str, str]] = [
    ("\\", "\\\\"),
    ("/", "\\/"),
    ("'", "\\\\'"),
    ('"', '\\"'),
    ("\n", "\\n"),
    ("\r", "\\r"),
    ("\t", "\\t"),
    ("\b", "\\b"),
    ("\f", "\\f"),
]


def _escape_text(raw_text: str) -> str:
    """Apply legacy escape-sequence replacements to extracted page text."""
    result = raw_text
    for old, new in _ESCAPE_TABLE:
        result = result.replace(old, new)
    return result


def extract_text_from_pdf(pdf_path: str) -> tuple[str | None, str, list[PageText]]:
    """Open *pdf_path*, extract per-page text, and return metadata.

    Returns:
        A tuple of (document_title, file_name, list_of_PageText).
    """
    with fitz.open(pdf_path) as doc:
        title: str | None = doc.metadata.get("title")
        file_name = os.path.basename(pdf_path)

        logger.info("Title: %s", title)
        logger.info("File name: %s", file_name)

        pages = [
            PageText(page_number=i + 1, text=_escape_text(doc[i].get_text()))
            for i in range(doc.page_count)
        ]

    return title, file_name, pages


# ---------------------------------------------------------------------------
# Page-range filtering
# ---------------------------------------------------------------------------
def filter_pages(
    pages: list[PageText], pages_arg: str | None
) -> list[PageText]:
    """Return the subset of *pages* indicated by a ``'start-end'`` string."""
    if not pages_arg:
        return pages

    parts = pages_arg.split("-")
    start = int(parts[0])
    end = int(parts[-1])
    return [p for p in pages if start <= p.page_number <= end]


# ---------------------------------------------------------------------------
# Message construction
# ---------------------------------------------------------------------------
def build_messages(
    system: str,
    user: str,
    data: str,
    *,
    few_shot_user: str | None = None,
    few_shot_assistant: str | None = None,
) -> list[dict[str, str]]:
    """Assemble the chat-completion message list.

    The few-shot pair is inserted between the system message and the
    real user message when provided.
    """
    messages: list[dict[str, str]] = [{"role": "system", "content": system}]

    if few_shot_user:
        messages.append({"role": "user", "content": few_shot_user})
    if few_shot_assistant:
        messages.append({"role": "assistant", "content": few_shot_assistant})

    messages.append({"role": "user", "content": user + data})
    return messages


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------
def parse_response(raw: str) -> Any:
    """Strip optional Markdown code fences and attempt JSON parse.

    Returns a parsed ``dict``/``list`` on success or the raw string on failure.
    """
    text = raw.strip()
    if text.startswith("```json") and text.endswith("```"):
        text = text[len("```json") : -len("```")].strip()
    elif text.startswith("```") and text.endswith("```"):
        text = text[3:-3].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


# ---------------------------------------------------------------------------
# File output
# ---------------------------------------------------------------------------
def save_response(
    data: Any,
    output_dir: Path,
    file_name: str,
) -> Path:
    """Write *data* as indented JSON to *output_dir / file_name*.

    Creates *output_dir* if it does not exist. Returns the full path.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / file_name
    logger.info("Saving output to %s", out_path)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=4, ensure_ascii=False)
    return out_path


# ---------------------------------------------------------------------------
# Mode resolution
# ---------------------------------------------------------------------------
def resolve_mode(args: argparse.Namespace) -> str:
    """Determine which extraction mode the user requested.

    Raises:
        SystemExit: If no mode flag was supplied.
    """
    if args.extractexamples:
        return MODE_EXTRACT
    if args.summary:
        return MODE_SUMMARY
    if args.keypoints:
        return MODE_KEYPOINTS
    if args.prompt:
        return MODE_PROMPT

    logger.error(
        "No extraction mode specified. Use one of: "
        "-extractexamples, -summary, -keypoints, -prompt"
    )
    sys.exit(1)


def build_messages_for_mode(
    mode: str, text: str, *, user_prompt_override: str | None = None,
    use_few_shot: bool = False,
) -> list[dict[str, str]]:
    """Build the correct message list for *mode*.

    Parameters:
        mode: One of MODE_EXTRACT, MODE_SUMMARY, MODE_KEYPOINTS, MODE_PROMPT.
        text: The concatenated page text to analyse.
        user_prompt_override: Free-form prompt text (for MODE_PROMPT).
        use_few_shot: Whether to include the few-shot example pair.
    """
    system = SYSTEM_PROMPTS[mode]

    if mode == MODE_PROMPT:
        user = user_prompt_override or ""
    else:
        user = USER_PROMPTS[mode]

    few_user = FEW_SHOT_USER.get(mode) if use_few_shot else None
    few_asst = FEW_SHOT_ASSISTANT.get(mode) if use_few_shot else None

    return build_messages(system, user, text, few_shot_user=few_user, few_shot_assistant=few_asst)


# ---------------------------------------------------------------------------
# CLI definition
# ---------------------------------------------------------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all supported flags."""
    parser = argparse.ArgumentParser(
        description="Extract text from a PDF and process it with Azure OpenAI."
    )
    parser.add_argument(
        "-filename", type=str, required=True,
        help="Path to the PDF file."
    )
    parser.add_argument(
        "-pages", type=str, default=None,
        help="Page range to process, e.g. '1-10'."
    )
    parser.add_argument(
        "-extractexamples", type=bool, default=False,
        help="Extract prompt engineering examples."
    )
    parser.add_argument(
        "-use_few_shot", type=bool, default=False,
        help="Include the few-shot example pair."
    )
    parser.add_argument(
        "-summary", type=bool, default=False,
        help="Summarise the PDF."
    )
    parser.add_argument(
        "-keypoints", type=bool, default=False,
        help="Extract keypoints from the PDF."
    )
    parser.add_argument(
        "-prompt", type=str, default=None,
        help="Free-form question to ask about the PDF."
    )
    parser.add_argument(
        "-printtoscreen", type=bool, default=False,
        help="Print the result to stdout."
    )
    return parser


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main() -> None:
    """Entry point: parse args, extract PDF text, query Azure OpenAI, save."""
    args = build_arg_parser().parse_args()
    config = AzureOpenAIConfig.from_env()

    # -- Extract and filter pages ------------------------------------------
    title, file_name, pages = extract_text_from_pdf(args.filename)
    pages = filter_pages(pages, args.pages)

    if not pages:
        logger.warning("No pages to process after filtering.")
        return

    # -- Resolve mode and prepare output directory -------------------------
    mode = resolve_mode(args)
    stem = os.path.splitext(file_name)[0].replace(".", "_")
    output_dir = Path(config.output_root) / stem
    iso_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # -- Create client once ------------------------------------------------
    client = AzureOpenAI(
        api_key=config.api_key,
        api_version=config.api_version,
        azure_endpoint=config.azure_endpoint,
    )

    # -- Process page sets -------------------------------------------------
    for i in range(0, len(pages), config.pages_per_set):
        page_set = pages[i : i + config.pages_per_set]
        first_page = page_set[0].page_number
        last_page = page_set[-1].page_number
        page_range_label = f"{first_page}-{last_page}"
        logger.info("Processing pages %s", page_range_label)

        combined_text = "\f".join(p.text for p in page_set)

        messages = build_messages_for_mode(
            mode,
            combined_text,
            user_prompt_override=args.prompt,
            use_few_shot=bool(args.use_few_shot),
        )

        try:
            response = client.chat.completions.create(
                model=config.model,
                messages=messages,
                temperature=config.temperature,
            )
        except (APIError, APIConnectionError, RateLimitError) as exc:
            logger.error("Azure OpenAI API error: %s", exc)
            break
        except Exception as exc:
            logger.error("Unexpected error: %s", exc)
            break

        parsed = parse_response(response.choices[0].message.content)

        out_name = f"{iso_timestamp}_{stem}_{mode}_{page_range_label}.json"
        save_response(parsed, output_dir, out_name)

        if args.printtoscreen:
            if isinstance(parsed, (dict, list)):
                print(json.dumps(parsed, indent=4, ensure_ascii=False))
            else:
                print(parsed)


if __name__ == "__main__":
    main()
