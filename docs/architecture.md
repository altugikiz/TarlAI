# TarlAI System Architecture

## Overview

TarlAI is a three-stage multimodal pipeline powered by Gemma 4 E4B-IT.

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│   STAGE 1       │     │   STAGE 2            │     │   STAGE 3           │
│   Vision        │────>│   Agentic Tool Use   │────>│   Recommendation    │
│                 │     │                      │     │                     │
│ Gemma 4 E4B     │     │ Native Function      │     │ Gemma 4 E4B         │
│ Image Analysis  │     │ Calling              │     │ Turkish Generation  │
│                 │     │                      │     │                     │
│ Input: Photo    │     │ get_weather()        │     │ Input: All data     │
│ Output: JSON    │     │ get_treatment()      │     │ Output: Turkish     │
│ {plant, disease │     │                      │     │ recommendation      │
│  severity}      │     │                      │     │                     │
└─────────────────┘     └──────────────────────┘     └─────────────────────┘
```

## Model Details

| Property | Value |
|----------|-------|
| Model | Gemma 4 E4B-IT |
| Effective Parameters | ~4B |
| Total Parameters | ~5.1B (including embeddings) |
| Context Window | 128K tokens |
| Vision | Variable resolution (70-1120 tokens per image) |
| Function Calling | Native special tokens |
| Languages | 140+ (Turkish used in this project) |
| License | Apache 2.0 |

## Stage 1: Vision Analysis

The farmer uploads a plant photo. Gemma 4's multimodal vision encoder processes it with:
- Variable aspect ratio support (no distortion)
- Configurable token budgets for speed/accuracy tradeoff
- Structured JSON output via prompt engineering

**Prompt Strategy:** We instruct the model to respond ONLY in JSON format with specific keys. This enables reliable downstream parsing via regex JSON extraction.

## Stage 2: Agentic Tool Use

Gemma 4's native function calling uses three special token pairs:
- `<|tool>` / `<tool|>` — Tool definitions in system prompt
- `<|tool_call>` / `<tool_call|>` — Model's tool invocation
- `<|tool_result>` / `<tool_result|>` — Tool execution results

The model receives tool definitions via `apply_chat_template(tools=...)` and autonomously decides which tools to call based on the user's query.

**Observed Behavior:** Given a query about grape disease in Antalya, the model generated TWO parallel tool calls (`get_weather` + `get_treatment`) in a single turn without explicit instruction about which tools to use.

## Stage 3: Recommendation Generation

All collected data (diagnosis, weather, treatment) is fed to Gemma 4 to generate a final Turkish-language recommendation. The model acts as "TarlAI" — a friendly agricultural advisor.

**Output Includes:**
1. Disease identification and severity
2. Chemical treatment options with dosage
3. Organic/natural alternatives
4. Weather-based spraying schedule
5. Prevention tips for future seasons

## Edge Deployment Path

The E4B model is specifically designed for edge/on-device deployment:
- Runs on devices with ~4GB RAM
- Supports offline operation (no internet required)
- Available via Ollama: `ollama run gemma4:e4b`
- Android deployment via LiteRT-LM with 2-bit/4-bit quantization

This makes TarlAI viable for rural areas with limited connectivity.
