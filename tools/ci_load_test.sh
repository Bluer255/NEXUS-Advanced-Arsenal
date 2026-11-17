#!/usr/bin/env bash
# Автоматичний тест мода у headless-сервері Mindustry (без графіки).
# Перевіряє: мод завантажується без помилок/попереджень, усі блоки з content/ існують,
# а Frostbite реально гасить пожежу (регресійний тест).
# Запуск:  bash tools/ci_load_test.sh     (потрібні: java 17+, curl, zip)
# Змінна GAME_VERSION задає тег гри (за замовчуванням v160.4).
set -euo pipefail

GAME_VERSION="${GAME_VERSION:-v160.4}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "== Завантаження сервера Mindustry $GAME_VERSION"
curl -fsSL -o "$WORK/server.jar" "https://github.com/Anuken/Mindustry/releases/download/${GAME_VERSION}/server-release.jar"

echo "== Збірка мода"
mkdir -p "$WORK/config/mods"
(cd "$ROOT" && zip -qr "$WORK/config/mods/nexus-arsenal.zip" mod.hjson content sprites bundles icon.png preview.png)

# Список id блоків береться з імен файлів у content/blocks/turrets
IDS=""
COUNT=0
for f in "$ROOT"/content/blocks/turrets/*.hjson; do
  id="$(basename "$f" .hjson)"
  IDS="${IDS}\"${id}\","
  COUNT=$((COUNT + 1))
done
IDS="[${IDS%,}]"

cat > "$WORK/cmds.txt" <<EOF
js ${IDS}.forEach(function(n){var b=Vars.content.getByName(ContentType.block,"nexus-arsenal-"+n);Log.info("CHECK "+n+" "+(b==null?"MISSING":"OK "+b.getClass().getSimpleName()))})
js Log.info("MODERR "+Vars.mods.list().map(function(m){return m.name+":"+m.hasContentErrors()}))
js Vars.logic.reset();Vars.world.resize(60,60);Vars.world.tiles.fill();Vars.state.rules.fire=true;Vars.world.tile(10,10).setBlock(Blocks.coreShard,Team.sharded,0);Vars.state.set(Packages.mindustry.core.GameState.State.playing)
js var f=Vars.content.getByName(ContentType.block,"nexus-arsenal-frostbite");Vars.world.tile(30,30).setBlock(f,Team.sharded,0);var b=Vars.world.tile(30,30).build;b.liquids.add(Liquids.water,20);Vars.world.tile(30,38).setBlock(Blocks.container,Team.sharded,0);var cb=Vars.world.tile(30,38).build;cb.items.add(Items.coal,10);Fires.create(Vars.world.tile(30,38));function cnt(){var n=0;for(var x=20;x<=40;x++)for(var y=28;y<=48;y++)if(Fires.has(x,y))n++;return n};Log.info("SIMSTART fires="+cnt())
js var out=[];for(var i=1;i<=450;i++){Time.delta=1;Vars.logic.update();if(i%150==0)out.push("t"+i+":fires="+cnt())};Log.info("SIM "+out.join(" | "))
exit
EOF

echo "== Запуск сервера"
OUT="$(cd "$WORK" && timeout 240 java -jar server.jar < cmds.txt 2>&1 | sed 's/\x1b\[[0-9;]*m//g' || true)"
echo "$OUT" | grep -E "mods loaded|CHECK|MODERR|SIM|\[(W|E)\]" || true

fail=0
echo "$OUT" | grep -q "1 mods loaded"                 || { echo "ПОМИЛКА: мод не завантажився"; fail=1; }
echo "$OUT" | grep -q "MODERR \[nexus-arsenal:false\]" || { echo "ПОМИЛКА: помилки контенту мода"; fail=1; }
OKN="$(echo "$OUT" | grep -c "CHECK .* OK " || true)"
[ "$OKN" -eq "$COUNT" ]                                || { echo "ПОМИЛКА: завантажено $OKN із $COUNT блоків"; fail=1; }
echo "$OUT" | grep -q "MISSING" && { echo "ПОМИЛКА: є незавантажені блоки"; fail=1; }
echo "$OUT" | grep -Eq "\[(W|E)\].*nexus"              && { echo "ПОМИЛКА: попередження/помилки в логу гри"; fail=1; }
echo "$OUT" | grep -Eq "SIM t150:fires=[0-9]+ \| t300:fires=0 " \
                                                        || { echo "ПОМИЛКА: Frostbite не загасив пожежу за 300 тіків (без нього вона горить ~600)"; fail=1; }

if [ "$fail" -ne 0 ]; then echo "== ТЕСТ НЕ ПРОЙДЕНО"; exit 1; fi
echo "== ТЕСТ ПРОЙДЕНО: $COUNT блоків, мод без помилок, пожежа гасне"
