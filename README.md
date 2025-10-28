# Utrecht Open Data Zoeksysteem

Een complete toolkit voor het zoeken, verkennen en downloaden van open datasets van de gemeente Utrecht via de DCAT API.

## 🎯 Overzicht

Dit project biedt toegang tot de Utrecht Open Data API (https://open.utrecht.nl/api) via:
- **Web interface** - Moderne, gebruiksvriendelijke browser applicatie
- **Command-line tool** - Python script voor automatisering en scripting
- **MCP Server** - Model Context Protocol server voor AI assistenten

### Toekomstige ontwikkelingen
De API bevat momenteel datasets in DCAT formaat. In de toekomst komen hier ook Woo (Wet open overheid) documenten en dossiers in vergelijkbaar formaat beschikbaar.

## ✨ Functionaliteit

### Web Interface
- 🔍 Zoeken door alle datasets
- 📊 Visuele weergave in grid layout
- 📖 Gedetailleerde dataset informatie
- ⬇️ Directe downloads in verschillende formaten (CSV, JSON, XML, etc.)
- **🔗 Woo-koppeling**: Automatische analyse van Woo-relevantie per dataset
- 📱 Responsive design voor desktop en mobiel
- 🎨 Utrecht huisstijl

### Command-line Tool
- Zoeken naar datasets met filters
- Details ophalen van specifieke datasets
- Beschikbare formaten bekijken
- Output in tabel, JSON of compact formaat
- Exporteren naar bestanden

### MCP Server
- Integratie met AI assistenten (Claude, etc.)
- Programmatische toegang tot alle datasets
- Tools voor zoeken, ophalen en downloaden
- **Woo-integratie**: Koppeling met landelijke Woo-index voor documentrelaties
- Intelligente analyse van dataset-relevantie voor Woo-categorieën

## 📦 Installatie

### Vereisten
- Python 3.6 of hoger
- Moderne webbrowser (Chrome, Firefox, Safari, Edge)

### Dependencies installeren

```bash
pip install -r requirements.txt
```

Of met een virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # Op Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Gebruik

### Web Interface (Aanbevolen)

**Let op:** De Utrecht Open Data API heeft geen CORS headers. Gebruik daarom de meegeleverde proxy server.

1. Start de proxy server:

```bash
python3 proxy_server.py
```

Je ziet:
```
╔═══════════════════════════════════════════════════════════════╗
║  Utrecht Open Data CORS Proxy Server                         ║
╚═══════════════════════════════════════════════════════════════╝

✓ Server draait op: http://localhost:8080
```

2. Open je browser op:
```
http://localhost:8080
```

3. Gebruik de interface:
   - Zoek naar datasets via de zoekbalk
   - Klik op een dataset tegel voor details
   - Bekijk de dataset beschrijving en metadata
   - Scroll naar "Downloads" voor beschikbare formaten
   - Bekijk de "Woo Koppeling" sectie voor gerelateerde documenten
   - Klik op de download knop om data op te halen

#### Andere poort gebruiken:
```bash
python3 proxy_server.py -p 8888
```

### Command-line Tool

Maak het script uitvoerbaar:
```bash
chmod +x utrecht_open_data.py
```

#### Zoeken naar datasets

Alle datasets ophalen:
```bash
./utrecht_open_data.py search
```

Zoeken met zoekterm:
```bash
./utrecht_open_data.py search verkeer
./utrecht_open_data.py search "openbare ruimte"
```

Met opties:
```bash
./utrecht_open_data.py search verkeer -n 10        # Max 10 resultaten
./utrecht_open_data.py search verkeer -f json      # JSON output
./utrecht_open_data.py search verkeer -o results.json  # Opslaan
```

#### Dataset details ophalen

```bash
./utrecht_open_data.py get afvalbakken
./utrecht_open_data.py get afvalbakken -f json
```

#### Beschikbare formaten bekijken

```bash
./utrecht_open_data.py formats afvalbakken
```

### MCP Server

De MCP server maakt de Utrecht Open Data API beschikbaar voor AI assistenten zoals Claude.

#### MCP Server starten

```bash
python3 mcp_server.py
```

#### Configuratie voor Claude Desktop

Voeg toe aan je Claude Desktop configuratie (`~/Library/Application Support/Claude/claude_desktop_config.json` op macOS):

```json
{
  "mcpServers": {
    "utrecht-opendata": {
      "command": "python3",
      "args": ["/path/to/open-utrecht-datasets/mcp_server.py"]
    }
  }
}
```

#### Beschikbare MCP Tools

**Dataset Tools:**
- `search_datasets` - Zoek naar datasets
- `get_dataset` - Haal dataset details op
- `get_distributions` - Haal beschikbare downloads op
- `list_all_datasets` - Toon alle datasets

**Woo Integratie Tools:**
- `analyze_woo_connection` - Analyseer relevantie van dataset voor Woo-categorieën
- `find_woo_related_datasets` - Zoek datasets gerelateerd aan Woo-onderwerpen

#### Woo Integratie Gebruiken

De MCP server kan datasets koppelen aan de 9 Woo-categorieën:
- 1a: Convenanten
- 1b: Jaarplannen en jaarverslagen  
- 1c: Organisatie en werkwijze
- 1d: Bereikbaarheidsgegevens
- 1e: Subsidies en opdrachten
- 1f: Klachten en bezwaren
- 1g: Adviezen Wob en Woo verzoeken
- 2: Woo-besluiten
- 3: Beschrijvingen van publieke informatie
- 4: Aanvullende actieve openbaarmaking

**Voorbeeld in Claude Desktop:**

```
Analyseer de Woo-relevantie van dataset 'parkeren'
```

Claude zal de `analyze_woo_connection` tool gebruiken en een rapport genereren met:
- Geëxtraheerde trefwoorden
- Gematchte onderwerpen (verkeer, mobiliteit, etc.)
- Relevante Woo-categorieën met toelichting
- Aanbevelingen voor documentkoppelingen

## 📖 API Details

### Base URL
```
https://open.utrecht.nl/api
```

### Endpoints

- `GET /api/datasets` - Lijst van datasets (DCAT formaat)
- `GET /api/datasets/{dataset}` - Dataset details
- `GET /api/datasets/{dataset}/distributions` - Beschikbare downloads

### DCAT Formaat

De API gebruikt de DCAT (Data Catalog Vocabulary) standaard met namespaced attributen:

- `dct:title` - Titel
- `dct:description` - Beschrijving
- `dct:modified` - Laatst gewijzigd
- `dct:publisher` - Uitgever
- `dcat:keyword` - Trefwoorden
- `dcat:accessURL` - Download URL

## 📁 Projectstructuur

```
utrecht/
├── README.md                  # Deze documentatie
├── QUICKSTART.md             # Snelstart gids
├── PROJECT_SUMMARY.md        # Project overzicht
├── requirements.txt           # Python dependencies
├── proxy_server.py           # CORS proxy server (verplicht voor web!)
├── utrecht_open_data.py      # Command-line tool
├── mcp_server.py             # MCP server voor AI assistenten
├── woo_connector.py          # Woo-integratie module
├── index.html                # Web interface
├── app.js                    # JavaScript (backup/legacy)
└── style.css                 # CSS styling (backup/legacy)
```

## 🔧 Technische Details

### Web Interface
- Vanilla JavaScript (geen frameworks)
- CORS proxy om browser beperkingen te omzeilen
- Responsive grid layout
- Modal dialogen voor details
- Directe download links
- **Asynchrone Woo-analyse per dataset**
- Real-time topic en categorie identificatie

### Command-line Tool
- Python 3.6+
- `requests` library voor HTTP calls
- Ondersteuning voor paginering
- Meerdere output formaten

### MCP Server
- Model Context Protocol v1.0
- Streaming output ondersteuning
- JSON-RPC 2.0
- Async/await voor performance
- Woo-integratie met keyword extractie en topic mapping
- 9 Woo-categorieën ondersteund
- Intelligent matching algoritme voor dataset-document relaties

### Browser Compatibiliteit
- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## 💡 Voorbeelden

### Voorbeeld 1: Zoeken en downloaden via web interface

1. Open http://localhost:8080
2. Zoek naar "afval"
3. Klik op "Afvalbakken"
4. Bekijk de dataset details
5. Scroll naar "Woo Koppeling" voor gerelateerde onderwerpen
6. Scroll naar "Downloads" sectie
7. Klik "Download CSV"

**Woo Koppeling toont:**
- Geïdentificeerde onderwerpen (bijv. "milieu", "openbare ruimte", "beheer")
- Relevante Woo-categorieën (indien van toepassing)
- Link naar Woo-index Utrecht
- Zoektermen voor documentonderzoek

### Voorbeeld 2: Alle datasets exporteren naar JSON

```bash
./utrecht_open_data.py search -f json -o alle_datasets.json
```

### Voorbeeld 3: Dataset details via command-line

```bash
./utrecht_open_data.py get afvalbakken
```

Output:
```
================================================================================
Dataset: Afvalbakken
================================================================================

ID: afvalbakken

Beschrijving:
Overzicht van bovengrondse afvalbakken in de gemeente Utrecht...

Keywords: afval, afvalbak
Gepubliceerd: 2021-11-24
================================================================================
```

### Voorbeeld 4: Beschikbare downloads bekijken

```bash
./utrecht_open_data.py formats bushaltes
```

Output:
```
================================================================================
Beschikbare formaten:
================================================================================

1. Formaat: CSV
   URL: https://data.utrecht.nl/.../bushaltes.csv
   Grootte: 0.45 MB
================================================================================
```

### Voorbeeld 5: Woo-analyse via MCP in Claude Desktop

**Vraag aan Claude:**
```
Analyseer de dataset 'parkeren' op Woo-relevantie
```

**Claude's response (gebruikt analyze_woo_connection tool):**
```
📊 WOO-ANALYSE VOOR DATASET
================================================================================
Dataset: Parkeertarieven Utrecht
ID: parkeren

🔍 GEËXTRAHEERDE TREFWOORDEN
────────────────────────────────────────────────────────────────────────────────
parkeren, tarieven, mobiliteit, verkeer

📌 GEMATCHTE ONDERWERPEN
────────────────────────────────────────────────────────────────────────────────
• verkeer
• mobiliteit
• openbare ruimte

✅ RELEVANTE WOO-CATEGORIEËN
────────────────────────────────────────────────────────────────────────────────

[1b] Jaarplannen en jaarverslagen
     → Kan onderdeel zijn van mobiliteitsplannen

[1c] Organisatie en werkwijze
     → Parkeerbeheer is onderdeel van gemeentelijke werkwijze

[3] Beschrijvingen van publieke informatie
     → Openbare tariefinformatie voor burgers

💡 AANBEVELINGEN
────────────────────────────────────────────────────────────────────────────────
Deze dataset bevat publieke tariefinformatie die relevant kan zijn voor:
- Mobiliteitsbeleid en parkeervisie (Woo 1b)
- Parkeerregelingen en handhavingsprotocollen (Woo 1c)
- Actieve openbaarmaking van tarieven (Woo 3)
```

## 🐛 Troubleshooting

### Web interface werkt niet

**Probleem:** Browser toont geen data of CORS error

**Oplossing:** Start de proxy server:
```bash
python3 proxy_server.py
```

Zorg dat je naar `http://localhost:8080` gaat (niet `file://`).

### Proxy server start niet

**Probleem:** Poort 8080 al in gebruik

**Oplossing:** Gebruik een andere poort:
```bash
python3 proxy_server.py -p 8888
```

Of check welk proces poort 8080 gebruikt:
```bash
lsof -i :8080
```

### Command-line tool: Connection Error

**Probleem:** Kan API niet bereiken

**Oplossing**Check internetverbinding en API status:
```bash
curl https://open.utrecht.nl/api/datasets
```

### Geen downloads beschikbaar

Sommige datasets hebben geen distributies. Probeer deze datasets die gegarandeerd downloads hebben:
- `afvalbakken` - CSV
- `bushaltes` - CSV
- `fietstellingen` - CSV

### Proxy server werkt niet
- Check of poort 8080 al in gebruik is: `lsof -i :8080`
- Probeer een andere poort: `python3 proxy_server.py -p 8888`
- Controleer of Python 3.6+ geïnstalleerd is: `python3 --version`

### MCP Server verbindt niet

**Probleem:** Claude Desktop ziet de server niet

**Oplossing:**
1. Check of het pad in de config correct is
2. Herstart Claude Desktop
3. Check de logs: `~/Library/Logs/Claude/mcp*.log`

## 🔗 Woo Integratie Details

### Hoe het werkt

De Woo-integratie gebruikt intelligente keyword extractie en topic mapping om datasets te koppelen aan Woo-categorieën:

1. **Keyword Extractie**: Haalt relevante termen uit dataset titel, beschrijving en keywords
2. **Topic Mapping**: Matcht keywords aan onderwerpen (bijv. "parkeren" → "verkeer", "mobiliteit")
3. **Categorie Matching**: Koppelt onderwerpen aan relevante Woo-categorieën
4. **Rapport Generatie**: Genereert leesbaar rapport met aanbevelingen

### Topic Mapping

De connector ondersteunt 20+ topic gebieden:
- Afval & Milieu
- Verkeer & Mobiliteit  
- Veiligheid & Handhaving
- Onderwijs & Jeugd
- Zorg & Welzijn
- Financiën & Economie
- Cultuur & Recreatie
- Ruimtelijke ordening
- En meer...

### Implementatie Details

De Woo-integratie is geïmplementeerd in `woo_connector.py`:

```python
from woo_connector import WooConnector

connector = WooConnector()
report = connector.generate_woo_report(dataset)
```

**Belangrijke methodes:**
- `extract_keywords(dataset)` - Haalt trefwoorden uit dataset
- `map_to_topics(keywords)` - Matcht keywords aan onderwerpen
- `analyze_dataset(dataset)` - Volledige analyse
- `generate_woo_report(dataset)` - Genereert leesbaar rapport

## 🔮 Toekomstige ontwikkelingen

### Woo Documenten & Dossiers

De gemeente Utrecht gaat metadata van Woo documenten en dossiers beschikbaar stellen via dezelfde API in vergelijkbaar DCAT formaat.

**Verwachte endpoints:**
- `/api/woo/documents` - Woo documenten
- `/api/woo/dossiers` - Woo dossiers

**Huidige status:**
- ✅ Woo-integratie met landelijke index operationeel
- ✅ MCP server met 6 tools beschikbaar
- 🔄 Wachten op Woo document API van gemeente Utrecht
- 📅 Command-line tool Woo subcommando's (gepland)
- 📅 Web interface Woo sectie (gepland)

## 📊 API Statistieken

Huidige productie data:
- **180** datasets beschikbaar
- DCAT formaat
- Verschillende distributie formaten: CSV, JSON, XML, GeoJSON

## 📄 Licentie

Dit is een tool voor gebruik met Open Data van de gemeente Utrecht.

**Data licentie:** Zie https://open.utrecht.nl voor voorwaarden van de data.

**Tool licentie:** Open source - vrij te gebruiken en aan te passen.

## 📞 Contact & Ondersteuning

**Voor vragen over de data:**
- Website: https://www.utrecht.nl
- Email: opendata@utrecht.nl
- Telefoon: 14 030

**Voor vragen over deze toolkit:**
- GitHub Issues (indien repository beschikbaar)
- Zie projectdocumentatie

## 🙏 Dankwoord

Data beschikbaar gesteld door de gemeente Utrecht via het Open Data portaal.

---

**Gemaakt met ❤️ voor Open Data**
