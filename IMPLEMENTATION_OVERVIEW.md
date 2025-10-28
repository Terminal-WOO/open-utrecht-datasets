# Utrecht Open Data - Implementatie Overzicht

## 📋 Project Samenvatting

Complete toolkit voor toegang tot de Utrecht Open Data API met intelligente Woo-integratie.

**Repository:** `https://github.com/Terminal-WOO/open-utrecht-datasets`  
**Status:** ✅ Volledig operationeel  
**Laatste update:** 2025-10-28

---

## 🎯 Wat is Gebouwd

### 1. Web Interface ✅
- Moderne browser applicatie voor dataset search en download
- CORS proxy server voor API toegang
- Modal interface met download functionaliteit
- Utrecht huisstijl styling

**Files:**
- `proxy_server.py` - Essential CORS proxy (port 8080)
- `index.html` - Complete web interface
- `app.js`, `style.css` - Legacy backups

**Start:** `python3 proxy_server.py` → http://localhost:8080

### 2. Command-line Tool ✅
- Python CLI voor automatisering
- Drie commands: search, get, formats
- Multiple output formats: table, json, compact

**File:** `utrecht_open_data.py`

**Gebruik:**
```bash
./utrecht_open_data.py search verkeer
./utrecht_open_data.py get afvalbakken
./utrecht_open_data.py formats bushaltes
```

### 3. MCP Server met Woo Integratie ✅
- Model Context Protocol server voor AI assistenten
- 6 tools beschikbaar (4 dataset + 2 Woo)
- Intelligente koppeling met landelijke Woo-index

**Files:**
- `mcp_server.py` - Main MCP server
- `woo_connector.py` - Woo integration module
- `test_mcp.py` - Test script
- `test_woo_mcp.py` - Woo integration test

**Configuratie Claude Desktop:**
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

### 4. Documentatie ✅
- `README.md` - Complete gebruikersdocumentatie (10KB+)
- `QUICKSTART.md` - Snelstart gids
- `PROJECT_SUMMARY.md` - Project overzicht
- `IMPLEMENTATION_OVERVIEW.md` - Dit document

---

## 🔧 Technische Architectuur

### API Endpoints
```
Base: https://open.utrecht.nl/api

GET /api/datasets                    # Lijst van datasets
GET /api/datasets/{id}               # Dataset details
GET /api/datasets/{id}/distributions # Download links
```

### DCAT Standaard
De API gebruikt DCAT (Data Catalog Vocabulary) met namespaced attributes:
- `dct:title` - Titel
- `dct:description` - Beschrijving
- `dcat:keyword` - Trefwoorden
- `dcat:accessURL` - Download URL

**Helper functions:**
- JavaScript: `getAttr(obj, key)` - Handles dct:/dcat:/foaf: prefixes
- Python: `get_attr(data, key)` - Same functionality

### CORS Oplossing
API heeft geen CORS headers → Proxy server nodig voor web interface

**proxy_server.py implementatie:**
```python
class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        super().end_headers()
    
    def do_GET(self):
        if self.path.startswith('/api/'):
            # Proxy to Utrecht API
            response = requests.get(f'https://open.utrecht.nl{self.path}')
            self.send_response(response.status_code)
            ...
```

---

## 🔗 Woo Integratie

### Overzicht
Intelligente koppeling tussen Utrecht datasets en 9 Woo-categorieën via keyword extraction en topic mapping.

### 9 Woo Categorieën
1. **1a**: Convenanten
2. **1b**: Jaarplannen en jaarverslagen
3. **1c**: Organisatie en werkwijze
4. **1d**: Bereikbaarheidsgegevens
5. **1e**: Subsidies en opdrachten
6. **1f**: Klachten en bezwaren
7. **1g**: Adviezen Wob en Woo verzoeken
8. **2**: Woo-besluiten
9. **3**: Beschrijvingen van publieke informatie
10. **4**: Aanvullende actieve openbaarmaking

### Werking
```python
# woo_connector.py flow:
1. extract_keywords(dataset)     # Haal trefwoorden uit dataset
2. map_to_topics(keywords)       # Match keywords → onderwerpen
3. analyze_dataset(dataset)      # Volledige analyse
4. generate_woo_report(dataset)  # Genereer leesbaar rapport
```

