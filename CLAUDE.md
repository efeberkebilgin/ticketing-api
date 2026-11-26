# CLAUDE.md – Ticketing API (Kalıcı Proje Kuralları)

Kalıcı kurallar ve kararlar yalnızca burada tutulur; güncel durum ve sıradaki iş için HANDOVER.md'ye bak.
Etiketler: **[Uygulandı]** kodda var · **[Karar verildi, yazılmadı]** plan aşamasında · **[Açık]** henüz karar yok

## Project Overview
- Amaç: Eşzamanlı yük altında doğru çalışan (aşırı satış ve çift rezervasyon yok) etkinlik bilet rezervasyon backend'i. [Karar verildi, yazılmadı]
- Bağlam: Yaz stajı başvurularında CV'yi güçlendirecek backend portfolyo projesi; sahibi 3. sınıf yazılım mühendisliği öğrencisi, programı yoğun.
- Çözülen problem: Aynı anda çok kişi son biletlere istek attığında stok eksiye düşmemeli; tekrarlanan istek ikinci kayıt üretmemeli.
- Temel işlevler:
  - P0: kayıt/giriş, JWT, roller (user/organizer/admin); mekan, etkinlik, bilet kategorisi CRUD; rezervasyon (hold, ~10 dk) ve durum makinesi (held → confirmed/expired/cancelled); idempotency; ödeme simülasyonu; süresi dolan hold'ları temizleyen arka plan görevi; kilitleme stratejisi + deadlock retry. [Karar verildi, yazılmadı]
  - P1: filtre/sayfalama, kullanıcı başına bilet limiti, iptal/iade, satış raporu, indeks optimizasyonu (EXPLAIN). [Karar verildi, yazılmadı]
  - P2: rate limiting, audit log, numaralı koltuk haritası, Redis cache. [Karar verildi, yazılmadı]

## Technology Stack
- [Uygulandı] Python 3.12 (Docker imajı python:3.12-slim), FastAPI, Uvicorn
- [Uygulandı] SQLAlchemy 2.0 (senkron), PyMySQL + cryptography, MySQL 8.0 (InnoDB), Alembic
- [Uygulandı] pydantic-settings, pytest + httpx, Docker Compose
- [Karar verildi, yazılmadı] GitHub Actions (CI), k6 veya Locust (yük testi)
- [Açık] JWT ve şifre hash kütüphanesi, arka plan görevi aracı (APScheduler/Celery), Redis, deploy platformu, lint/format aracı

