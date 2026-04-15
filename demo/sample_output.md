# TarlAI - Sample Analysis Output

## Input
- **Image:** Grape leaf with brown spots and lesions
- **Location:** Antalya, Turkey

## Pipeline Output

```
>> Location: Antalya
>> Diagnosing with Gemma 4...

>> Plant: grape
>> Disease: Powdery mildew or leaf spot disease (likely fungal)
>> Severity: moderate
>> Weather: Sunny, 26C

>> Generating recommendation...

==================================================
TARLAI - ANALYSIS REPORT
==================================================
Merhaba ciftci kardesim, ben TarlAI. Tarim danismanlik hizmetinizdeyim.

Goruntudeki yapraklardan yola cikarak uzum agacinizda yaprak lekesi hastaligi
(mantar kaynakli bir sorun) tespit edilmis durumda. Hastaligin siddeti orta duzeyde.

### 1. Tespit Edilen Sorun
- Hastalik: Yaprak Lekesi (mantar kaynakli enfeksiyon)
- Belirti: Yapraklarda kahverengi, lekeli ve lezyonlar olusuyor

### 2. Tedavi Secenekleri

A. Kimyasal Tedavi:
- Ilaclar: Bakir bazli fungisitler veya Mankozeb iceren ilaclar
- Uygulama: 7-14 gunde bir duzenli araliklarla

B. Organik Tedavi:
- Karisimlar: Bordeaux karisimi veya Neem yagi
- Uygulama: 7-14 gunde bir duzeli araliklarla

### 3. Hava Kosullarina Gore Sprey Zamanlamasi
Mevcut hava kosullari: Antalya, 26C, %72 Nem, %15 Yagmur, Gunesli

- Ruzgar hafif, ilaclama icin uygun
- Sabah erken saatleri veya aksam ustu tercih edin
- Gunes en tepedeyken ilaclama yapmayin

### 4. Hastalik Onleme Yollari
1. Budama ve Havalandirma: Hava akisini artirin
2. Temizlik: Hastalikli yapraklari temizleyin
3. Sulama Yonetimi: Damla sulama tercih edin
4. Ilaclama Takvimi: Onleyici ilaclama programi uygulayin

Ozetle: Hemen fungisit veya neem yagi ile tedaviye baslayin.
Basarilar dilerim!
==================================================
```

## Function Calling Output

Gemma 4 autonomously generated these tool calls:

```
<|tool_call>call:get_weather{location:"Antalya"}<tool_call|>
<|tool_call>call:get_treatment{disease_name:"leaf_spot"}<tool_call|>
```

### Weather API Response
```json
{
  "location": "Antalya",
  "temp": 26,
  "humidity": 72,
  "rain_pct": 15,
  "wind_kmh": 12,
  "condition": "Sunny"
}
```

### Treatment Database Response
```json
{
  "name": "Leaf Spot",
  "chemical": "Copper-based fungicide, Mancozeb",
  "organic": "Bordeaux mixture, Neem oil",
  "interval": "7-14 days"
}
```