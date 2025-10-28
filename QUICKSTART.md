# 🚀 Quickstart: Utrecht Open Data

## Kies je methode:

### 1️⃣ Web Interface (Eenvoudigst)

**Start de server:**
```bash
cd open-utrecht-datasets
python3 proxy_server.py
```

**Open in browser:**
```
http://localhost:8080
```

**Gebruik:**
- Zoek datasets
- Klik op een tegel voor details
- Download data met één klik

---

### 2️⃣ Command-line Tool

**Zoeken:**
```bash
./utrecht_open_data.py search verkeer
```

**Details bekijken:**
```bash
./utrecht_open_data.py get afvalbakken
```

**Downloads bekijken:**
```bash
./utrecht_open_data.py formats bushaltes
```

---

### 3️⃣ MCP Server (Voor AI Assistenten)

**Configuratie:**

Voeg toe aan `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

**Herstart Claude Desktop**

**Gebruik in Claude:**
```
Zoek naar datasets over verkeer in Utrecht
Geef me details van de dataset 'afvalbakken'
Welke downloads zijn er beschikbaar voor bushaltes?
```

---

## 🔧 Troubleshooting

### Web doet het niet?
```bash
# Check of server draait
ps aux | grep proxy_server

# Herstart server
pkill -f proxy_server
python3 proxy_server.py
```

### Command-line doet het niet?
```bash
# Maak executable
chmod +x utrecht_open_data.py

# Test
./utrecht_open_data.py search
```

### MCP server doet het niet?
```bash
# Test de server
python3 test_mcp.py

# Check Claude logs
tail -f ~/Library/Logs/Claude/mcp*.log
```

---

## 📊 Populaire Datasets

Probeer deze:
- `afvalbakken` - Locaties van afvalbakken (CSV)
- `bushaltes` - Bushalte locaties (CSV)
- `fietstellingen` - Fiets tellingen (CSV)
- `parkeren` - Parkeerdata
- `verkeer` - Verkeersdata

---

## 📞 Hulp Nodig?

**Data vragen:** opendata@utrecht.nl  
**Tool vragen:** Zie README.md  
**API docs:** https://open.utrecht.nl/api

---

**Veel plezier met Utrecht Open Data! 🏛️**