## Project Structure
```
app/            main.py (FastAPI app) · config.py (Settings) · database.py (engine, SessionLocal, get_db)
app/models/     base.py (Base, NAMING_CONVENTION, TimestampMixin, enum_column) · user.py · catalog.py · booking.py · __init__.py
app/routers/    health.py (/health, /health/db)
alembic/        env.py · script.py.mako · versions/ (migration dosyaları)
tests/          test_health.py
docs/           er-diagram.md (Mermaid ER diyagramı)
kök             docker-compose.yml · Dockerfile · alembic.ini · pytest.ini · requirements(-dev).txt · .env.example · README.md
                CLAUDE.md · HANDOVER.md · AGENTS.md · GEMINI.md
```
- `app/models/__init__.py` tüm modelleri içe aktarır; Alembic'in modelleri görmesi buna bağlıdır.
- Henüz yok, eklenecek [Karar verildi, yazılmadı]: `app/schemas/` (Pydantic), `app/services/` (iş mantığı), `tests/conftest.py` (test DB fixture'ları).

## Commands
Ortam: Windows + PowerShell + Docker Desktop; komutlar proje kökünden (docker-compose.yml'ın olduğu klasör) çalışır.
- Başlat: `docker compose up --build` (arka planda: `docker compose up -d`) · Durdur: `docker compose down` · Veritabanını sıfırla: `docker compose down -v`
- Log: `docker compose logs -f api`
- Migration üret: `docker compose exec api alembic revision --autogenerate -m "<mesaj>"`; üretileni oku, sonra uygula
- Migration uygula / geri al / durum: `docker compose exec api alembic upgrade head` · `... downgrade -1` · `... current`
- Test: `docker compose exec api pytest`
- Tabloları gör: `docker compose exec db mysql -u<db_kullanıcısı> -p <db_adı> -e "SHOW TABLES;"` (kullanıcı/db adı docker-compose.yml'de, parola istenir)
- Swagger: http://localhost:8000/docs · MySQL host portu: 3307
- Lint/format: Henüz yok [Açık]

## Environment Variables
Yalnızca isimler (değerler yazılmaz):
- `DATABASE_URL`: SQLAlchemy bağlantı adresi (`Settings.database_url`, app/config.py). Docker'da docker-compose.yml verir; Docker dışında `.env` ya da kod varsayılanı.
- `APP_NAME`: opsiyonel, FastAPI başlığı (`Settings.app_name`).
- `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`: yalnızca db konteynerinin ilk kurulumu (docker-compose.yml, yerel geliştirme).
- Öncelik: ortam değişkeni > `.env` > kod varsayılanı. `.env` git'e girmez, `.env.example` girer.
- JWT gizli anahtarı vb.: Henüz yok [Açık]

## Architecture
- [Uygulandı] Katmanlar: router (app/routers) → oturum (app/database.py: `get_db` dependency'si) → ORM modelleri (app/models) → MySQL. Ayarlar app/config.py'de tek yerde.
- [Uygulandı] Engine bağlantıyı tembel açar; session istek başına açılır ve `finally` ile kapanır; commit/rollback servise aittir.
- [Karar verildi, yazılmadı] İş mantığı app/services/ altında; router'lar ince kalır; giriş/çıkış doğrulaması app/schemas/ (Pydantic); auth ve rol kontrolü FastAPI dependency'leri.
- [Açık] Ayrı repository katmanı olacak mı.

## Coding Standards
- [Uygulandı] Tip ipuçları; SQLAlchemy 2.0 stili (`Mapped[...]`, `mapped_column`); modeller alan bazlı dosyalarda (user/catalog/booking).
- [Uygulandı] Yeni model `app/models/__init__.py`'ye eklenmeli, yoksa Alembic autogenerate görmez.
- [Uygulandı] Enum'lar `enum_column()` ile VARCHAR; para `Numeric(10, 2)`; `created_at` için `TimestampMixin`; her `CheckConstraint` bir `name=` taşır (naming convention gereği).
- [Uygulandı] İsimlendirme: dosya/fonksiyon snake_case, sınıf PascalCase, tablo adı çoğul snake_case. Docstring ve yorumlar kısa, İngilizce, "neden"i anlatır.
- [Karar verildi, yazılmadı] İş mantığı router'da değil servislerde.
- Hata yönetimi (HTTPException / özel exception sınıfları): Henüz yok [Açık]

## Database Standards
- [Uygulandı] MySQL 8.0 InnoDB, utf8mb4 / utf8mb4_unicode_ci; şema değişikliği yalnızca Alembic ile.
- [Uygulandı] Kısıt ve indeks isimleri `NAMING_CONVENTION` ile (app/models/base.py). `ON DELETE CASCADE` yalnızca `ticket_tiers.event_id` ve `reservation_items.reservation_id`'de; diğer FK'ler bağlı kayıt varken silmeyi engeller.
- [Uygulandı] Bütünlük kuralları: `ticket_tiers` CHECK (`available_quantity >= 0` ve `<= total_quantity`), `reservation_items` CHECK (`quantity > 0`); UNIQUE `users.email`, `(event_id, name)`, `(user_id, idempotency_key)`; indeksler `(status, starts_at)` ve `(status, expires_at)`. (Yazıldı; DB'ye uygulandığı ve davranışı doğrulanmadı, bkz. HANDOVER.md.)
- [Uygulandı] `reservation_items.unit_price` alanı var; fiyatın rezervasyon anında kopyalanması [Karar verildi, yazılmadı].
- [Karar verildi, yazılmadı] Stok değişimi tek transaction içinde; çok kategorili işlemde kilitler `ticket_tiers.id` artan sırayla alınır; deadlock'ta retry.
- [Karar verildi, yazılmadı] Dört strateji aynı yük testiyle kıyaslanır: naif (kasıtlı hatalı baseline), atomik `UPDATE ... WHERE available_quantity >= n`, `SELECT ... FOR UPDATE`, optimistic (`version` kolonu).
- [Açık] Zaman dilimi (UTC standardı; Python saati mi MySQL `NOW()` mu), izolasyon seviyesi (MySQL varsayılanı REPEATABLE READ).

## API Standards
- [Uygulandı] `GET /health`, `GET /health/db` (JSON sözlük döner).
- [Karar verildi, yazılmadı] JWT Bearer (`Authorization` başlığı); `POST /reservations` için `Idempotency-Key` başlığı; Pydantic doğrulaması; yazma işlemleri rol bazlı (organizer/admin).
- [Açık] URL öneki/sürümleme, hata yanıt formatı, sayfalama formatı, durum kodu eşlemeleri.

## Git Rules
- Ben açıkça istemeden commit/push yapma.
- Oturum başında branch ve commit durumunu incele; commit edilmemiş değişiklikleri koru, izinsiz geri alma veya silme yapma.
- [Uygulandı] Tek dal `main`; remote `origin` = github.com/efeberkebilgin/ticketing-api. Commit mesajları İngilizce Conventional Commits (`feat:`, `chore:` ...); migration ayrı commit.
- [Açık] Özellik dalları kullanılacak mı.

## Definition of Done
- Kod yazıldı, Docker içinde gerçekten çalıştırıldı, ilgili test yazıldı ve geçti; migration varsa üretildi, okundu ve uygulandı.
- İlgili haftanın bitiş kriteri (HANDOVER.md, Pending Tasks) sağlandı.
- Kullanıcı yazılan kodu kendi cümleleriyle açıklayabiliyor (bkz. çalışma biçimi).
- Oturum sonunda HANDOVER.md güncellenir (Testing Status ve Recent Changes dahil); yazılmış kod ile test edilmiş kod ayrı belirtilir.

## Language Rules
- Kullanıcıyla konuşma dili: Türkçe.
- [Uygulandı] Kod, kod yorumları, commit mesajları ve README: İngilizce.
- API hata mesajlarının dili [Açık].

## Security
- Bu dosyalara ve koda asla şifre, token, API anahtarı yazma.
- docker-compose.yml'deki veritabanı bilgileri yalnızca yerel geliştirme içindir; üretimde kullanılmaz. MySQL'in 3307 portu yalnızca geliştirme için açıktır.
- Şifreler düz saklanmaz (`users.hashed_password`); hash algoritması [Açık].
- `text()` ile ham SQL'e kullanıcı girdisi string birleştirmeyle eklenmez.

## Important Technical Decisions
- Python + FastAPI + MySQL: kullanıcı kısıtı (gerekçe: backend'e odaklanma, CV).
- Senkron SQLAlchemy 2.0 (alternatif: async): kilitleme/transaction davranışını anlamak ve test etmek daha sade; FastAPI senkron endpoint'leri thread pool'da çalıştırır.
- PyMySQL + cryptography: saf Python sürücü; MySQL 8 `caching_sha2_password` için cryptography şart.
- Kategori bazlı stok (`ticket_tiers.available_quantity`), numaralı koltuk değil (alternatif: koltuk haritası, P2): MVP'yi basit tutar, eşzamanlılık konsepti aynı.
- Son savunma hattı olarak veritabanı CHECK kısıtları: kodda hata olsa da aşırı satış yazılamaz.
- Idempotency, `reservations` üzerinde UNIQUE `(user_id, idempotency_key)` ile başladı; ilk planda ayrı tablo düşünülmüştü, güncel olan kısıt yaklaşımı. [Açık] 4. haftada gerekirse ayrı tabloya ayrılır.
- Enum'lar VARCHAR (alternatif: native ENUM): yeni değer eklemek migration gerektirmez.
- Hold süresi ~10 dk (plan taslağı).
- Plan: 8 hafta (ilk öneri ~7 haftaydı, güncel olan 8 hafta). 3, 4 ve 7. haftalar dokunulmaz; kayarsa önce P2, sonra P1 kesilir. Haftalık işler HANDOVER.md'de.
- Çalışma biçimi (kullanıcı onayladı): Claude yazar ve anlatır → kullanıcı kendi cümleleriyle geri anlatır → kullanıcı küçük bir değişikliği kendi yapar → Claude gözden geçirir. 3-4. haftada kilitleme stratejilerinden en az birini kullanıcının yazması önerildi, ayrıca onaylanmadı [Açık].

## Development Rules
- Mevcut mimariyi ve standartları koru; gerekçesiz teknoloji/mimari değişikliği yapma.
- Çalışan kodu gereksiz yere yeniden yazma veya refactor etme.
- Değişiklikten önce ilgili dosyaları ve aralarındaki ilişkileri incele.
- Gereksiz bağımlılık ve karmaşık çözüm ekleme; en basit sürdürülebilir çözümü seç.
- Güvenlik, veri bütünlüğü ve hata yönetimini ihmal etme.
- Emin olmadığın teknik detayı varsayma: önce kodu incele, hâlâ emin değilsen bana sor veya [Açık] olarak işaretle.
- Gereksiz uzun açıklamadan kaçın; çalışan dosyaların tamamını tekrar yazma, yalnızca değişen bloğu göster.
- Her kod değişikliğinde dosya yolunu açıkça belirt.
