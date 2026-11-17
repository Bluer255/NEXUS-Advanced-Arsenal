# Changelog

Формат: [Keep a Changelog](https://keepachangelog.com/). Версії: [SemVer](https://semver.org/).

## [0.3.0] - 2026-11-17

### Added
- Frostbite тепер гасить пожежі: кожен постріл складається з крижаного осколка та водяного «гасильника» (`MultiBulletType` + `LiquidBulletType`).
- Локалізації: англійська (`bundle.properties`, `bundle_en.properties`), українська (`bundle_uk_UA.properties`), російська (`bundle_ru.properties`).
- `preview.png` (1280×720, потрібне для Steam Workshop) та `icon.png` (256×256).
- `subtitle` у `mod.hjson`.
- Скрипти: `tools/gen_bundles.py`, `tools/gen_preview.py`, `tools/ci_load_test.sh`.
- CI (GitHub Actions): перевірка текстур/локалізацій, тест завантаження в headless-сервері v160.4 і регресійний тест гасіння пожежі; автоматичний реліз за тегом.

### Changed
- Назви турелей відповідають мові гри: NEXUS Титан / Шок / Заморозка (uk, ru), NEXUS Titan / Volt / Frostbite (en).

### Fixed
- Параметр `extinguish: true` у Frostbite не мав ефекту (осколки не гасять вогонь) — турель цілилась у пожежі й не гасила їх.

## [0.2.0] - 2026-11-16

### Added
- Перші три турелі: Volt, Frostbite, Titan (внутрішній id `nx-titan`, щоб не конфліктувати з ванільною Erekir-турелью `titan`).
- Піксель-арт спрайти (база, верх, рухомі частини, heat-шари), генератор `tools/gen_sprites.py`, перевірка `tools/validate.py`.
- Українська локалізація.
