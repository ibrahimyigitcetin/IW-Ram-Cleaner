# 🧹 IW Ram Cleaner | Night Club Edition

## 🌟 Proje Hakkında

**IW Ram Cleaner**, sisteminizdeki RAM (Bellek) tüketimini yönetmek için tasarlanmış, güçlü ve estetik bir Python uygulamasıdır. Yüksek kaynak kullanan veya yanıt vermeyen süreçleri kolayca tespit etmenizi sağlar ve akıllı **güvenli sonlandırma (Safe Kill)** mekanizması ile sistem kararlılığınızı koruyarak anında bellek serbestleştirme imkanı sunar.

Uygulama, klasik **"Retro Night Club Game"** estetiği ile tasarlanmıştır; karanlık arka planlar, neon renkler (Cyan ve Pembe) ve `Consolas` yazı tipi kullanarak sistem yönetimine dinamik ve eğlenceli bir yaklaşım getirir.

### ✨ Güçlü Özellikler

| Özellik | Detaylı Açıklama |
| :--- | :--- |
| **🛡️ Akıllı Koruma (Safe Kill)** | Uygulama, `csrss.exe`, `winlogon.exe` gibi kritik Windows sistem süreçlerini tanır. Bu süreçlerin yanlışlıkla sonlandırılması otomatik olarak engellenir ve kullanıcıya sistemi çökme potansiyeli hakkında güçlü bir uyarı sunulur. |
| **📈 Detaylı Bellek Metrikleri** | Süreç listesinde iki önemli bellek metriği yer alır: **RSS (Resident Set Size)**: Sürecin fiziksel RAM'de (Gerçek RAM) kullandığı miktar. **VMS (Virtual Memory Size)**: Sürecin tahsis ettiği toplam sanal bellek miktarı. |
| **Sistem RAM Genel Bakışı** | Pencerenin üst kısmında, sisteminizin **Toplam**, **Kullanılan** ve **Boş** RAM miktarlarını gösteren anlık, güncel bilgi çubuğu bulunur. |
| **Çoklu Seçim ve Filtreleme** | Tek bir tıklama ve sürükleme hareketiyle veya **`Ctrl` / `Shift`** tuşlarıyla birden fazla süreci seçin. Üstteki arama kutusu, süreç **Adı** veya **PID** (İşlem Numarası) ile anında, yüksek performanslı filtreleme sağlar. |
| **Gelişmiş Kullanıcı Deneyimi (UX)** | Uygulama, hızlı etkileşim için klavye kısayollarını destekler: **`F5`** ile listeyi yenileme ve **`Delete`** ile seçili süreçleri sonlandırma. Ayrıca, butonlar üzerinde bilgi sağlayan **Tooltip'ler** bulunur. |

-----

## ⚙️ Kurulum ve Başlatma

Bu uygulamayı çalıştırmak için **Python 3.x** ve **`psutil`** kütüphanesine ihtiyacınız vardır.

### 1\. Kütüphane Kurulumu

Aşağıdaki komutu kullanarak gerekli bağımlılıkları kurun:

```bash
pip install psutil
```

### 2\. Başlatma

Kodu kaydettiğiniz dosyayı (örneğin `iw_ram_cleaner.py`) terminalde çalıştırın:

```bash
python iw_ram_cleaner.py
```

> 🚨 **Yönetici Yetkisi:** Windows veya Linux sistemlerinde kritik süreçleri güvenilir bir şekilde sonlandırmak için uygulamayı **Yönetici/Root** yetkileriyle çalıştırmanız önerilir.

-----

## 🖥️ Kullanım Rehberi

1.  **RAM Durumu:** Üstteki bilgi çubuğundan anlık sistem RAM kullanımınızı kontrol edin.
2.  **Hedefleme:** Liste, en çok fiziksel RAM tüketen süreçten başlayarak sıralanır.
3.  **Filtreleme:** Hızlıca bir süreç bulmak için **"Arama"** kutusunu kullanın.
4.  **Serbestleştirme:**
      * Bir veya daha fazla süreci seçin.
      * **`☢️ RAM SERBEST BIRAK`** butonuna tıklayın veya klavyeden **`Delete`** tuşuna basın.
      * Uygulama, güvenli olmayan işlemler için size kritik uyarılar sunacaktır.
5.  **Güncelleme:** Listeyi ve sistem RAM bilgilerini yenilemek için **`🔄 YENİLE (F5)`** butonunu kullanın.

-----

## 🎨 Retro Tema Renk Şeması

| Bileşen | Hex Kodu | Açıklama |
| :--- | :--- | :--- |
| **Arka Plan** | `#1A1A1A` | Koyu Gece Siyahı (BG\_DARK) |
| **Ana Vurgu** | `#00FFFF` (CYAN) | RAM Bilgisi, Normal Butonlar, Liste Metni |
| **Kritik Vurgu** | `#FF00FF` (PINK) | Başlıklar, Seçili Öğeler, KILL Butonu |
| **Yazı Tipi** | `Consolas` | Retro Terminal Görünümü |

-----

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

Detaylar için [CONTRIBUTING.md](CONTRIBUTING.md) ve [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) dosyasını inceleyiniz.

## 📄 Lisans

Bu proje MIT lisansı altında dağıtılmaktadır. Detaylar için [LICENSE](LICENSE) dosyasını inceleyiniz.
