#!/usr/bin/env python3
"""
Генератор локалізацій NEXUS: Advanced Arsenal (UTF-8).
Файли в bundles/:
  bundle.properties        - англійська (мова за замовчуванням / запасна)
  bundle_en.properties     - англійська (явний файл)
  bundle_uk_UA.properties  - українська
  bundle_ru.properties     - російська
Ключі формату block.<mod>-<id>.name|description|details (mod = nexus-arsenal).
"""
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bundles")
MOD = "nexus-arsenal"

T = {
 "en": {
  "volt": ("NEXUS Volt",
           "Electric turret. Fires charged orbs that burst into chain lightning on impact, striking nearby enemies.",
           "Medium damage, high rate of fire. Hits ground and air targets. Requires power; coolant increases fire rate."),
  "frostbite": ("NEXUS Frostbite",
           "Cryogenic turret. Fires ice shards that slow and freeze enemies, and extinguishes fires. Cryofluid creates a powerful icy burst with shrapnel.",
           "Low damage, strong area control. Runs on water; cryofluid gives a bigger burst and longer freezing. Prioritizes fires within range."),
  "nx-titan": ("NEXUS Titan",
           "Heavy kinetic turret. Fires massive armor-piercing slugs with high direct damage and powerful recoil.",
           "Slow rate of fire, ground targets only. Graphite is the basic ammo; thorium pierces armor and hits up to three targets in a line."),
 },
 "uk_UA": {
  "volt": ("NEXUS Шок",
           "Електрична турель. Стріляє зарядженими орбами, які при влученні розпадаються на ланцюгові блискавки та вражають сусідніх ворогів.",
           "Середній урон, висока швидкість атаки. Б'є по наземних і повітряних цілях. Потребує енергії; охолодження підвищує швидкість стрільби."),
  "frostbite": ("NEXUS Заморозка",
           "Кріогенна турель. Стріляє крижаними осколками, які сповільнюють і заморожують ворогів, а також гасить пожежі. Кріорідина створює потужний крижаний вибух з уламками.",
           "Малий урон, але сильний контроль території. Працює на воді; кріорідина дає більший вибух і довше заморожування. Пріоритетно цілиться у пожежі в радіусі дії."),
  "nx-titan": ("NEXUS Титан",
           "Важка кінетична турель. Стріляє масивними бронебійними снарядами з великим прямим уроном і потужною віддачею.",
           "Повільна стрільба, б'є лише по наземних цілях. Графіт - базовий снаряд; торій пробиває броню й уражає до трьох цілей на шляху."),
 },
 "ru": {
  "volt": ("NEXUS Шок",
           "Электрическая турель. Стреляет заряженными шарами, которые при попадании распадаются на цепные молнии и поражают соседних врагов.",
           "Средний урон, высокая скорострельность. Бьёт по наземным и воздушным целям. Требует энергии; охлаждение повышает скорострельность."),
  "frostbite": ("NEXUS Заморозка",
           "Криогенная турель. Стреляет ледяными осколками, которые замедляют и замораживают врагов, а также тушит пожары. Криожидкость создаёт мощный ледяной взрыв с осколками.",
           "Малый урон, но сильный контроль территории. Работает на воде; криожидкость даёт больший взрыв и более долгое замораживание. Приоритетно целится в пожары в зоне досягаемости."),
  "nx-titan": ("NEXUS Титан",
           "Тяжёлая кинетическая турель. Стреляет массивными бронебойными снарядами с большим прямым уроном и мощной отдачей.",
           "Медленная стрельба, бьёт только по наземным целям. Графит - базовый снаряд; торий пробивает броню и поражает до трёх целей на пути."),
 },
}
FILES = {"en": ["bundle.properties", "bundle_en.properties"], "uk_UA": ["bundle_uk_UA.properties"], "ru": ["bundle_ru.properties"]}
HEAD = {"en": "# NEXUS: Advanced Arsenal - English localization",
        "uk_UA": "# NEXUS: Advanced Arsenal - українська локалізація",
        "ru": "# NEXUS: Advanced Arsenal - русская локализация"}

os.makedirs(OUT, exist_ok=True)
for lang, turrets in T.items():
    lines = [HEAD[lang], "# Keys: block.<mod>-<id>.name / .description / .details", ""]
    for tid, (name, desc, det) in turrets.items():
        lines += [f"block.{MOD}-{tid}.name={name}", f"block.{MOD}-{tid}.description={desc}",
                  f"block.{MOD}-{tid}.details={det}", ""]
    for fn in FILES[lang]:
        with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines))
print("OK:", sorted(os.listdir(OUT)))