### Topic Mapping (20+ topics)
```python
TOPIC_MAPPING = {
    "afval": ["milieu", "openbare ruimte", "beheer"],
    "verkeer": ["mobiliteit", "infrastructuur", "veiligheid"],
    "parkeren": ["verkeer", "mobiliteit", "openbare ruimte"],
    "onderwijs": ["onderwijs", "jeugd", "ontwikkeling"],
    "zorg": ["gezondheid", "zorg", "welzijn"],
    # ... 15+ more topics
}
```

### MCP Tools

**Dataset Tools:**
1. `search_datasets` - Zoek datasets
2. `get_dataset` - Haal dataset details op
3. `get_distributions` - Haal downloads op
4. `list_all_datasets` - Toon alle datasets

**Woo Tools:**
5. `analyze_woo_connection` - Analyseer Woo-relevantie van dataset
6. `find_woo_related_datasets` - Zoek datasets voor Woo-onderwerp

### Voorbeeld Output
```
📊 WOO-ANALYSE VOOR DATASET
Dataset: Parkeertarieven Utrecht

🔍 GEËXTRAHEERDE TREFWOORDEN
parkeren, tarieven, mobiliteit, verkeer

📌 GEMATCHTE ONDERWERPEN
• verkeer
• mobiliteit
• openbare ruimte

✅ RELEVANTE WOO-CATEGORIEËN
[1b] Jaarplannen en jaarverslagen
     → Kan onderdeel zijn van mobiliteitsplannen

[1c] Organisatie en werkwijze
     → Parkeerbeheer is onderdeel van gemeentelijke werkwijze

[3] Beschrijvingen van publieke informatie
     → Openbare tariefinformatie voor burgers
```

---

## 🧪 Testing

### Web Interface Test
```bash
python3 proxy_server.py
# Open http://localhost:8080
# Zoek "verkeer"
# Klik op dataset
# Test downloads
```

### CLI Test
```bash
./utrecht_open_data.py search verkeer -n 5
./utrecht_open_data.py get afvalbakken -f json
./utrecht_open_data.py formats bushaltes
```

### MCP Server Test
```bash
# Basic test
python3 test_mcp.py

# Woo integration test
python3 test_woo_mcp.py
```

**Expected output:**
```
✅ Found 6 tools:
   - search_datasets
   - get_dataset
   - get_distributions
   - list_all_datasets
   - analyze_woo_connection
   - find_woo_related_datasets
✅ Woo analysis successful
✅ Woo search successful
```

---

## 📊 Development Timeline

### Phase 1: Basic API Access
- ✅ Explored API structure (DCAT format)
- ✅ Created CLI tool (utrecht_open_data.py)
- ✅ Implemented search, get, formats commands

### Phase 2: Web Interface
- ✅ Created initial web interface
- ✅ Fixed CORS issues with proxy server
- ✅ Implemented modal-based details view
- ✅ Added download functionality
- ✅ Fixed format extraction from URIs

### Phase 3: Documentation
- ✅ Created comprehensive README.md
- ✅ Created QUICKSTART.md
- ✅ Created PROJECT_SUMMARY.md

### Phase 4: MCP Server
- ✅ Implemented MCP server (4 dataset tools)
- ✅ Created test script
- ✅ Documented Claude Desktop integration

### Phase 5: Woo Integration
- ✅ Created woo_connector.py module
- ✅ Implemented keyword extraction
- ✅ Implemented topic mapping (20+ topics)
- ✅ Integrated into MCP server (2 new tools)
- ✅ Fixed indentation errors
- ✅ Created test_woo_mcp.py
- ✅ Updated all documentation

---

## 🐛 Problemen Opgelost

### 1. CORS Error (Web Interface)
**Probleem:** Browser kan API niet direct benaderen  
**Oorzaak:** API heeft geen CORS headers  
**Oplossing:** proxy_server.py met CORS headers  
**Status:** ✅ Opgelost

### 2. Click Functionaliteit
**Probleem:** Kan niet doorklikken op datasets  
**Oorzaak:** Ontbrekende event handlers en modal  
**Oplossing:** Volledig herschreven modal interface  
**Status:** ✅ Opgelost

