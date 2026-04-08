# Multimodal PEIL + Agent Case Study

**Thesis reference:** Chapter 6, §6.4 — Multimodal Case Study: Vision-Based Categorisation

## Overview

This case study compares two approaches to the same vehicle damage assessment task using the same image (`blueCorollaCrash.jpg`):

1. **Baseline (2024):** Naive categorising prompt → GPT-4 Vision API → 5-field JSON with "N/A" for repair cost
2. **PEIL + Agent (2026):** PEIL Skill-generated prompt → Claude Opus 4.6 via GitHub Copilot in VS Code with tool calling → 7-component breakdown with AUD repair estimates

## Files

| File | Description |
|------|-------------|
| `peil_prompt.txt` | The PEIL-structured prompt used for the 2026 assessment |
| `response.json` | The full JSON response from Claude Opus 4.6 |
| `tool_calls.md` | Log of all web fetch attempts and retrieved data |

## Key Findings

- PEIL's structured prompt produced a per-component damage breakdown (7 components) vs the baseline's single paragraph description
- Tool calling enabled AUD cost estimates ($5,600–$11,400 total) vs the baseline's "N/A"
- The PEIL prompt's fabrication control instruction ("do not fabricate cost estimates") was validated: estimates were grounded in retrieved Oneflare data
- 10 of 12 Australian cost sites blocked content extraction, demonstrating real-world tool calling limitations
- The model correctly identified the vehicle as a 12th-gen (E210) Toyota Corolla hatchback, adding the year range that the 2024 baseline did not provide

## Model and Platform

- **Assessment model:** Claude Opus 4.6 (via GitHub Copilot in VS Code)
- **Tool:** `fetch_webpage` (VS Code Copilot built-in)
- **Date:** 8 April 2026
- **PEIL Skill used:** `skills/peil/SKILL.md`
