# Utrecht Open Data - GitHub Pages

Dit is de vereenvoudigde GitHub Pages versie van de Utrecht Open Data toolkit.

## 🌐 Live Demo

Deze versie draait op: **https://terminal-woo.github.io/open-utrecht-datasets/**

## ✨ Functionaliteit

Deze GitHub Pages versie bevat:

- ✅ **Utrecht Open Data** - 180 datasets van gemeente Utrecht
- ✅ Zoeken door alle datasets
- ✅ Dataset details bekijken
- ✅ Directe downloads (CSV, JSON, XML, etc.)
- ✅ Responsive design voor desktop en mobiel
- ✅ 100% client-side (geen server nodig!)

## 🔍 Wat ontbreekt?

Deze versie bevat **NIET**:

- ❌ Data.overheid.nl integratie (10.000+ landelijke datasets)
- ❌ Woo-analyse functionaliteit
- ❌ MCP server tools
- ❌ Organisatie filtering

**Waarom?** data.overheid.nl API heeft geen CORS headers, dus werkt niet in de browser zonder proxy server.

## 💻 Wil je de volledige versie?

Download de complete toolkit met:
- ✅ 10.000+ landelijke datasets (data.overheid.nl)
- ✅ Woo-analyse integratie
- ✅ MCP server met 10 tools voor AI assistenten
- ✅ CORS proxy server
- ✅ Python modules voor automatisering

**GitHub**: https://github.com/Terminal-WOO/open-utrecht-datasets

### Installatie volledige versie:

```bash
# Clone repository
git clone https://github.com/Terminal-WOO/open-utrecht-datasets.git
cd open-utrecht-datasets

# Installeer dependencies
pip install -r requirements.txt

# Start proxy server
python3 proxy_server.py

# Open browser
open http://localhost:8080
```

Nu heb je toegang tot **beide** APIs met volledige functionaliteit!

## 🛠️ Technische Details

Deze GitHub Pages versie:
- Gebruikt directe API calls naar `https://open.utrecht.nl/api`
- Utrecht Open Data API heeft CORS ondersteuning
- Pure vanilla JavaScript (geen frameworks)
- Statische HTML/CSS/JS
- Werkt zonder server

## 📖 API Documentatie

- **Utrecht Open Data**: https://open.utrecht.nl
- **GitHub Repository**: https://github.com/Terminal-WOO/open-utrecht-datasets
- **Volledige documentatie**: Zie README.md in de repository

## 🎯 Use Cases

Gebruik deze GitHub Pages versie voor:
- 🔍 Snel zoeken in Utrecht datasets
- 📊 Dataset exploratie en ontdekking
- 📥 Directe data downloads
- 📱 Mobiele toegang
- 🔗 Delen van datasets via URLs

## 📞 Contact & Issues

Voor vragen, bugs of feature requests:
- **GitHub Issues**: https://github.com/Terminal-WOO/open-utrecht-datasets/issues
- **Repository**: https://github.com/Terminal-WOO/open-utrecht-datasets

---

**Gemaakt met ❤️ voor Open Data**  
Data beschikbaar gesteld door de gemeente Utrecht
