# TarlAI - AI-Powered Agricultural Assistant

> Multimodal plant disease diagnosis with weather-aware treatment recommendations using Google's Gemma 4

## Overview

TarlAI is an AI-powered agricultural assistant that helps Turkish farmers diagnose plant diseases from photos and receive actionable treatment recommendations. Built for the [Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good-hackathon) on Kaggle.

**Team:** Altug Ikiz, Arda Akinci, Simittin, Zeynep Yonca Ozel  
**Track:** Impact Track - Digital Equity & Inclusivity  
**University:** Akdeniz University, Computer Engineering

## How It Works

```
[Farmer takes photo] → [Gemma 4 Vision: diagnose disease]
                              ↓
                    [Function Calling: get_weather + get_treatment]
                              ↓
                    [Gemma 4: generate Turkish recommendation]
                              ↓
                    [Farmer receives actionable advice]
```

### Three-Stage Pipeline

1. **Vision Analysis** - Gemma 4 E4B analyzes the plant photo to identify species, disease, and severity
2. **Agentic Tool Use** - Model autonomously calls weather API and treatment database using native function calling
3. **Recommendation** - Synthesizes all data into a comprehensive Turkish-language treatment plan

## Technical Stack

| Component | Details |
|-----------|---------|
| Model | Gemma 4 E4B-IT (~4B effective parameters) |
| Framework | Hugging Face Transformers |
| Inference | GPU T4 x2 on Kaggle |
| Vision | Native multimodal image encoding |
| Function Calling | Native special tokens |
| Language | Turkish (140+ language support) |

## Quick Start

### Run on Kaggle (Recommended)

1. Open the [Kaggle Notebook](https://www.kaggle.com/code/altugikiz/notebook19edf1be11)
2. Ensure GPU T4 x2 is selected
3. Run all cells
4. Call `tarlai_analyze("path/to/plant_image.jpg", "Antalya")`

### Run Locally

```bash
# Requirements
pip install transformers accelerate torch pillow

# Download Gemma 4 E4B-IT from Hugging Face
# Requires ~8GB VRAM
```

## Project Structure

```
TarlAI/
├── README.md
├── tarlai_notebook.py      # Main notebook code
├── tarlai_tools.py         # Weather API and treatment database
├── report/
│   └── TarlAI_Technical_Report.docx
└── demo/
    └── sample_output.md    # Sample analysis output
```

## Sample Output

```
>> Location: Antalya
>> Plant: grape
>> Disease: Powdery mildew or leaf spot disease (likely fungal)
>> Severity: moderate
>> Weather: Sunny, 26C

TARLAI - ANALYSIS REPORT
==================================================
Merhaba ciftci kardesim, ben TarlAI. Tarim danismanlik hizmetinizdeyim.

1. Tespit Edilen Sorun: Yaprak Lekesi (mantar kaynakli enfeksiyon)
2. Tedavi: Bakir bazli fungisitler veya Mankozeb (7-14 gunde bir)
3. Organik: Bordeaux karisimi veya Neem yagi
4. Zamanlama: Hava gunesli - sabah erken veya aksam ust ilaclayin
5. Onleme: Havalandirma, damla sulama, hastalikli yapraklari budayin
```

## Gemma 4 Features Used

- **Multimodal Vision** - Native image understanding without separate CV model
- **Native Function Calling** - Special tokens for deterministic tool use
- **Multilingual** - Fluent Turkish with correct agricultural terminology
- **Edge-Deployable** - E4B model suitable for mobile/offline deployment

## Future Plans

- Real-time OpenWeatherMap API integration
- Expanded disease database (50+ Turkish crop diseases)
- Fine-tuning with Unsloth on Turkish agricultural data
- Android app via LiteRT for offline operation

## License

Apache 2.0

## Acknowledgments

- Google DeepMind for Gemma 4
- Kaggle for the Gemma 4 Good Hackathon platform
- Akdeniz University, Department of Computer Engineering