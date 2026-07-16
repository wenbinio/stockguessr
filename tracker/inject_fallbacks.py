"""Re-inject every docs/api/*.json payload into the hub's offline-fallback
markers. Runs last in the CI refresh so the baked snapshots always match the
live endpoints.

Marker convention in docs/index.html:
  /*FALLBACK-START*/...json.../*FALLBACK-END*/            <- performance.json
  /*R2FALLBACK-START*/.../*R2FALLBACK-END*/               <- round2.json
  /*R3FALLBACK-START*/.../*R3FALLBACK-END*/               <- round3.json
  /*AGENTSFALLBACK-START*/.../*AGENTSFALLBACK-END*/       <- agents.json
  /*LEDGERFALLBACK-START*/.../*LEDGERFALLBACK-END*/       <- ledger.json
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "docs" / "api"
PAGE = ROOT / "docs" / "index.html"

MAP = {
    "FALLBACK": "performance.json",
    "R2FALLBACK": "round2.json",
    "R3FALLBACK": "round3.json",
    "AGENTSFALLBACK": "agents.json",
    "LEDGERFALLBACK": "ledger.json",
}


def main() -> None:
    html = PAGE.read_text()
    done = []
    for marker, fname in MAP.items():
        f = API / fname
        if not f.exists() or f"/*{marker}-START*/" not in html:
            continue
        blob = f.read_text().strip()
        html = re.sub(rf"(/\*{marker}-START\*/).*?(/\*{marker}-END\*/)",
                      lambda m: m.group(1) + blob + m.group(2), html, flags=re.S)
        done.append(marker)
    PAGE.write_text(html)
    print(f"injected: {', '.join(done) or 'nothing (no markers found)'}")


if __name__ == "__main__":
    main()
