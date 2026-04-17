"""
TarlAI Hastalık Veritabanı
Türkiye'de yaygın bitki hastalıkları için tedavi ve önleme bilgileri.

Kaynaklar:
- T.C. Tarım ve Orman Bakanlığı (tarim.gov.tr)
- Antalya Tarım İl Müdürlüğü yayınları
- FAO Plant Disease Management kılavuzları
- Türkiye Ziraat Fakülteleri ders materyalleri
"""

DISEASE_DB = {

    # ─────────────────────────────────────────────
    # GENEL / YAYGINN FUNGAL HASTALIKLAR
    # ─────────────────────────────────────────────

    "leaf_spot": {
        "name": "Leaf Spot (Yaprak Lekesi)",
        "affected_plants": ["tomato", "pepper", "eggplant", "cucumber", "bean", "strawberry"],
        "symptoms": "Yapraklar üzerinde kahverengi veya siyah dairesel lekeler oluşur. Lekeler büyüyerek birleşebilir ve yaprak dökülmesine neden olabilir.",
        "chemical": "Bakır bazlı fungisit, Mankozeb, Klorotalonil",
        "organic": "Bordo bulamacı, Nim yağı",
        "interval": "7-14 gün",
        "severity_indicators": {
            "mild": "Birkaç yaprakta küçük, izole lekeler; bitkinin %10'undan azı etkilenmiş.",
            "moderate": "Birden fazla yaprak katmanında yaygın lekeler; bitkinin %10-30'u etkilenmiş.",
            "severe": "Yapraklarda yaygın nekroz ve erken döküm; bitkinin %30'undan fazlası etkilenmiş."
        },
        "prevention": "Damla sulama kullan, yaprakları ıslatma. Bitki artıklarını temizle. Rotasyon uygula. Hava sirkülasyonunu artır.",
        "notes": "Tepe sulamasından kaçın. Sulama sabah erken yapılmalı ki yapraklar gün içinde kuruyabilsin."
    },

    "early_blight": {
        "name": "Early Blight (Erken Yanıklık - Alternaria)",
        "affected_plants": ["tomato", "potato", "eggplant"],
        "symptoms": "Yapraklarda koyu kahverengi, konsantrik halkalar içeren 'boğa gözü' görünümünde lekeler. Alt yapraklardan başlar ve yukarı yayılır.",
        "chemical": "Mankozeb, Klorotalonil, Azoksistrobin",
        "organic": "Nim yağı, Bakır sülfat çözeltisi",
        "interval": "7-10 gün",
        "severity_indicators": {
            "mild": "Alt yapraklarda 1-3 leke; sarılık henüz yok.",
            "moderate": "Alt ve orta yapraklarda çok sayıda leke, sarılık ve erken döküm başlamış.",
            "severe": "Bitkinin alt yarısında yaprak dökümü, meyvelerde de lezyonlar görülüyor."
        },
        "prevention": "Sermahe dirençli çeşitler seç. Bitki artıklarını tarladan uzaklaştır. Aşırı azot gübresinden kaçın. 2-3 yıllık ekim nöbeti uygula.",
        "notes": "Sabah erken veya akşam geç saatlerde ilaçlama yapın. Yüksek nemde hastalık hızla yayılır."
    },

    "late_blight": {
        "name": "Late Blight (Geç Yanıklık - Phytophthora)",
        "affected_plants": ["tomato", "potato"],
        "symptoms": "Yapraklarda su emmiş görünümlü, gri-yeşil lekeler; arkasında beyaz küflenme. Saplar ve meyveler de etkilenir. Çok hızlı yayılır.",
        "chemical": "Metalaksil, Bordo bulamacı, Dimetomorf, Fosetil-Al",
        "organic": "Bordo bulamacı (bakır bazlı)",
        "interval": "5-7 gün",
        "severity_indicators": {
            "mild": "Birkaç yaprakta su emmiş lekeler, henüz küflenme yok.",
            "moderate": "Birden fazla yaprakta gri lekeler ve alt yüzeyde beyaz küf; saplar etkileniyor.",
            "severe": "Bitkide hızlı çürüme, sap lezyonları, meyvede kahverengi çürüme; tüm bitki tehlikede."
        },
        "prevention": "Sertifikalı, sağlıklı fide/tohum kullan. Sulama suyunu kontrol et. Yüksek nem dönemlerinde koruyucu ilaçlama yap. Etkilenen bitkileri derhal uzaklaştır.",
        "notes": "Enfeksiyonlu yaprakları hemen uzaklaştırın. Serin ve nemli havalarda çok agresif yayılır. İrlanda patates kıtlığına yol açan hastalıktır."
    },

    "powdery_mildew": {
        "name": "Powdery Mildew (Külleme)",
        "affected_plants": ["cucumber", "zucchini", "grape", "strawberry", "pepper", "tomato", "apple"],
        "symptoms": "Yaprak yüzeyinde beyaz, un gibi pudra görünümlü fungal örtü. Yapraklar sararır ve kıvrılır. Meyve kalitesi düşer.",
        "chemical": "Kükürt bazlı fungisit, Mikobutanil, Tebukonazol",
        "organic": "Süt-su karışımı (%40 süt), Karbonat çözeltisi (1 çay kaşığı/1L su), Bitkisel yağ emülsiyonu",
        "interval": "7 gün",
        "severity_indicators": {
            "mild": "Birkaç yaprakta küçük beyaz lekeler; bitkinin %5'inden azı etkilenmiş.",
            "moderate": "Yaprakların büyük bölümünde beyaz örtü, hafif sararma; bitkinin %5-30'u etkilenmiş.",
            "severe": "Tüm yaprak yüzeyinde yoğun küf örtüsü, yaprak kıvrılması ve erken döküm."
        },
        "prevention": "Bitkilerin arasında yeterli mesafe bırak. Aşırı azot gübrelemesinden kaçın. Dirençli çeşitler kullan. Sabah sulama yap.",
        "notes": "Hava sirkülasyonunu artır. Diğer fungal hastalıkların aksine kuru havalarda da gelişebilir."
    },

    "downy_mildew": {
        "name": "Downy Mildew (Mildiyö)",
        "affected_plants": ["cucumber", "grape", "onion", "lettuce", "spinach", "pepper"],
        "symptoms": "Yaprak üst yüzeyinde sarı-yeşil lekeler, alt yüzeyde gri-mor tüylü küf oluşumu. Yüksek nem ve serin hava koşullarında hızla yayılır.",
        "chemical": "Metalaksil, Fosetil-Al, Mankozeb, Dimetomorf",
        "organic": "Bakır hidroksit, Bakır oksiklorür",
        "interval": "7-10 gün",
        "severity_indicators": {
            "mild": "Birkaç yaprakta sarı lekeler; alt yüzeyde küf henüz yok.",
            "moderate": "Birden fazla yaprakta sarı-kahverengi lekeler ve alt yüzeyde küf örtüsü.",
            "severe": "Yaygın yaprak dökümü, tüm bitkide yayılmış enfeksiyon, meyve tutumu bozulmuş."
        },
        "prevention": "Yüksek nem dönemlerinde koruyucu ilaçlama uygula. İyi drenaj sağla. Sabah sulama yap. Yaprakları nemlendirmekten kaçın.",
        "notes": "İyi drenaj sağla. Serin ve yağışlı havalarda çok hızlı yayılır."
    },

    "rust": {
        "name": "Rust (Pas Hastalığı)",
        "affected_plants": ["wheat", "bean", "corn", "rose", "apple", "pear", "garlic", "onion"],
        "symptoms": "Yaprak alt yüzeyinde turuncu-kahverengi toz halinde spor yığınları (pustüller). Şiddetli enfeksiyonda yaprak sararır ve kurur.",
        "chemical": "Triadimefon, Propikonazol, Tebukonazol",
        "organic": "Kükürt tozu, Nim yağı, Sarımsak infüzyonu",
        "interval": "7-14 gün",
        "severity_indicators": {
            "mild": "Birkaç yaprakta izole turuncu lekeler; spor yığınları henüz küçük.",
            "moderate": "Birden fazla yaprakta yoğun spor yığınları; sararma başlamış.",
            "severe": "Yaygın sararma ve kuruma; verim ciddi şekilde etkilenmiş."
        },
        "prevention": "Dirençli çeşitler kullan. Bitki artıklarını tarladan uzaklaştır. Aşırı azot gübresinden kaçın. Ekim nöbeti uygula.",
        "notes": "Enfeksiyon görmüş bitki artıklarını yakarak imha et. Rüzgarla çok hızlı yayılır."
    },

    "anthracnose": {
        "name": "Anthracnose (Antraknoz)",
        "affected_plants": ["pepper", "tomato", "cucumber", "bean", "strawberry", "mango", "grape"],
        "symptoms": "Yaprak, meyve ve saplarda koyu kahverengi-siyah batık lekeler. Meyvede çürüme. Islak havalarda pembe-turuncu spor kütlesi oluşur.",
        "chemical": "Klorotalonil, Bakır fungisit, Azoksistrobin, Mankozeb",
        "organic": "Bordo bulamacı",
        "interval": "7-10 gün",
        "severity_indicators": {
            "mild": "Birkaç yaprak veya meyvede küçük lekeler; batık lezyonlar henüz yok.",
            "moderate": "Birden fazla meyve veya yaprakta batık lekeler; ürün kaybı başlamış.",
            "severe": "Yaygın meyve çürümesi; hasat öncesi ve sonrası ciddi kayıp."
        },
        "prevention": "Hasatta zedelenmelerden kaçın. Sera/depo havalandırmasını artır. Dirençli çeşit kullan. Bitki artıklarını temizle.",
        "notes": "Islak bitkilerle çalışmaktan kaçın. Hasat sonrası depolama koşullarına dikkat edin."
    },

    "bacterial_spot": {
        "name": "Bacterial Spot (Bakteriyel Leke - Xanthomonas)",
        "affected_plants": ["tomato", "pepper"],
        "symptoms": "Yapraklarda küçük, su emmiş görünümlü lekeler, sonra kahverengi-siyaha döner. Meyve yüzeyinde kabarık, sert lekeler oluşur. Rüzgar ve yağmurla yayılır.",
        "chemical": "Bakır bazlı bakterisit, Bakır hidroksit + Mankozeb kombinasyonu",
        "organic": "Bakır hidroksit spreyi",
        "interval": "5-7 gün",
        "severity_indicators": {
            "mild": "Birkaç yaprakta su emmiş lekeler; meyvelerde henüz leke yok.",
            "moderate": "Birden fazla yaprakta yayılmış lekeler, yaprak dökümü başlamış; bazı meyvelerde leke.",
            "severe": "Ağır yaprak dökümü, meyvelerin büyük bölümünde leke; ticari değer düşmüş."
        },
        "prevention": "Sertifikalı, hastalıksız tohum kullan. Tepe sulamadan kaçın. Bitkiler ıslakken çalışmaktan kaçın. 2-3 yıl ekim nöbeti uygula.",
        "notes": "Bir kez yerleşti mi kimyasal çare yoktur, önlemeye odaklan. Bakır direnci gelişebilir, rotasyon yap."
    },

    "mosaic_virus": {
        "name": "Mosaic Virus (Mozaik Virüsü)",
        "affected_plants": ["tomato", "pepper", "cucumber", "zucchini", "bean", "tobacco"],
        "symptoms": "Yapraklarda açık-koyu yeşil mozaik görünüm, kıvrılma, kabarcıklanma. Bitki büyümesi durur, meyveler küçük ve şekil bozuk kalır.",
        "chemical": "Kimyasal tedavi mevcut değil",
        "organic": "Enfeksiyon görmüş bitkileri çıkarıp imha et. Böcek vektörlerini kontrol et (yaprak biti).",
        "interval": "Yok (önleme odaklı)",
        "severity_indicators": {
            "mild": "Birkaç yaprakta hafif mozaik renk değişimi; büyüme normal seyrediyor.",
            "moderate": "Yaygın mozaik ve kıvrılma; bitki büyümesi yavaşlamış, meyveler küçük.",
            "severe": "Tüm bitkide yayılmış semptomlar; ciddi verim kaybı, bitki imhası gerekebilir."
        },
        "prevention": "Yaprak bitlerine ve diğer böcek vektörlerine karşı mücadele et. Dirençli çeşit kullan. Enfeksiyon görmüş bitkilere dokunan aletleri dezenfekte et. Yabancı otları temizle.",
        "notes": "Yaprak biti vektörlerini kontrol et, dirençli çeşit kullan. Sigara ve tütün kullananlar bitkiye dokunmadan önce ellerini yıkamalı (TMV)."
    },

    "root_rot": {
        "name": "Root Rot (Kök Çürüklüğü - Pythium/Phytophthora)",
        "affected_plants": ["tomato", "pepper", "cucumber", "citrus", "avocado", "bean", "strawberry"],
        "symptoms": "Kökler kahverengiye dönüp çürür, bitki solup sararır ve solar. Toprak seviyesinde sap da etkilenebilir. Aşırı sulama ve ağır toprak koşullarında yaygın.",
        "chemical": "Metalaksil toprak uygulaması, Fosetil-Al",
        "organic": "Drenajı iyileştir, sulamayı azalt. Trichoderma içerikli biyolojik preparatlar.",
        "interval": "14-21 gün",
        "severity_indicators": {
            "mild": "Hafif sararma ve büyüme yavaşlaması; kökler kısmen etkilenmiş.",
            "moderate": "Belirgin solgunluk ve sararma; köklerın büyük bölümü kahverengi ve çürümüş.",
            "severe": "Bitki geri dönüşü olmayan solgunluk; kök sistemi tamamen çökmüş."
        },
        "prevention": "Aşırı sulamadan kaçın. İyi drene olan toprak kullan. Yükseltilmiş tarhlar veya drenaj kanalları oluştur. Steril yetiştirme ortamı kullan.",
        "notes": "Su baskını koşullarından kaçın. Saksı bitkilerinde iyi delikli saksı kullan."
    },

    # ─────────────────────────────────────────────
    # DOMATES HASTALIKLARI
    # ─────────────────────────────────────────────

    "septoria_leaf_spot": {
        "name": "Septoria Leaf Spot (Septorya Yaprak Lekesi)",
        "affected_plants": ["tomato"],
        "symptoms": "Alt yapraklarda ortası açık renkli, etrafı koyu kahverengi halkalarla çevrili küçük yuvarlak lekeler. Leke içinde siyah mikroskobik spor yuvaları görülür.",
        "chemical": "Mankozeb, Klorotalonil, Bakır fungisit",
        "organic": "Bordo bulamacı, Bakır oksiklorür",
        "interval": "7-10 gün",
        "severity_indicators": {
            "mild": "Alt yapraklarda birkaç leke; sararma henüz yok.",
            "moderate": "Alt ve orta yapraklarda yaygın lekeler; sararma ve erken döküm başlamış.",
            "severe": "Bitkinin alt yarısında tamamen dökülmüş yapraklar; üst yapraklara yayılmış."
        },
        "prevention": "Bitki artıklarını tarladan temizle. Damla sulama kullan. 2 yıl ekim nöbeti uygula. Alt yaprakları budayarak hava sirkülasyonunu artır.",
        "notes": "Alt yaprakları düzenli kontrol et, erken tespitte büyük önem taşır. Enfeksiyonun üst yapraklara yayılmasını önle."
    },

    "tomato_mosaic_virus": {
        "name": "Tomato Mosaic Virus - ToMV (Domates Mozaik Virüsü)",
        "affected_plants": ["tomato", "pepper", "eggplant"],
        "symptoms": "Yapraklarda açık ve koyu yeşil mozaik deseni, kıvrılma ve kabarcıklanma. Meyveler küçük kalır, sap rengi açılır. Temas yoluyla çok kolay bulaşır.",
        "chemical": "Kimyasal tedavi mevcut değil",
        "organic": "Enfeksiyon görmüş bitkileri çıkarıp uzaklaştır. Aletleri %10 çamaşır suyuyla dezenfekte et.",
        "interval": "Yok (önleme odaklı)",
        "severity_indicators": {
            "mild": "Birkaç yaprakta hafif renk değişimi; büyüme normal.",
            "moderate": "Yaygın mozaik ve kıvrılma; büyüme yavaşlamış.",
            "severe": "Tüm bitki etkilenmiş; ciddi verim kaybı, bitki imhası gerekiyor."
        },
        "prevention": "ToMV dirençli çeşit kullan. Fide yetiştiriciliğinde titiz hijyen uygula. Tütün kullanıcıları ellerini yıkamalı. Aletleri sterilize et.",
        "notes": "Temas yoluyla çok kolay bulaşır. Fide yetiştirmede titiz hijyen uygula."
    },

    "fusarium_wilt": {
        "name": "Fusarium Wilt (Fusarium Solgunluğu)",
        "affected_plants": ["tomato", "pepper", "eggplant", "cucumber", "watermelon", "melon", "banana"],
        "symptoms": "Bir taraflı solgunluk ile başlar, bitkinin bir yanı önce solar. Sap enine kesildiğinde iletim dokusunda kahverengi renk değişimi görülür. Sonunda tüm bitki solar ve ölür.",
        "chemical": "Fungisit toprağa karıştırma (Benomil, Karbendazim). Not: Etkisi sınırlı, önleme esastır.",
        "organic": "Dirençli anaç üzerine aşılı fide. Trichoderma içerikli biyolojik preparatlar. Toprak solarizasyonu.",
        "interval": "Önleme aşamasında",
        "severity_indicators": {
            "mild": "Tek taraflı hafif solgunluk; akşamları toparlanıyor.",
            "moderate": "Kalıcı tek taraflı solgunluk; sap kesitinde renk değişimi var.",
            "severe": "Tüm bitkide solma ve ölüm; fideler hızla ölüyor."
        },
        "prevention": "Fusarium dirençli çeşit veya aşılı fide kullan. Toprak solarizasyonu uygula (temmuz-ağustos). Enfeksiyon görmüş toprakta aynı familyadan bitki ekme. Drenajı iyileştir.",
        "notes": "Toprakta yıllarca canlı kalır. Toprak solarizasyonu en etkili önlemdir. Aşılı fide kullanımı çok önemlidir."
    },

    "verticillium_wilt": {
        "name": "Verticillium Wilt (Verticillium Solgunluğu)",
        "affected_plants": ["tomato", "pepper", "eggplant", "strawberry", "potato", "olive"],
        "symptoms": "Alt yapraklardan başlayan sararma ve solgunluk. Yapraklarda V şeklinde sarı lekeler karakteristiktir. Sap kesitinde kahverengi renk değişimi. Fusarium'dan daha yavaş ilerler.",
        "chemical": "Toprağa fungisit karıştırma (sınırlı etki). Karbendazim.",
        "organic": "Toprak solarizasyonu. Biyolojik kontrol (Trichoderma spp.).",
        "interval": "Önleme aşamasında",
        "severity_indicators": {
            "mild": "Alt yapraklarda hafif sararma; bitki henüz normal büyüyor.",
            "moderate": "Belirgin V şeklinde lekeler ve solgunluk; büyüme yavaşlamış.",
            "severe": "Yaygın yaprak dökümü ve bitki ölümü; verim tamamen yok."
        },
        "prevention": "Dirençli çeşit kullan. Toprak solarizasyonu uygula. Hassas bitkilerle ekim nöbetini 4-5 yıla çıkar. Enfeksiyon görmüş bitki artıklarını yak.",
        "notes": "Toprakta uzun süre canlı kalır. Serin toprak sıcaklığında daha aktiftir (15-25°C)."
    },

    "blossom_end_rot": {
        "name": "Blossom End Rot (Çiçek Ucu Çürüklüğü)",
        "affected_plants": ["tomato", "pepper", "zucchini", "watermelon", "eggplant"],
        "symptoms": "Meyvenin çiçek ucunda (alt kısmında) su emmiş görünümlü koyu leke, sonra kuruyup sertleşir ve siyahlaşır. Fungal bir hastalık değil, kalsiyum eksikliğidir.",
        "chemical": "Kalsiyum klorür foliar spreyi (%0.5-1)",
        "organic": "Kalsiyum nitrat yaprak gübresi. Düzenli sulama programı. Kireç toprağa karıştırma.",
        "interval": "10-14 gün (önleyici olarak)",
        "severity_indicators": {
            "mild": "Birkaç meyvede küçük, açık renkli leke; henüz sertleşmemiş.",
            "moderate": "Birden fazla meyvede belirgin koyu leke; ticari değer düşmüş.",
            "severe": "Ürünün büyük bölümünde hasarlı meyveler; ciddi verim kaybı."
        },
        "prevention": "Düzenli ve eşit sulama yap (kuraklık-taşkın döngüsünden kaçın). Aşırı azot gübrelemesinden kaçın. Toprak pH'ını 6.5-7.0 arasında tut. Mulch kullan.",
        "notes": "Fungal değil fizyolojik bir bozukluktur; kalsiyumun meyveye taşınamamasından kaynaklanır. Düzenli sulama en önemli önlemdir."
    },

    # ─────────────────────────────────────────────
    # BİBER HASTALIKLARI
    # ─────────────────────────────────────────────

    "pepper_anthracnose": {
        "name": "Pepper Anthracnose (Biber Antraknoz - Colletotrichum)",
        "affected_plants": ["pepper"],
        "symptoms": "Olgunlaşmakta olan ve olgun meyvelerde koyu kahverengi-siyah batık lekeler. Islak havalarda leke üzerinde pembe-turuncu spor kütlesi oluşur. Meyve çürümesine yol açar.",
        "chemical": "Azoksistrobin, Mankozeb, Klorotalonil",
        "organic": "Bordo bulamacı, Bakır oksiklorür",
        "interval": "7-10 gün",
        "severity_indicators": {
            "mild": "Birkaç meyvede küçük batık lekeler; pembe spor kütlesi henüz yok.",
            "moderate": "Birden fazla meyvede yaygın batık lekeler ve spor oluşumu.",
            "severe": "Meyvelerin büyük bölümünde çürüme; hasat öncesi ciddi kayıp."
        },
        "prevention": "Dirençli çeşit kullan. Biber meyvelerini hasatta zedelemekten kaçın. Sera havalandırmasını artır. Bitki artıklarını temizle.",
        "notes": "Özellikle kırmızı biberde hasat öncesi ciddi sorun oluşturur. Depolama sırasında da yayılabilir."
    },

    "pepper_mosaic_virus": {
        "name": "Pepper Mosaic Virus - PeMV (Biber Mozaik Virüsü)",
        "affected_plants": ["pepper", "tomato"],
        "symptoms": "Yapraklarda sarı-yeşil mozaik desen, kıvrılma ve kabarcıklanma. Bitki bodur kalır. Meyveler küçük, şekil bozuk ve sararabilir.",
        "chemical": "Kimyasal tedavi mevcut değil",
        "organic": "Enfeksiyon görmüş bitkileri çıkar. Yaprak biti vektörlerini insektisit ile kontrol et.",
        "interval": "Yok (önleme odaklı)",
        "severity_indicators": {
            "mild": "Birkaç yaprakta hafif mozaik; büyüme normal.",
            "moderate": "Yaygın mozaik ve kıvrılma; meyveler küçük kalıyor.",
            "severe": "Tüm bitki etkilenmiş; ticari üretim mümkün değil."
        },
        "prevention": "Yaprak bitlerine karşı insektisit uygula (sarı yapışkan tuzak kullan). Dirençli çeşit kullan. Yabancı otları temizle (rezervuar konakçı).",
        "notes": "Yaprak bitleri başlıca taşıyıcıdır. Sarı yapışkan tuzaklar erken uyarı için kullanılabilir."
    },

    # ─────────────────────────────────────────────
    # ÜZÜM HASTALIKLARI
    # ─────────────────────────────────────────────

    "grape_black_rot": {
        "name": "Grape Black Rot (Üzüm Kara Leke - Guignardia)",
        "affected_plants": ["grape"],
        "symptoms": "Yapraklarda küçük sarı-kahverengi lekeler, kenarlarda siyah nokta halinde sporlar. Meyveler önce kahverengiye döner, sonra mumyalaşır. Meyve kayıpları çok yüksek olabilir.",
        "chemical": "Mankozeb, Mikobutanil, Klorotalonil",
        "organic": "Bordo bulamacı (tomurcuk kabarması döneminden itibaren)",
        "interval": "10-14 gün (özellikle yağmurdan sonra)",
        "severity_indicators": {
            "mild": "Birkaç yaprakta küçük lekeler; meyvelerde henüz belirti yok.",
            "moderate": "Yapraklarda yaygın lekeler ve bazı meyvelerde kahverengi renk değişimi.",
            "severe": "Meyvelerin büyük bölümü mumyalaşmış; verim ciddi düşmüş."
        },
        "prevention": "Mumyalaşmış meyveleri ve enfeksiyon görmüş sürgünleri kış budamasında uzaklaştır. Asma altlarını temizle. İyi havalanma sağla. Tomurcuk kabarmasından itibaren ilaçlama programı başlat.",
        "notes": "Tomurcuk kabarmasından çiçeklenme sonrasına kadar kritik dönemdir. Kış budamasında enfeksiyonlu sürgünleri temizlemek şarttır."
    },

    "grape_phylloxera": {
        "name": "Grape Phylloxera (Bağ Filokserası - Daktulosphaira vitifoliae)",
        "affected_plants": ["grape"],
        "symptoms": "Köklerde şişkinlik (nodositeler), büyüme yavaşlaması, yaprak sararması, giderek azalan verim. Toprak altında yaşadığı için görülmesi zordur. Bağın ölümüne yol açar.",
        "chemical": "Kök enjeksiyonu (sınırlı etki). Kimyasal mücadele pratikte zordur.",
        "organic": "Filoksera toleranslı/dirençli anaç üzerine aşılama (en etkili yöntem).",
        "interval": "Sürekli izleme gerekir",
        "severity_indicators": {
            "mild": "Bazı bölgelerde hafif büyüme yavaşlaması; kökler az etkilenmiş.",
            "moderate": "Belirgin verim düşüşü ve yaprak sararması; köklerde yaygın nodositeler.",
            "severe": "Bağın büyük bölümünde ciddi verim kaybı veya bitki ölümü."
        },
        "prevention": "Dirençli anaç üzerine aşılı fide kullan (V. berlandieri x V. riparia anaçları). Filoksera bulunan bölgelerden toprak taşıma. Budama ve hasat aletlerini dezenfekte et.",
        "notes": "Türkiye'nin bazı bölgelerinde yaygın. En etkili çözüm dirençli anaç kullanımıdır. 19. yüzyılda Avrupa bağlarını mahveden haşeredir."
    },

    "grape_esca": {
        "name": "Grape Esca / Wood Disease (Üzüm Kav Hastalığı)",
        "affected_plants": ["grape"],
        "symptoms": "Yapraklarda şeritler halinde sararma ve kurumayla 'kaplan derisi' görünümü. Saplarda su emmiş görünümlü lekeler. Odun dokusunda kahverengi çürüme. Ani solma (apoplexy) görülebilir.",
        "chemical": "Budama yaralarına Trichoderma içerikli koruyucu macun uygula. Etkili kimyasal tedavi sınırlıdır.",
        "organic": "Budama yaralarını koruyucu macunla kapat. Budama artıklarını yakarak imha et.",
        "interval": "Yıllık budama sonrası koruyucu uygulama",
        "severity_indicators": {
            "mild": "Birkaç yaprakta kaplan derisi belirtisi; odunda henüz ciddi çürüme yok.",
            "moderate": "Birden fazla sürgünde belirtiler; verim düşmüş.",
            "severe": "Ani solma ve odun çürümesi yaygın; bağın büyük bölümü etkilenmiş."
        },
        "prevention": "Budama aletlerini dezenfekte et. Budama yaralarına hemen koruyucu macun uygula. Kış budamasını kuru havalarda yap. Stres faktörlerini (kuraklık, aşırı yük) azalt.",
        "notes": "Budama yaralarından giren funguslar neden olur. Yaraları hemen kapat. Asmanın yaşlı kısımlarında daha yaygın."
    },

    # ─────────────────────────────────────────────
    # TURUNÇGİL HASTALIKLARI (Antalya için kritik)
    # ─────────────────────────────────────────────

    "citrus_greening": {
        "name": "Citrus Greening / HLB (Turunçgil Yeşillenme Hastalığı - Huanglongbing)",
        "affected_plants": ["orange", "lemon", "mandarin", "grapefruit", "citrus"],
        "symptoms": "Yapraklarda asimetrik (tek taraflı) sararma (blotchy mottle). Meyveler küçük, şekil bozuk, acı ve tuzlu; tohumlar siyahlaşır. Ağaç giderek zayıflar ve ölür.",
        "chemical": "Kimyasal tedavi yok (bakteri kaynaklı). Psyllid vektörüne karşı insektisit (İmidakloprid, Spirotetramat).",
        "organic": "Vektör böceği (Diaphorina citri) kontrolü. Enfeksiyon görmüş ağaçları söküp imha et.",
        "interval": "Sürekli vektör izleme ve mücadelesi",
        "severity_indicators": {
            "mild": "Birkaç dalda asimetrik sararma; meyve kalitesi hafif düşmüş.",
            "moderate": "Ağacın büyük bölümünde belirtiler; meyveler küçük ve şekil bozuk.",
            "severe": "Tüm ağaç etkilenmiş; ekonomik üretim mümkün değil, ağaç ölüme gidiyor."
        },
        "prevention": "Sertifikalı, sağlıklı fide kullan. Psyllid böceğini düzenli takip et ve mücadele et. Enfeksiyon görmüş ağaçları hemen söküp imha et. Karantina önlemlerine uy.",
        "notes": "Türkiye'de karantina altındaki zararlı. Antalya bölgesinde büyük tehdit. Etkilenen ağaçları derhal ihbar et ve söküp yak."
    },

    "citrus_canker": {
        "name": "Citrus Canker (Turunçgil Bakteriyel Kanseri - Xanthomonas axonopodis)",
        "affected_plants": ["lemon", "orange", "grapefruit", "mandarin", "citrus"],
        "symptoms": "Yaprak, meyve ve saplarda kabarık, mantarca dokulu, sarı halkayla çevrili kahverengi lekeler. Meyve pazarlama değeri düşer. Şiddetli vakalarda yaprak ve meyve dökülmesi.",
        "chemical": "Bakır bazlı bakterisit, Bakır hidroksit",
        "organic": "Bakır oksiklorür spreyi",
        "interval": "14-21 gün (özellikle yağmurlu dönemde)",
        "severity_indicators": {
            "mild": "Birkaç yaprakta küçük lekeler; meyvelerde henüz belirti yok.",
            "moderate": "Yaprak ve meyvelerde yaygın lekeler; ürün kalitesi düşmüş.",
            "severe": "Ağır yaprak ve meyve dökümü; ihracat kalitesinde ciddi kayıp."
        },
        "prevention": "Sertifikalı hastalıksız fide kullan. Rüzgarı kıran şeritler oluştur. Enfeksiyon görmüş yaprak ve dalları budayıp yak. Bölgeden bölgeye taşımadan kaçın.",
        "notes": "Rüzgar ve yağmurla yayılır. Fırtına sonrasında ilaçlama mutlaka yapılmalıdır."
    },

    "citrus_scab": {
        "name": "Citrus Scab (Turunçgil Uyuz Hastalığı - Elsinoe fawcettii)",
        "affected_plants": ["lemon", "mandarin", "citrus"],
        "symptoms": "Genç yaprak ve meyvelerde pembe-gri renkli siğil benzeri kabarcıklar. Meyve yüzeyinde pürüzlü, mantarca görünümlü lekeler. İhracat kalitesini ciddi düşürür.",
        "chemical": "Mankozeb, Klorotalonil, Bakır fungisit",
        "organic": "Bordo bulamacı",
        "interval": "10-14 gün (özellikle yeni sürgün döneminde)",
        "severity_indicators": {
            "mild": "Birkaç yaprakta hafif kabarcık; meyvelerde henüz belirti yok.",
            "moderate": "Meyve yüzeyinde belirgin pürüzlü lekeler; görsel kalite düşmüş.",
            "severe": "Meyvelerin büyük bölümü etkilenmiş; ihracat standartlarını karşılamıyor."
        },
        "prevention": "Yeni sürgün döneminde koruyucu ilaçlama yap. Bahçe hijyenini koru. Aşırı sulama ve gübrelemeden kaçın.",
        "notes": "Limon ve mandarinde daha yaygın. Yeni sürgün ve çiçeklenme dönemlerinde kritik dönemdir."
    },

    "citrus_black_spot": {
        "name": "Citrus Black Spot (Turunçgil Siyah Leke - Phyllosticta citricarpa)",
        "affected_plants": ["orange", "lemon", "mandarin", "grapefruit", "citrus"],
        "symptoms": "Olgunlaşmakta olan meyvelerde önce kırmızı-kahverengi nokta, sonra gri-açık renkli batık leke ve etrafında kırmızı halka. Meyve içi sağlıklı olabilir ancak ihracat değeri sıfıra düşer.",
        "chemical": "Bakır fungisit, Mankozeb, Klorotalonil",
        "organic": "Bakır oksiklorür spreyi",
        "interval": "21-28 gün (yaz-sonbahar döneminde)",
        "severity_indicators": {
            "mild": "Birkaç meyvede küçük lekeler; pazarlama değeri biraz düşmüş.",
            "moderate": "Meyvelerin %20-50'sinde leke; ihracat dışı.",
            "severe": "Meyvelerin büyük bölümünde yaygın leke; tüm ürün değer kaybetmiş."
        },
        "prevention": "Hastalıksız fide kullan. Bahçe artıklarını temizle (sporlar yaprak artıklarında kışlıyor). Yaz-sonbahar döneminde düzenli ilaçlama programı uygula.",
        "notes": "AB ve bazı ülkelere ihracatta karantina zararlısı sayılır. İhracat yapan bahçelerde çok dikkatli takip gerekir."
    },

    # ─────────────────────────────────────────────
    # ZEYTİN HASTALIKLARI
    # ─────────────────────────────────────────────

    "olive_peacock_spot": {
        "name": "Olive Peacock Spot (Zeytin Halkalı Leke - Spilocea oleagina)",
        "affected_plants": ["olive"],
        "symptoms": "Yaprakların alt yüzeyinde önce sarı halkayla çevrili yeşilimsi lekeler, sonra kahverengileşir ve 'tavus kuşu gözü' görünümü alır. Ağır enfeksiyonda erken yaprak dökümü yaşanır.",
        "chemical": "Bakır bazlı fungisit (bakır hidroksit, bakır oksiklorür)",
        "organic": "Bordo bulamacı (sonbahar ve ilkbaharda)",
        "interval": "Sonbaharda hasat sonrası + ilkbaharda çiçeklenme öncesi",
        "severity_indicators": {
            "mild": "Birkaç yaprakta küçük lekeler; yaprak dökümü yok.",
            "moderate": "Birden fazla dalda yaygın lekeler; erken yaprak dökümü başlamış.",
            "severe": "Ağır yaprak dökümü; ağacın zayıflaması ve verim düşüşü."
        },
        "prevention": "Hasat sonrası ve çiçeklenme öncesi bakır spreyi uygula. Budama ile hava sirkülasyonunu artır. Aşırı azot gübrelemesinden kaçın.",
        "notes": "Sonbahar ve ilkbahar yağışlı dönemlerinde ilaçlama kritiktir. Hasat sonrası uygulama çok önemlidir."
    },

    "olive_knot": {
        "name": "Olive Knot / Knot Disease (Zeytin Dal Kanseri - Pseudomonas savastanoi)",
        "affected_plants": ["olive"],
        "symptoms": "Dal ve sürgünlerde sert, yuvarlak ur (yumru/kanser) oluşumu. Urlar dalın iletim dokusunu tıkayarak zayıflamaya yol açar. Rüzgar ve yağmurla, özellikle budama yaraları üzerinden bulaşır.",
        "chemical": "Bakır bazlı bakterisit (koruyucu). Etkilenmiş dalları kes.",
        "organic": "Etkilenmiş dal ve sürgünleri budamayla uzaklaştır. Budama aletlerini dezenfekte et.",
        "interval": "Hastalıklı dal tespitinde anında müdahale",
        "severity_indicators": {
            "mild": "Birkaç sürgünde küçük urlar; ağacın genel sağlığı iyi.",
            "moderate": "Birden fazla ana dalda urlar; büyüme ve verim etkilenmiş.",
            "severe": "Ağacın iskelet dallarında yaygın urlar; ağır verim kaybı, ağaç giderek zayıflıyor."
        },
        "prevention": "Budama aletlerini %10 çamaşır suyu veya %70 alkolle dezenfekte et. Budama yaralarına bakır macun sür. Kuru havalarda budama yap. Zararlı böcek zararlarından koruma sağla.",
        "notes": "Budama aletlerini dezenfekte etmek şarttır. Budama sonrası yaraları hemen kapat."
    },

    "verticillium_olive": {
        "name": "Verticillium Wilt of Olive (Zeytin Verticillium Solgunluğu - Verticillium dahliae)",
        "affected_plants": ["olive"],
        "symptoms": "Ani veya yavaş seyreden solgunluk ve dal ölümü. Etkilenen dalların iletim dokusunda kahverengi renk değişimi. Bütün ağaç hızla veya birkaç yılda ölebilir.",
        "chemical": "Etkili fungisit tedavisi yoktur. Toprak fumigasyonu (sınırlı etki).",
        "organic": "Toprak solarizasyonu (temmuz-ağustos). Trichoderma biyolojik preparatlar. Toprak organik maddesini artır.",
        "interval": "Önleme aşamasında",
        "severity_indicators": {
            "mild": "Tek dal veya sürgünde solar; ağacın büyük bölümü sağlıklı.",
            "moderate": "Birden fazla ana dalda veya ağacın yarısında solma.",
            "severe": "Tüm ağaç solmuş veya ölmüş."
        },
        "prevention": "Etkilenmiş alanlarda yeni dikim öncesi toprak solarizasyonu yap. Sulama sistemini kontrol et (aşırı sudan kaçın). Enfeksiyon görmüş toprakta alternatif konakçılardan kaçın.",
        "notes": "Genç zeytinliklerde özellikle tehlikelidir. Daha önce sebze yetiştirilen alanlarda dikim yaparken dikkatli ol."
    },

    # ─────────────────────────────────────────────
    # GENEL HASTALIKLAR
    # ─────────────────────────────────────────────

    "gray_mold": {
        "name": "Gray Mold (Kurşuni Küf - Botrytis cinerea)",
        "affected_plants": ["tomato", "pepper", "strawberry", "grape", "lettuce", "bean", "cucumber", "rose"],
        "symptoms": "Çiçek, yaprak, meyve veya sapda gri-kahverengi yumuşak çürüme ve gri toz halinde spor örtüsü. Sera koşullarında ve yüksek nemde çok yaygın ve agresif.",
        "chemical": "Iprodion, Boscalid, Fenheksamid, Siprodinil+Fludioksonil",
        "organic": "Trichoderma içerikli biyolojik preparatlar. Potasyum bikarbonat spreyi. Havalandırma artışı.",
        "interval": "7-10 gün",
        "severity_indicators": {
            "mild": "Birkaç çiçek veya yaprakta gri leke; spor yığını henüz küçük.",
            "moderate": "Birden fazla meyve veya yaprakta yaygın yumuşak çürüme ve gri spor.",
            "severe": "Ürünün büyük bölümünde hızlı çürüme; sera veya depo kayıpları çok yüksek."
        },
        "prevention": "Sera havalandırmasını artır. Nispi nemi %85'in altında tut. Ölü bitki kısımlarını düzenli temizle. Bitki sıklığını azalt. Sulama saatini gündüz seç.",
        "notes": "Seralar için büyük tehdit. Nispi nemi düşür ve havalandırmayı artır. Kimyasal direnci hızlı gelişebilir, aktif madde rotasyonu yap."
    },

    "damping_off": {
        "name": "Damping Off (Fide Çöküş Hastalığı - Pythium / Rhizoctonia)",
        "affected_plants": ["tomato", "pepper", "eggplant", "cucumber", "lettuce", "all seedlings"],
        "symptoms": "Fidelerde toprak seviyesinden su emmiş görünümlü kahverengi nekroz ve çökme. Fideler devrilip ölür. Hem çimlenme öncesi hem de sonrası ölüme yol açar.",
        "chemical": "Metalaksil (Pythium için), PCNB, Karbendazim (Rhizoctonia için) — tohuma veya toprağa uygulama",
        "organic": "Steril yetiştirme ortamı kullan. Trichoderma içerikli biyolojik preparatlar. Aşırı sulamadan kaçın.",
        "interval": "Dikimden önce önleyici uygulama",
        "severity_indicators": {
            "mild": "Birkaç fidede çökme; genel tablette büyük bölüm sağlıklı.",
            "moderate": "Tablette birden fazla alanda yaygın çökme; %20-50 fide kaybı.",
            "severe": "Tablette %50'den fazla fide kaybı; yeniden ekim gerekiyor."
        },
        "prevention": "Steril tohum yetiştiriciliği ortamı kullan. Aşırı sulama yapma. Fideler için iyi drenajlı ortam hazırla. Tohumu fungisitle ilaçla. Yeterli havalandırma sağla.",
        "notes": "Aşırı sulama ve düşük sıcaklık riski artırır. Steril yetiştirme ortamı ve kontrollü sulama en iyi önlemdir."
    },

}


def get_treatment(disease_name: str) -> dict:
    """Look up treatment information for a plant disease from DISEASE_DB.

    Performs fuzzy matching: the query and database keys are compared
    with substring matching in both directions.

    Args:
        disease_name: Disease identifier, e.g. 'early_blight', 'powdery_mildew'.

    Returns:
        Dict with disease info (name, chemical, organic, interval, notes, etc.).
        Returns a fallback entry if the disease is not found in the database.
    """
    normalized_key = disease_name.lower().replace(" ", "_").strip()
    for disease_id, info in DISEASE_DB.items():
        if disease_id in normalized_key or normalized_key in disease_id:
            return info
    return {
        "name": disease_name,
        "chemical": "Consult local agricultural office",
        "organic": "N/A",
        "interval": "N/A",
        "notes": "Disease not found in database",
    }
