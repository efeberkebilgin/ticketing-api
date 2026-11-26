# HANDOVER.md – Güncel Durum

Son güncelleme: 2026-11-26 · Etiketler: **[Uygulandı]** · **[Karar verildi, yazılmadı]** · **[Açık]**
Kalıcı kurallar ve kararlar için CLAUDE.md'ye bak; burada tekrarlanmaz.

## Current Project Status
- Aşama: 8 haftalık planın 1. haftası tamamlandı; 2. hafta başlamadı. [Uygulandı]
- Var: Docker Compose ortamı, FastAPI iskeleti, 7 tablonun SQLAlchemy modelleri, ilk Alembic migration dosyası, tek smoke test.
- Yok: kimlik doğrulama, CRUD, rezervasyon mantığı, servis katmanı, veritabanı kullanan testler, CI.
- Doğrulama sınırı: Bu dosya, kullanıcının yerel repo'sundaki güncel kod incelenmeden yazıldı. Dayanak: Claude'un hafta 1'de ürettiği iskelet, kullanıcının bildirdiği komut çıktıları ve sohbet kararları. Migration dosyasının içeriği ve yerel değişiklikler incelenmedi.

## Completed Features
- Docker Compose ortamı (`db`: MySQL 8.0, `api`: FastAPI + Uvicorn `--reload`): `docker-compose.yml`, `Dockerfile`. Yazıldı; kullanıcı `docker compose up --build` çalıştırdı, testler konteynerde koştu.
- Health endpoint'leri: `app/routers/health.py`. `/health` pytest ile test edildi. `/health/db` yazıldı, çalıştığı bildirilmedi.
- Veri modeli: `User`, `Venue`, `Event`, `TicketTier`, `Reservation`, `ReservationItem`, `Payment` (`app/models/`); şema `docs/er-diagram.md`. Yazıldı, test edilmedi.
- Alembic kurulumu ve ilk migration: `alembic/env.py`, `alembic/versions/*_initial_schema.py`. Dosya üretildi ve commit'lendi (`e9d92f7`); DB'ye uygulandığı bildirilmedi.
- Dokümantasyon: `README.md`, `docs/er-diagram.md`; 1. hafta teknik rehberi (Claude Doc "Ticketing API — 1. Hafta Teknik Rehberi": https://claude.ai/artifact/E43RjLTyCdn4JieArwbaMK).
- Proje hafızası: `CLAUDE.md`, `HANDOVER.md`, `AGENTS.md`, `GEMINI.md` kök dizine kopyalandı (kullanıcı bildirdi).

## Active Task
- Devam eden kod işi yok. Sıradaki görev: 2. hafta, kimlik doğrulama (JWT). Başlamadı.
- Çalışma biçimi CLAUDE.md'de: Claude kodu açıklamalı hazırlar, kullanıcı geri anlatır.

## Pending Tasks
Tümü [Karar verildi, yazılmadı]:
- H2: kayıt/giriş, şifre hash, JWT, rol dependency'leri; mekan/etkinlik/bilet kategorisi CRUD; test DB + `conftest.py`. Bitiş: Swagger'dan organizatör etkinlik ve kategori oluşturur, sıradan kullanıcı reddedilir.
- H3: kasıtlı kilitsiz naif rezervasyon + eşzamanlı test; aşırı satış baseline'ı ölçülür.
- H4: atomik UPDATE / `FOR UPDATE` çözümleri, hold ve durum makinesi, idempotency, kilit sırası. Bitiş: 200 eşzamanlı istek / 50 stok → tam 50 başarılı.
- H5: ödeme simülasyonu, iptal/iade, expiry arka plan görevi, deadlock retry.
- H6: raporlama, filtre/sayfalama, `EXPLAIN` + indeks; P1'den seçmeler.
- H7: tam testler, GitHub Actions CI, k6/Locust ile 4 stratejinin karşılaştırma tablosu.
- H8: README, mimari şema, deploy, demo, CV satırları.

## Known Issues
- Testler veritabanına dokunmuyor; test DB altyapısı yok.
- Alembic log çıktısı kapalı olabilir (`upgrade` sessiz). İsteğe bağlı ayar önerildi, yerel repo'da uygulanıp uygulanmadığı bilinmiyor.
- Tarihler naive `datetime`, `created_at` MySQL saatiyle; UTC kararı yok [Açık].
- Bazı kurallar DB'de zorlanmıyor: kategori toplamı ≤ `venues.capacity`, bir rezervasyona çoklu başarılı ödeme; `ticket_tiers.version` kullanılmıyor.
- `UniqueConstraint("event_id", "name")` adı `uq_ticket_tiers_event_id` olur; yanıltıcı, işlevsel hata değil.
- Dev/prod ayrımı yok: dev bağımlılıkları imajda, `--reload`, sabit yerel DB bilgileri, 3307 portu açık.
- Havuz: `pool_size=10` + `max_overflow=20`, worker sayısıyla çarpılır; MySQL `max_connections` yük testinde önemli.
- ORM ilişkileri eksik (`Event.organizer`, `Reservation.user`). `updated_at` `onupdate` yalnızca SQLAlchemy güncellemelerinde çalışır.
- Proje yolunda ASCII olmayan karakter varsa Docker volume sorunu çıkabilir (yol bilinmiyor) [Açık].

## Testing Status
- Başarılı: `tests/test_health.py` → 1 passed (yalnızca `/health`), 1 uyarı (starlette `TestClient` / httpx deprecation, zararsız).
- Test edilmeyen: `/health/db`, modeller ve kısıtlar, migration upgrade/downgrade, tabloların oluşması, veritabanı kullanan her şey, eşzamanlılık.

## Recent Changes
- Bu oturumda kaynak kod değişmedi. Eklenenler: `CLAUDE.md`, `HANDOVER.md`, `AGENTS.md`, `GEMINI.md` (kök dizin).
- Hafta 1'de: iskelet oluşturuldu; kullanıcı migration üretip iki commit attı ve `main`'i GitHub'a gönderdi (`d4024dd`, `e9d92f7`).
- Git: 4 `.md` dosyasının commit'lendiği bildirilmedi; muhtemelen commit edilmemiş. İzinsiz geri alma veya silme yapma.

## Open Questions
- Kullanıcı: aşağıdaki Verification çıktıları nedir (özellikle `alembic current`, tablolar, `/health/db`)?
- Kullanıcı: 3-4. haftada bir kilitleme stratejisini kendisi yazacak mı?
- Kullanıcı: önerilen ön adımlar (rehberdeki kendini sına soruları, sahiplenme egzersizleri) yapılsın mı, atlansın mı?
- Seçimler bekliyor: JWT ve şifre hash kütüphanesi, API öneki/hata formatı, UTC standardı, özellik dalları, Alembic log ayarı.

## Next Step
- 1) Önce Verification komutlarıyla 1. hafta durumunu doğrula; sonuçları bu dosyaya yaz.
- 2) Sonra 2. hafta ilk adımı: kimlik doğrulama (kayıt/giriş, şifre hash, JWT üretimi/doğrulama). Önerilen yerleşim [Açık]: `app/security.py`, `app/schemas/auth.py`, `app/routers/auth.py`, kayıt `app/main.py`'de, yeni bağımlılıklar `requirements.txt`'de. Kütüphane seçimini kullanıcıya sor. Hedef: Swagger'dan kayıt ol, giriş yap, token al.

## Verification
- `docker compose exec api alembic current` → bir revizyon kodu ve `(head)` görünmeli.
- `docker compose exec db mysql -u<db_kullanıcısı> -p <db_adı> -e "SHOW TABLES;"` → 7 uygulama tablosu + `alembic_version`.
- Tarayıcıda `http://localhost:8000/health/db` → `reachable`.
- `docker compose exec api pytest` → 1 passed.
- Kimlik doğrulama adımı sonrası: Swagger'da kayıt, giriş ve token akışı çalışmalı; ilgili testler geçmeli.
