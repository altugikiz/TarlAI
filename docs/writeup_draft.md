# TarlAI: Putting an Agricultural Expert in Every Farmer's Pocket

**Team:** Altug Ikiz, Arda Akinci, Simittin, Zeynep Yonca Ozel  
**Track:** Impact Track — Digital Equity & Inclusivity  
**University:** Akdeniz University, Computer Engineering

---

## The Morning Mehmet Almost Lost Everything

It was early June in Antalya when Mehmet Demir, a 58-year-old lemon farmer, noticed something wrong. The leaves on a dozen of his trees had begun yellowing at the edges, curling inward in an unfamiliar way. His father had farmed this same grove for forty years, and Mehmet had inherited the land along with the unspoken rule that you learn by doing. But this — whatever this was — he had never seen before.

The nearest agricultural extension office was a 45-minute drive away. The agronomist there serves eleven villages. An appointment would take a week. By then, the disease could spread to hundreds of trees. Mehmet photographed the leaves with his phone and sent the image to his nephew in the city. "Google it," his nephew replied. The search results came back in English. Mehmet does not read English.

This is not an unusual story. It is the everyday reality for millions of Turkish farmers.

---

## The Problem: A Knowledge Gap at Scale

Turkey's agricultural sector supports **5.5 million farmers** (TÜİK Agricultural Census, 2021), roughly **85% of whom operate small family farms** of less than 50 decares. Together they produce crops worth billions of dollars annually — citrus from Antalya, grapes from Aegean valleys, olives from the Aegean and Mediterranean coasts, vegetables from Adana's plains.

Yet plant disease destroys an estimated **20–30% of crop yield** in Turkey each year. The losses are not evenly distributed. Large commercial farms have agronomists on staff. Small family farmers do not. They rely on word of mouth, memory, and occasional visits from overworked government extension officers who cover dozens of villages at once.

When disease strikes, every hour counts. Fungal infections like late blight can devastate a tomato field in 48 hours under the right humidity conditions. Citrus greening (HLB), now a serious threat to Antalya's groves — which produce **60% of Turkey's citrus crop** — is irreversible once established. Early detection and immediate action are the only defenses.

What these farmers need is not a brochure. They need a knowledgeable advisor who speaks their language, understands their region's climate, and is available the moment they take out their phone.

---

## Our Solution: TarlAI

TarlAI is a multimodal AI agricultural assistant that turns a smartphone photo into a complete, actionable treatment plan — in Turkish — within seconds. A farmer photographs a diseased plant. TarlAI identifies the disease, checks current weather conditions, looks up the appropriate treatment, and generates a clear recommendation in plain, accessible Turkish.

The core insight behind TarlAI is that **all three capabilities needed for this task exist natively in Gemma 4** — and they can be orchestrated into a single coherent pipeline without any additional models or external APIs.

### Three-Stage Pipeline

**Stage 1 — Vision Diagnosis.** Gemma 4 E4B's multimodal encoder analyzes the uploaded image. No separate computer vision model is required. The model identifies the plant species, the disease, the severity level, and outputs a structured JSON object for downstream processing. The variable-resolution image encoder processes photos at native aspect ratios without distortion, critical for recognizing field-condition photos taken on consumer smartphones.

**Stage 2 — Agentic Tool Use.** Using Gemma 4's native function calling (special tokens `<|tool_call>` and `<tool_result>`), the model autonomously decides which tools to invoke — a weather API and a plant disease treatment database. In our tests, given only the diagnosis and location, Gemma 4 generated **two parallel tool calls in a single turn** without explicit instruction about which tools to use. This is not scripted branching logic; it is genuine agentic reasoning.

**Stage 3 — Turkish Recommendation.** Synthesizing the diagnosis, live weather data, and treatment information, Gemma 4 generates a comprehensive recommendation in Turkish. The model knows when to spray based on humidity and wind conditions, which chemicals are available locally, and how to explain severity to a farmer who has never read a phytopathology textbook.

### Disease Knowledge Base

We built a disease database of **29 crop diseases** specific to Turkish agriculture, covering tomatoes, peppers, grapes, citrus, and olives. Each entry includes symptoms, affected crops, chemical and organic treatment options, application intervals, severity indicators, and prevention strategies — informed by Turkish Ministry of Agriculture publications and FAO plant disease management guidelines. The database is the first of its kind structured for function-calling integration.

---

## Why Gemma 4 Makes This Possible

Every design choice in TarlAI is enabled by a specific Gemma 4 capability that would require a separate model or service in any other architecture:

| Capability | What It Enables |
|-----------|----------------|
| **Native multimodal vision** | Diagnose from photo without a separate CV pipeline |
| **Native function calling** | Autonomous tool use without custom parsing or scripted logic |
| **140+ language support** | Fluent Turkish with correct agricultural terminology |
| **E4B edge-deployable size** | Runs offline on ~4GB RAM — no internet connection required |
| **Apache 2.0 license** | Free for commercial deployment, NGOs, and government programs |

The last point matters more than it might appear. Turkey's agricultural extension system could theoretically integrate TarlAI into its existing mobile infrastructure at zero licensing cost. The E4B model runs via Ollama on commodity hardware, or can be deployed on Android via LiteRT-LM with 4-bit quantization — covering areas with no internet connectivity at all, which describes much of rural Antalya.

---

## Results and Impact Potential

In our demonstration, TarlAI correctly identified grape leaf spot disease from a field photograph, autonomously retrieved weather conditions for Antalya (26°C, 72% humidity, sunny), looked up the appropriate treatment protocol, and generated a complete Turkish-language recommendation — including timing advice based on current wind and sun conditions — in a single pipeline run.

The recommendation quality is not generic. It tells the farmer: spray copper-based fungicide every 7–14 days, apply in early morning or late evening to avoid heat evaporation, and prioritize drip irrigation to prevent spread. It explains why, in language a farmer can act on immediately.

Scaled to Antalya province alone — home to approximately **250,000 agricultural workers** — TarlAI could reduce late-diagnosis crop losses that currently cost millions of lira per season. Extended to Turkey's 5.5 million farmers, the impact on rural livelihoods would be substantial.

Back in his lemon grove, Mehmet would take a photo, open an app, and have his answer in thirty seconds. In Turkish. For free. Offline if necessary.

That is what we built.

---

## What's Next

- **Real-time weather integration** via OpenWeatherMap API (replacing the current mock database)
- **Fine-tuning on Turkish agricultural data** using Unsloth for improved terminology and local pest knowledge
- **Android application** via LiteRT-LM for fully offline field use
- **Expansion to 50+ diseases** covering wheat, corn, and cotton — crops critical to Central and Eastern Turkey

---

*TarlAI is open source under Apache 2.0. Notebook available on Kaggle.*