### 3. Format Extractie
**Probleem:** Format toont "Onbekend"  
**Oorzaak:** API retourneert URIs (http://.../CSV)  
**Oplossing:** Extract format from URI split  
**Status:** ✅ Opgelost

### 4. MCP Indentation Errors
**Probleem:** IndentationError bij Woo methods  
**Oorzaak:** Methods appended buiten MCPServer class  
**Oplossing:** Python script om correct te inserteren  
**Status:** ✅ Opgelost

---

## 📦 Dependencies

```txt
requests>=2.31.0
mcp>=1.1.2
```

**Installatie:**
```bash
pip install -r requirements.txt
```

---

## 🚀 Quick Start

```bash
# 1. Clone/navigate to project
cd open-utrecht-datasets

# 2. Install dependencies
pip install -r requirements.txt

# 3A. Start web interface
python3 proxy_server.py
# → http://localhost:8080

# 3B. Use CLI
./utrecht_open_data.py search verkeer

# 3C. Start MCP server for Claude
python3 mcp_server.py
# Configure Claude Desktop (see README.md)
```

---

## 📈 Statistieken

- **180** datasets beschikbaar via API
- **9** Woo-categorieën ondersteund
- **20+** topic mappings geïmplementeerd
- **6** MCP tools beschikbaar
- **3** toegangsmethoden (Web, CLI, MCP)
- **10KB+** documentatie

---

## 🔮 Toekomst

### Korte Termijn (Gereed voor gebruik)
- ✅ Woo-integratie operationeel
- ✅ MCP server volledig functioneel
- ✅ Web interface werkend
- ✅ Documentatie compleet

### Middellange Termijn (Gepland)
- 📅 Woo document API van gemeente Utrecht
- 📅 CLI tool Woo subcommando's
- 📅 Web interface Woo sectie
- 📅 Extended topic mapping

### Lange Termijn (Optioneel)
- 📅 Real-time dataset monitoring
- 📅 Dataset change notifications
- 📅 Advanced filtering options
- 📅 Data quality metrics

---

## 📁 File Overzicht

```
utrecht/
├── README.md                    # 10KB+ complete documentatie ✅
├── QUICKSTART.md               # Snelstart gids ✅
├── PROJECT_SUMMARY.md          # Project overzicht ✅
├── IMPLEMENTATION_OVERVIEW.md  # Dit document ✅
│
├── requirements.txt            # Dependencies ✅
│
├── proxy_server.py            # CORS proxy (essential!) ✅
├── utrecht_open_data.py       # CLI tool ✅
├── mcp_server.py              # MCP server met Woo ✅
├── woo_connector.py           # Woo integratie module ✅
│
├── index.html                 # Web interface ✅
├── app.js                     # Legacy backup
├── style.css                  # Legacy backup
│
├── test_mcp.py               # MCP test script ✅
└── test_woo_mcp.py           # Woo integratie test ✅
```

**Status legenda:**
- ✅ Volledig operationeel
- 📄 Legacy/backup
- 🧪 Test script

---

## 🎓 Lessons Learned

### Technical
1. **CORS is kritisch** - Proxy server is essentieel voor web interfaces
2. **Namespace handling** - DCAT gebruikt dct:/dcat:/foaf: prefixes
3. **Error recovery** - Indentation bugs moeten zorgvuldig gefixed worden
4. **Testing** - Aparte test scripts per feature component

### Process
1. **Iterative development** - User feedback leidde tot multiple fixes
2. **Documentation matters** - Comprehensive docs helpen bij onboarding
3. **Modular design** - WooConnector als separate module werkt goed
4. **Integration testing** - test_woo_mcp.py valideerde volledige flow

---

## ✅ Deliverables Checklist

- [x] Web interface met CORS proxy
- [x] Command-line tool (search/get/formats)
- [x] MCP server met 4 dataset tools
- [x] Woo connector module
- [x] MCP server met 2 Woo tools
- [x] Comprehensive README.md
- [x] QUICKSTART.md guide
- [x] PROJECT_SUMMARY.md
- [x] Test scripts (test_mcp.py, test_woo_mcp.py)
- [x] Implementation overview (dit document)

---

## 🏁 Conclusie

Het Utrecht Open Data project is **volledig operationeel** met:

1. **3 toegangsmethoden**: Web, CLI, MCP
2. **Woo-integratie**: Intelligente dataset-document koppeling
3. **Complete documentatie**: README, quickstart, summaries
4. **Geteste implementatie**: Alle components getest en werkend

**Ready for use!** 🚀

---

*Document gegenereerd: 2025-10-28*  
*GitHub: https://github.com/Terminal-WOO/open-utrecht-datasets*  
*Status: Production Ready ✅*
