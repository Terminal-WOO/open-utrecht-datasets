# Data.overheid.nl Integratie

## 🎉 Overzicht

De Utrecht Open Data toolkit is uitgebreid met volledige ondersteuning voor **data.overheid.nl**, het nationale open data portaal van Nederland. Dit betekent toegang tot 10.000+ datasets van alle Nederlandse overheidsorganisaties!

## 🆕 Wat is er nieuw?

### 1. DataOverheid Python Module (`dataoverheid.py`)

Een complete Python module voor toegang tot de CKAN API van data.overheid.nl:

**Functionaliteit:**
- ✅ Zoeken naar datasets met filters
- ✅ Dataset details ophalen
- ✅ Organisaties lijst en details
- ✅ Tags en licenties
- ✅ Geformatteerde output voor CLI gebruik

**Voorbeeld gebruik:**
```python
from dataoverheid import DataOverheidConnector

connector = DataOverheidConnector()

# Zoek datasets
result = connector.search_datasets(
    query="klimaat",
    organization="cbs-opendata",
    rows=20
)

# Haal dataset op
dataset = connector.get_dataset("cbs-energie-kerncijfers")

# Lijst organisaties
orgs = connector.list_organizations(all_fields=True)
```

### 2. MCP Server Tools

De MCP server (`mcp_server.py`) heeft nu **4 nieuwe tools** voor data.overheid.nl:

| Tool | Beschrijving |
|------|-------------|
| `dataoverheid_search` | Zoek datasets met filters (query, organisatie, tags) |
| `dataoverheid_get_dataset` | Haal dataset details op inclusief resources |
| `dataoverheid_list_organizations` | Lijst van alle overheidsorganisaties |
| `dataoverheid_get_organization` | Organisatie details met datasets |

**Gebruik in Claude Desktop:**
```
Zoek datasets over "duurzaamheid" van CBS op data.overheid.nl
```

Claude gebruikt automatisch de `dataoverheid_search` tool met filters.

### 3. Proxy Server Ondersteuning

De CORS proxy server (`proxy_server.py`) ondersteunt nu beide APIs:

**Endpoints:**
- `http://localhost:8080/api/*` → Utrecht Open Data API
- `http://localhost:8080/dataoverheid/*` → Data.overheid.nl API
- `http://localhost:8080/woo/analyze/*` → Woo-analyse

**Voorbeeld:**
```bash
# Start proxy
python3 proxy_server.py

# Test data.overheid.nl
curl "http://localhost:8080/dataoverheid/package_search?q=utrecht&rows=5"
```

## 📊 Data Toegang

### Utrecht Open Data
- **Datasets**: ~180
- **Organisatie**: Gemeente Utrecht
- **Formaat**: DCAT
- **Update**: Realtime

### Data.overheid.nl  
- **Datasets**: 10.000+
- **Organisaties**: 100+ (CBS, gemeenten, ministeries, etc.)
- **Formaat**: CKAN (gestandaardiseerd)
- **Update**: Dagelijks

## 🏛️ Organisaties op data.overheid.nl

De belangrijkste organisaties met veel datasets:

1. **CBS OpenData** (5815 datasets)
   - Statistische data over Nederland
   - Economie, bevolking, gezondheid, etc.

2. **CBS Microdata** (1313 datasets)
   - Gedetailleerde microdata voor onderzoek

3. **Dataplatform** (1731 datasets)
   - Overheidsbrede datasets

4. **Gemeenten**
   - Gemeente Amsterdam (137 datasets)
   - Gemeente Utrecht (656 datasets via zoeken)
   - Gemeente Rotterdam, Den Haag, etc.

5. **Ministeries & Rijksdiensten**
   - DNB (De Nederlandsche Bank)
   - DUO (Dienst Uitvoering Onderwijs)
   - Rijkswaterstaat
   - RIVM

6. **Waterschappen & Provincies**

## 🔍 Zoek Mogelijkheden

### Basis zoeken
```python
# Alle datasets
result = connector.search_datasets(query="*", rows=100)

# Specifiek onderwerp
result = connector.search_datasets(query="klimaat", rows=20)
```

### Filteren op organisatie
```python
# Alleen CBS data
result = connector.search_datasets(
    organization="cbs-opendata",
    rows=50
)

# Gemeente Utrecht
result = connector.search_datasets(
    organization="gemeente-utrecht",
    rows=50
)
```

### Filteren op tags
```python
# Datasets met specifieke tags
result = connector.search_datasets(
    tags=["klimaat", "energie"],
    rows=20
)
```

### Combineren
```python
# Complex filter
result = connector.search_datasets(
    query="mobiliteit",
    organization="gemeente-amsterdam",
    tags=["verkeer"],
    rows=10
)
```

## 📖 API Endpoints

### CKAN API v3 Structuur

**Base URL**: `https://data.overheid.nl/data/api/3/action`

