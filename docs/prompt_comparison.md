# TarlAI — Prompt Engineering Analysis

## Overview

Three prompts drive the TarlAI pipeline. Each was analyzed across three versions:
- **V1** — Current baseline (what's in the notebook now)
- **V2** — Structured / schema-explicit (recommended)
- **V3** — Chain-of-thought or few-shot (experimental)

Evaluation criteria (theoretical analysis — run on Kaggle GPU to confirm):

| Criterion | What it measures |
|-----------|----------------|
| **Accuracy** | Does the model output the correct structured data? |
| **Turkish Quality** | Is the Turkish output natural, correct, and accessible to farmers? |
| **Robustness** | Does it handle edge cases (blurry photo, unknown disease)? |
| **Token Efficiency** | Prompt length vs. output quality ratio |

---

## PROMPT 1 — Stage 1: Vision Diagnosis

### Context
Gemma 4 receives a plant photo and must output structured JSON. The output feeds directly into the pipeline — incorrect keys or invalid JSON breaks Stage 2.

---

### V1 — Current Baseline

```python
DIAGNOSIS_PROMPT_V1 = """You are an expert agricultural engineer. Analyze this plant image.
Respond ONLY with JSON: {"plant": "name", "disease": "name", "severity": "mild/moderate/severe", "disease_key": "snake_case_name"}"""
```

**Analysis:**
- Simple and fast
- No schema enforcement — model may deviate from expected keys
- `disease_key` format is underspecified (how to handle multi-word diseases?)
- No fallback instruction for unclear images

**Expected output quality:** Good for clear photos, brittle for edge cases

---

### V2 — Schema-Explicit (RECOMMENDED ✓)

```python
DIAGNOSIS_PROMPT_V2 = """You are an expert plant pathologist and agricultural engineer.

Analyze the plant image carefully. Identify the plant species, the disease or health condition, and its severity.

Respond ONLY with a valid JSON object matching this exact schema:
{
  "plant": "<plant species in English, e.g. tomato, grape, lemon>",
  "disease": "<disease name in English, e.g. early blight, powdery mildew>",
  "severity": "<one of: mild, moderate, severe>",
  "disease_key": "<snake_case disease identifier, e.g. early_blight, powdery_mildew>"
}

If the image is unclear or no disease is visible, use:
{
  "plant": "<plant name or unknown>",
  "disease": "healthy",
  "severity": "none",
  "disease_key": "healthy"
}

Output JSON only. No explanation. No markdown."""
```

**Why it's better:**
- Explicit schema with examples for each field → prevents key name variation
- `disease_key` format is shown by example → consistent snake_case
- Fallback case for healthy/unclear images → pipeline doesn't break
- Stronger persona ("plant pathologist") → more specific outputs
- "No markdown" instruction prevents code block wrapping

**Expected output quality:** High accuracy, consistent keys, handles edge cases

---

### V3 — Chain-of-Thought + Schema (Experimental)

```python
DIAGNOSIS_PROMPT_V3 = """You are an expert plant pathologist. Before giving your answer, think step by step:
1. What plant species is in the image? Look at leaf shape, stem structure, and any fruit/flower.
2. What symptoms are visible? (spots, discoloration, wilting, lesions, powder, etc.)
3. Based on symptoms, what disease is most likely?
4. How severe is the infection? (mild = <10% affected, moderate = 10-30%, severe = >30%)

After reasoning, output ONLY this JSON (no other text):
{"plant": "...", "disease": "...", "severity": "mild/moderate/severe", "disease_key": "snake_case"}"""
```

**Why it might help:** CoT reasoning improves vision accuracy for ambiguous cases
**Tradeoff:** +30-50 tokens in output (reasoning before JSON), requires robust JSON extraction regex

**Expected output quality:** Highest accuracy, but slower and requires reliable post-processing

---

### Prompt 1 Comparison Table

| Version | Accuracy | Robustness | Token Efficiency | Notes | Winner |
|---------|----------|------------|-----------------|-------|--------|
| V1 (current) | ★★★☆☆ | ★★☆☆☆ | ★★★★★ | Breaks on edge cases | |
| **V2 (schema)** | **★★★★☆** | **★★★★★** | **★★★★☆** | **Best balance** | **✓** |
| V3 (CoT) | ★★★★★ | ★★★★☆ | ★★★☆☆ | Needs careful JSON extraction | |

**Recommended:** V2 for production. V3 worth testing if accuracy is critical and latency is acceptable.

---

## PROMPT 2 — Stage 2: Function Calling

### Context
This prompt triggers Gemma 4's native function calling. The model receives tool definitions via `apply_chat_template(tools=[...])` and must autonomously call `get_weather(location)` and `get_treatment(disease_name)`.

---

### V1 — Current Baseline

```python
# This is hardcoded as a demo message — not parameterized
FC_PROMPT_V1 = "I found leaf spot disease on my grape plants in Antalya. When should I spray considering the weather? Respond in Turkish."
```

**Analysis:**
- Not reusable — hardcoded disease name and location
- Single tool call pattern — model may only call `get_weather` or `get_treatment`, not both
- "Respond in Turkish" may leak into the tool call decision (unnecessary)

---

### V2 — Parameterized Template (RECOMMENDED ✓)

```python
def build_fc_prompt_v2(plant: str, disease: str, location: str) -> str:
    return f"""I am a farmer. My {plant} plants in {location} have been diagnosed with {disease}.

Please:
1. Check the current weather conditions in {location}
2. Look up the treatment protocol for {disease}

Use the available tools to gather this information."""

# Example usage:
# build_fc_prompt_v2("grape", "leaf_spot", "Antalya")
```

**Why it's better:**
- Fully parameterized — works for any plant/disease/location combination
- Explicitly mentions both tools → increases likelihood of both being called
- Separates tool call from language generation → cleaner pipeline design
- Language instruction moved to Stage 3 where it belongs

**Expected behavior:** Model reliably calls both `get_weather` AND `get_treatment` in parallel

---

### V3 — System-Prompt Enriched (Experimental)

```python
FC_SYSTEM_V3 = """You are an agricultural diagnostic agent. When given information about a plant disease and location, you MUST call ALL of the following tools:
- get_weather(location): to determine optimal spray timing
- get_treatment(disease_name): to find the correct treatment protocol

Always call both tools. Do not ask clarifying questions. Do not generate text — only tool calls."""

def build_fc_prompt_v3(plant: str, disease: str, location: str) -> str:
    return f"Plant: {plant} | Disease: {disease} | Location: {location}"
```

**Why it might help:** System prompt constraint forces both tool calls, even if the user message is minimal
**Tradeoff:** System prompt support in function-calling turns depends on Gemma 4's chat template implementation

---

### Prompt 2 Comparison Table

| Version | Both Tools Called | Parameterizable | Clean Separation | Notes | Winner |
|---------|------------------|----------------|-----------------|-------|--------|
| V1 (current) | ★★★☆☆ | ★☆☆☆☆ | ★★☆☆☆ | Demo only, not reusable | |
| **V2 (parameterized)** | **★★★★☆** | **★★★★★** | **★★★★★** | **Production-ready** | **✓** |
| V3 (system prompt) | ★★★★★ | ★★★★★ | ★★★★☆ | Test with Gemma 4 chat template | |

**Recommended:** V2 immediately. Test V3 to see if system-level tool forcing improves parallel calls.

---

## PROMPT 3 — Stage 3: Turkish Recommendation

### Context
All data is now collected. The model generates the final output that the farmer reads. This is the most user-visible prompt — quality here determines whether TarlAI is actually useful.

---

### V1 — Current Baseline

```python
RECOMMENDATION_PROMPT_V1 = f"""You are TarlAI, an agricultural AI assistant for Turkish farmers.
Ignore the image. Based on this data, give a complete recommendation in Turkish:
DIAGNOSIS: {json.dumps(diagnosis)}
WEATHER: {json.dumps(weather)}
TREATMENT: {json.dumps(treatment)}
Cover: 1) Disease found 2) Treatment options 3) When to spray based on weather 4) Prevention tips
Use simple Turkish a farmer can understand."""
```

**Analysis:**
- "Ignore the image" is confusing (Stage 3 has no image)
- Severity information from diagnosis is not used to calibrate tone
- No structure instruction → output format varies between runs
- Treatment data now includes richer fields (`severity_indicators`, `prevention`) that aren't leveraged

---

### V2 — Severity-Aware Structured Persona (RECOMMENDED ✓)

```python
def build_recommendation_prompt_v2(diagnosis: dict, weather: dict, treatment: dict) -> str:
    severity = diagnosis.get("severity", "moderate")
    
    urgency_map = {
        "mild":     "Durum henüz erken evrede, ama vakit kaybetmeden harekete geçmek önemli.",
        "moderate": "Durum orta şiddette, bu hafta ilaçlama başlamalısın.",
        "severe":   "ACELE ET! Hastalık ileri seviyede, bugün veya yarın ilaçlamalısın."
    }
    urgency = urgency_map.get(severity, urgency_map["moderate"])

    return f"""Sen TarlAI'sin — Türk çiftçileri için yapay zeka destekli tarım danışmanı.
Aşağıdaki verilere dayanarak kapsamlı bir Türkçe tavsiye oluştur.
Dili sade tut: lise mezunu bir çiftçinin anlayabileceği şekilde yaz.

ACİLİYET NOTU: {urgency}

VERİLER:
- Teşhis: {json.dumps(diagnosis, ensure_ascii=False)}
- Hava durumu ({weather.get('location', '')}): {weather.get('temp')}°C, %{weather.get('humidity')} nem, {weather.get('condition')}, rüzgar {weather.get('wind_kmh')} km/s
- Tedavi bilgisi: {json.dumps(treatment, ensure_ascii=False)}

YAPI (tam olarak bu bölümleri kullan):

## 1. Tespit
[Hastalık adını ve şiddetini açıkla. Belirtileri kısaca tanımla.]

## 2. Tedavi Seçenekleri
**Kimyasal:** [İlaç adları ve uygulama sıklığı]
**Organik/Doğal:** [Alternatif yöntemler]

## 3. Spreylamanın Zamanlaması
[Hava durumuna göre ne zaman ilaçlayacağını söyle — sabah/akşam, yağmur öncesi/sonrası, rüzgar durumu]

## 4. Önleme
[Bir sonraki sezonda bu hastalıktan nasıl korunur?]

Sonunda tek cümlelik öz bir özet yaz. Samimi ve cesaretlendirici bir ton kullan."""
```

**Why it's better:**
- Severity-aware urgency note → tone adapts to how serious the situation is
- Structured section headers → consistent, parseable output across runs
- Weather data rendered as human-readable sentence, not raw JSON
- Uses Turkish directly in the prompt for Turkish output → stronger language signal
- Leverages richer treatment data (`severity_indicators`, `prevention`) from the new diseases.py

**Expected output quality:** Consistent structure, appropriate urgency, better Turkish

---

### V3 — Few-Shot Example (Experimental)

```python
FEW_SHOT_EXAMPLE = """
## Örnek Çıktı (erken yanıklık, orta şiddet):

## 1. Tespit
Domates bitkilerinizde **Erken Yanıklık** (Alternaria mantar hastalığı) tespit edilmiştir. Şiddet: orta düzey. Alt yapraklarda boğa gözü görünümlü koyu lekeler başlamış durumda.

## 2. Tedavi Seçenekleri
**Kimyasal:** Mankozeb veya Klorotalonil içerikli fungisit — 7-10 günde bir uygula.
**Organik/Doğal:** Nim yağı veya bakır sülfat çözeltisi — aynı aralıkta uygulayabilirsin.

## 3. Spreylama Zamanlaması
Hava şu an güneşli ve 26°C. Sabah 07:00-09:00 veya akşam 18:00 sonrası ilaçla. Rüzgar 12 km/s — ilaçlama için uygun. Yağmur beklenmiyorsa bugün başlayabilirsin.

## 4. Önleme
Gelecek sezon: alt yaprakları erken buda, damla sulama kullan ve aşırı azot gübrelemesinden kaçın.

**Özet:** Hemen Mankozeb ile ilaçlamaya başla, 10 gün sonra tekrarla — bu hastalık erken müdahaleyle kontrol altına alınabilir, cesaretini kaybetme!
"""

RECOMMENDATION_PROMPT_V3 = f"""Sen TarlAI'sin. Aşağıdaki format ve tona uyarak Türkçe tavsiye oluştur.

FORMAT ÖRNEĞİ:
{FEW_SHOT_EXAMPLE}

GERÇEK VERİLER:
- Teşhis: {json.dumps(diagnosis, ensure_ascii=False)}
- Hava: {json.dumps(weather, ensure_ascii=False)}
- Tedavi: {json.dumps(treatment, ensure_ascii=False)}

Aynı yapıyı kullanarak yukarıdaki verilere özgü tavsiye yaz."""
```

**Why it might help:** Few-shot locking produces extremely consistent output format across different diseases
**Tradeoff:** Long prompt (+300 tokens); example must be updated if output format changes

---

### Prompt 3 Comparison Table

| Version | Structure Consistency | Severity-Aware | Turkish Quality | Token Cost | Winner |
|---------|--------------------|----------------|-----------------|-----------|--------|
| V1 (current) | ★★☆☆☆ | ★☆☆☆☆ | ★★★☆☆ | Low | |
| **V2 (structured persona)** | **★★★★☆** | **★★★★★** | **★★★★☆** | **Medium** | **✓** |
| V3 (few-shot) | ★★★★★ | ★★★☆☆ | ★★★★★ | High | |

**Recommended:** V2 for production. V3 if strict output formatting is critical (e.g., parsing output downstream).

---

## Final Recommendations Summary

| Prompt | Current (V1) | Recommended | Key Improvement |
|--------|-------------|-------------|----------------|
| **P1 Diagnosis** | Minimal JSON | **V2 Schema-Explicit** | Consistent keys, edge case handling |
| **P2 Function Calling** | Hardcoded demo | **V2 Parameterized** | Reusable, triggers both tools |
| **P3 Recommendation** | Simple list | **V2 Severity-Aware** | Urgency tone, consistent structure, uses new disease data |

## Chain-of-Thought Decision

CoT (V3 for P1) is worth testing if:
- The target use case involves low-quality/blurry field photos
- Accuracy on ambiguous diseases matters more than response speed
- JSON extraction is handled robustly (regex with fallback)

For the current hackathon demo, V2 for all three prompts is the right call.

## System Prompt Decision

Gemma 4 E4B supports system prompts via `apply_chat_template`. Using a system prompt for Stage 3 (TarlAI persona) is a clean architecture. However, the current single-turn pipeline works well without it. Adding system prompts adds complexity without clear benefit for V2.

## JSON Schema Decision

For P1, V2 uses inline schema examples rather than a formal JSON Schema object. This is intentional — Gemma 4's function calling already uses JSON Schema for tool definitions; adding another schema format in a text prompt may confuse the model. Inline examples with `e.g.` annotations are sufficient.
