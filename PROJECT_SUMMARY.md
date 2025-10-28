# 📋 Utrecht Open Data - Project Samenvatting

## ✅ Wat is gemaakt

Een complete toolkit voor het werken met de Utrecht Open Data API (DCAT formaat).

## 🎯 Drie toegangsmethoden

### 1. Web Interface
- **Bestand:** `index.html`
- **Server:** `proxy_server.py` (verplicht - lost CORS op)
- **Features:**
  - Zoeken door datasets
  - Klikbare tegels met details
  - Downloads in verschillende formaten
  - Responsive design
  - Utrecht huisstijl (rood/wit)

**Gebruik:**
```bash
python3 proxy_server.py
# Open http://localhost:8080
```

### 2. Command-line Tool
- **Bestand:** `utrecht_open_data.py`
- **Features:**
  - Zoeken met filters
  - Dataset details ophalen
  - Formaten bekijken
  - Output in tabel/JSON/compact
  - Export naar bestanden

**Gebruik:**
```bash
./utrecht_open_data.py search verkeer
./utrecht_open_data.py get afvalbakken
./utrecht_open_data.py formats bushaltes
```

### 3. MCP Server
- **Bestand:** `mcp_server.py`
- **Features:**
  - Integratie met Claude en andere AI assistenten
  - 4 tools: search_datasets, get_dataset, get_distributions, list_all_datasets
  - Resources endpoint
  - Async/await voor performance

**Configuratie:**
```json
{
  "mcpServers": {
    "utrecht-opendata": {
      "command": "python3",
      "args": ["/pad/naar/mcp_server.py"]
    }
  }
}
```

## 📁 Bestandsstructuur

```
utrecht/
├── README.md                 # Complete documentatie
├── QUICKSTART.md            # Snelstart gids
├── PROJECT_SUMMARY.md       # Dit bestand
├── requirements.txt         # Python dependencies
│
├── proxy_server.py          # CORS proxy (verplicht voor web!)
├── index.html               # Web interface
├── app.js                   # JavaScript (legacy)
├── style.css                # CSS (legacy)
│
├── utrecht_open_data.py     # Command-line tool
├── mcp_server.py            # MCP server
├── test_mcp.py              # MCP test script
└── mcp_config_example.json  # MCP configuratie voorbeeld
```

## 🔑 Belangrijke concepten

### CORS Probleem
De Utrecht API heeft geen CORS headers, daarom:
- **Web interface** → Gebruik `proxy_server.py` (verplicht!)
- **Command-line** → Werkt direct (geen proxy nodig)
- **MCP server** → Werkt direct (geen proxy nodig)

### DCAT Formaat
De API gebruikt namespaced attributen:
- `dct:title` → Titel
- `dct:description` → Beschrijving
- `dcat:accessURL` → Download URL
- `dct:modified` → Laatste wijziging

Alle tools handelen dit automatisch af met `getAttr()` helpers.

### Distributies
Datasets kunnen meerdere "distributies" hebben (downloads):
- CSV
- JSON
- XML
- GeoJSON

Endpoint: `/api/datasets/{id}/distributions`

## 🎨 Design Beslissingen

1. **Proxy Server**
   - Noodzakelijk voor CORS
   - Simpel - erft van SimpleHTTPRequestHandler
   - Voegt headers toe + proxied API calls

2. **Web Interface**
   - Vanilla JavaScript (geen frameworks)
   - Single page application
   - Modal dialogs voor details
   - Utrecht kleuren (#cc0000 rood)

3. **MCP Server**
   - JSON-RPC 2.0 protocol
   - Stdio transport (stdin/stdout)
   - Async voor betere performance
   - Getest met test script

## 📊 API Statistieken

- **Base URL:** https://open.utrecht.nl/api
- **Datasets:** ~180 beschikbaar
- **Formaat:** DCAT (Data Catalog Vocabulary)
- **Toekomst:** Woo documenten en dossiers

## 🔮 Toekomstige uitbreidingen

Voorbereid voor Woo (Wet open overheid):
- `/api/woo/documents` (toekomstig)
- `/api/woo/dossiers` (toekomstig)

Aanpassingen nodig:
- MCP server: Nieuwe tools toevoegen
- Web interface: Woo sectie toevoegen
- Command-line: Woo subcommando's

## ✅ Getest & Werkend

### Web Interface ✓
- Datasets worden geladen
- Zoeken werkt
- Klikken op tegels opent details
- Downloads worden getoond
- Download knoppen werken

### Command-line ✓
- Search commando
- Get commando
- Formats commando
- JSON export

### MCP Server ✓
- Initialize ✓
- List tools ✓
- Call tools ✓
- List resources ✓
- Async operations ✓

## 📞 Support

**Data vragen:**
- Email: opendata@utrecht.nl
- Website: https://www.utrecht.nl
- Telefoon: 14 030

**API documentatie:**
- https://open.utrecht.nl/api
- OpenAPI spec: https://open.utrecht.nl/open-api-specification.json

## 🏆 Succesvol getest met

- **Datasets:** afvalbakken, bushaltes, fietstellingen
- **Formats:** CSV, JSON
- **Browsers:** Chrome, Safari
- **Python:** 3.13.3
- **MCP Protocol:** 2024-11-05

## 🎉 Klaar voor gebruik!

Alles is getest en werkend. De toolkit is klaar voor:
- Productie gebruik
- Uitbreidingen (Woo)
- Integratie in andere tools
- Educatief gebruik

---

**Gemaakt:** Oktober 2025  
**Versie:** 1.0.0  
**Status:** ✅ Production Ready