**Belangrijkste actions:**

1. **package_search** - Zoek datasets
   ```
   GET /package_search?q=klimaat&rows=10
   GET /package_search?fq=organization:"cbs-opendata"&rows=20
   ```

2. **package_show** - Dataset details
   ```
   GET /package_show?id=dataset-id
   ```

3. **organization_list** - Organisaties
   ```
   GET /organization_list?all_fields=true
   ```

4. **organization_show** - Organisatie met datasets
   ```
   GET /organization_show?id=cbs-opendata&include_datasets=true
   ```

5. **tag_list** - Alle tags
   ```
   GET /tag_list?all_fields=true
   ```

## 🚀 Aan de Slag

### 1. Test de module
```bash
python3 dataoverheid.py
```

Dit voert de ingebouwde tests uit.

### 2. Gebruik in eigen scripts
```python
from dataoverheid import DataOverheidConnector

connector = DataOverheidConnector()

# Zoek interessante datasets
result = connector.search_datasets(query="jouw onderwerp", rows=10)
print(connector.format_search_results(result))

# Haal details op
dataset = connector.get_dataset("dataset-id")
print(connector.format_dataset_summary(dataset))
```

### 3. Gebruik via MCP in Claude

1. Configureer MCP server in Claude Desktop
2. Vraag aan Claude:
   ```
   Zoek datasets over "duurzaamheid" op data.overheid.nl
   
   Toon mij alle organisaties met hun aantal datasets
   
   Haal de dataset "cbs-energie-kerncijfers" op
   ```

## 💡 Use Cases

### 1. Data Journalistiek
Vind datasets van verschillende overheidslagen voor onderzoeksjournalistiek:
```python
# Zoek datasets over specifiek onderwerp bij alle organisaties
result = connector.search_datasets(query="subsidie", rows=100)
```

### 2. Wetenschappelijk Onderzoek
Toegang tot CBS microdata en statistieken:
```python
result = connector.search_datasets(
    organization="cbs-microdata",
    rows=50
)
```

### 3. Gemeentelijke Vergelijking
Vergelijk datasets van verschillende gemeenten:
```python
# Zoek parkeerdata van alle gemeenten
result = connector.search_datasets(query="parkeren", rows=100)

# Filter op specifieke gemeente
utrecht = connector.search_datasets(
    query="parkeren",
    organization="gemeente-utrecht"
)
```

### 4. Open Data Portaal
Bouw je eigen open data portaal met data van meerdere bronnen:
- Utrecht Open Data (lokaal)
- Data.overheid.nl (landelijk)
- Woo-documenten (wet open overheid)

## 🔗 Vergelijking APIs

| Aspect | Utrecht Open Data | Data.overheid.nl |
|--------|------------------|------------------|
| **Datasets** | ~180 | 10.000+ |
| **Scope** | Gemeente Utrecht | Heel Nederland |
| **API Type** | DCAT | CKAN v3 |
| **Organisaties** | 1 (Utrecht) | 100+ |
| **Standaardisatie** | DCAT vocabulaire | CKAN standaard |
| **Update frequentie** | Realtime | Dagelijks |
| **Woo-integratie** | Ja | In ontwikkeling |

**Voordeel Utrecht API:**
- Specifiek voor Utrecht
- Woo-analyse integratie
- Direct DCAT formaat
- Realtime updates

**Voordeel Data.overheid.nl:**
- Landelijke dekking
- Veel meer datasets
- Gestandaardiseerde API
- Vergelijking tussen organisaties

## 📚 Documentatie

- **CKAN API Docs**: https://docs.ckan.org/en/latest/api/
- **Data.overheid.nl**: https://data.overheid.nl
- **API Docs NL**: https://docs.datacommunities.nl/
- **Utrecht Open Data**: https://open.utrecht.nl

## 🔮 Toekomst

Mogelijk toekomstige uitbreidingen:
- [ ] Web interface voor data.overheid.nl
- [ ] Command-line tool voor data.overheid.nl
- [ ] Cross-API zoeken (beide APIs tegelijk)
- [ ] Dataset vergelijkingstool
- [ ] Download manager voor grote datasets
- [ ] Automatische sync met lokale database

## ✅ Status

- ✅ Python module voor data.overheid.nl
- ✅ MCP server integratie (4 tools)
- ✅ Proxy server ondersteuning
- ✅ Documentatie
- ✅ Voorbeelden
- ⏳ Web interface (gepland)
- ⏳ CLI tool (gepland)

## 🎯 Conclusie

Met deze integratie heb je nu toegang tot:
- **10.180+ datasets** (180 Utrecht + 10.000+ landelijk)
- **100+ organisaties**
- **2 gestandaardiseerde APIs**
- **1 uniforme MCP interface**

Perfect voor data-analyse, onderzoek, journalistiek en AI-assistenten! 🚀
