#!/usr/bin/env python3
"""
Woo-Dataset Connector

Een intelligente tool die Utrecht Open Data datasets koppelt aan potentiële
Woo documenten en dossiers via keyword matching en topic analysis.

Aangezien de Woo-index nog geen publieke API heeft, gebruikt deze module:
1. Keyword extraction uit datasets
2. Topic mapping naar Woo categorieën
3. Suggesties voor gerelateerde Woo onderwerpen
"""

import re
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict
import urllib.request
import json


class WooConnector:
    """Koppelt datasets aan potentiële Woo documenten"""

    # Woo categorieën volgens de wet (Art 3.3 Woo)
    WOO_CATEGORIES = {
        "1a": "Convenanten",
        "1b": "Jaarplannen en jaarverslagen",
        "1c": "Onderzoeksrapporten",
        "1d": "Adviezen van adviescolleges",
        "1e": "Beschikkingen over aanvragen om een subsidie",
        "1f": "Beschikkingen Wob-verzoeken",
        "1g": "Beschikkingen Woo-verzoeken",
        "2": "Vergaderstukken bestuursorganen",
        "3": "Bestuurlijke besluiten",
        "4": "Regelingen en beleidsnota's"
    }

    # Topic mapping: dataset keywords → Woo topics
    TOPIC_MAPPING = {
        # Ruimtelijke ordening & Infrastructuur
        "afval": ["milieu", "openbare ruimte", "beheer", "huisvesting"],
        "parkeren": ["verkeer", "mobiliteit", "openbare ruimte", "handhaving"],
        "verkeer": ["mobiliteit", "infrastructuur", "veiligheid", "openbare ruimte"],
        "bus": ["openbaar vervoer", "mobiliteit", "infrastructuur"],
        "fiets": ["mobiliteit", "infrastructuur", "openbare ruimte"],
        "straat": ["openbare ruimte", "beheer", "infrastructuur"],
        "woning": ["huisvesting", "ruimtelijke ordening", "bouw"],
        "bouw": ["ruimtelijke ordening", "vergunningen", "handhaving"],

        # Sociale zaken
        "jeugd": ["jeugdzorg", "welzijn", "onderwijs", "zorg"],
        "zorg": ["gezondheidszorg", "welzijn", "sociaal domein"],
        "onderwijs": ["educatie", "jeugd", "cultuur"],
        "werk": ["arbeidsmarkt", "economie", "sociale zaken"],

        # Milieu & Duurzaamheid
        "milieu": ["duurzaamheid", "klimaat", "natuur"],
        "energie": ["duurzaamheid", "klimaat", "milieu"],
        "water": ["waterbeheer", "milieu", "infrastructuur"],
        "groen": ["natuur", "openbare ruimte", "milieu"],

        # Veiligheid & Handhaving
        "veiligheid": ["openbare orde", "handhaving", "politie"],
        "criminaliteit": ["veiligheid", "politie", "handhaving"],
        "overlast": ["openbare orde", "handhaving", "veiligheid"],

        # Bestuur & Organisatie
        "subsidie": ["financiën", "beleid", "ondersteuning"],
        "beleid": ["bestuur", "regelgeving", "strategie"],
        "financiën": ["begroting", "subsidie", "economie"],
        "vergunning": ["handhaving", "regelgeving", "bouw"],
    }

    # Woo-index URL per organisatie
    WOO_INDEX_BASE = "https://organisaties.overheid.nl"
    UTRECHT_WOO_URL = f"{WOO_INDEX_BASE}/woo/nl.oorg.gemutrecht_gemeente"

    def __init__(self):
        self.dataset_topics = defaultdict(set)
        self.topic_datasets = defaultdict(list)

    def extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords uit tekst"""
        if not text:
            return set()

        # Lowercase en split op niet-alfanumeriek
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter stopwords (basis Nederlandse stopwords)
        stopwords = {
            'de', 'het', 'een', 'van', 'in', 'op', 'voor', 'met', 'aan',
            'uit', 'en', 'of', 'maar', 'is', 'zijn', 'was', 'waren',
            'deze', 'dit', 'die', 'dat', 'door', 'naar', 'bij', 'om',
            'te', 'tot', 'over', 'onder', 'tussen', 'na', 'als', 'dan'
        }

        keywords = {w for w in words if len(w) > 3 and w not in stopwords}
        return keywords

    def map_to_topics(self, keywords: Set[str]) -> Set[str]:
        """Map keywords naar Woo topics"""
        topics = set()

        for keyword in keywords:
            # Zoek in topic mapping
            for key, topic_list in self.TOPIC_MAPPING.items():
                if key in keyword or keyword in key:
                    topics.update(topic_list)

        return topics

    def analyze_dataset(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Analyseer een dataset voor Woo koppeling"""
        attrs = dataset.get('attributes', {})

        # Haal data op
        title = self._get_attr(attrs, 'title') or ''
        description = self._get_attr(attrs, 'description') or ''
        keywords_raw = self._get_attr(attrs, 'keyword') or []
        dataset_id = dataset.get('id', '')

        # Extract keywords
        text = f"{title} {description} {' '.join(keywords_raw)}"
        keywords = self.extract_keywords(text)

        # Map naar topics
        topics = self.map_to_topics(keywords)

        # Bepaal relevante Woo categorieën
        woo_categories = self._suggest_woo_categories(keywords, topics)

        # Genereer zoeksuggesties voor Woo-index
        search_terms = self._generate_search_terms(keywords, topics)

        return {
            'dataset_id': dataset_id,
            'title': title,
            'keywords': list(keywords)[:10],  # Top 10
            'topics': list(topics),
            'woo_categories': woo_categories,
            'woo_search_terms': search_terms,
            'woo_index_url': self.UTRECHT_WOO_URL,
            'relevance_score': len(topics) + len(woo_categories)
        }

    def _suggest_woo_categories(self, keywords: Set[str], topics: Set[str]) -> List[Dict[str, str]]:
        """Suggereer relevante Woo categorieën"""
        suggestions = []

        # Keyword-based matching
        category_keywords = {
            "1a": ["convenant", "overeenkomst", "samenwerkings"],
            "1b": ["jaarplan", "jaarverslag", "begroting"],
            "1c": ["onderzoek", "rapport", "evaluatie", "studie"],
            "1d": ["advies", "aanbeveling", "commissie"],
            "1e": ["subsidie", "financiering", "ondersteuning"],
            "1f": ["wob", "openbaarmaking"],
            "1g": ["woo", "openbaarmaking"],
            "2": ["vergader", "raad", "commissie", "besluit"],
            "3": ["besluit", "beschikking", "verordening"],
            "4": ["beleid", "regeling", "verordening", "nota"]
        }

        for cat_id, cat_keywords in category_keywords.items():
            for kw in keywords:
                if any(ck in kw for ck in cat_keywords):
                    suggestions.append({
                        'category': cat_id,
                        'name': self.WOO_CATEGORIES[cat_id],
                        'reason': f"Bevat keyword: {kw}"
                    })
                    break

        # Topic-based suggestions
        if any(t in topics for t in ['beleid', 'regelgeving', 'bestuur']):
            suggestions.append({
                'category': '4',
                'name': self.WOO_CATEGORIES['4'],
                'reason': 'Gerelateerd aan beleid en regelgeving'
            })

        if any(t in topics for t in ['subsidie', 'financiën']):
            suggestions.append({
                'category': '1e',
                'name': self.WOO_CATEGORIES['1e'],
                'reason': 'Gerelateerd aan subsidies'
            })

        # Verwijder duplicaten
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            key = s['category']
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(s)

        return unique_suggestions

    def _generate_search_terms(self, keywords: Set[str], topics: Set[str]) -> List[str]:
        """Genereer zoektermen voor Woo-index"""
        terms = []

        # Gebruik top keywords
        sorted_keywords = sorted(keywords, key=len, reverse=True)[:5]
        terms.extend(sorted_keywords)

        # Voeg topics toe
        terms.extend(list(topics)[:3])

        # Maak uniek en return
        return list(dict.fromkeys(terms))  # Preserves order

    def _get_attr(self, obj: dict, key: str) -> Any:
        """Get attribute met namespace support"""
        return obj.get(f"dct:{key}") or obj.get(f"dcat:{key}") or obj.get(key)

    def find_related_datasets(self, woo_topic: str, datasets: List[Dict]) -> List[Dict]:
        """Vind datasets gerelateerd aan een Woo onderwerp"""
        related = []
        topic_lower = woo_topic.lower()

        for dataset in datasets:
            analysis = self.analyze_dataset(dataset)

            # Check if topic matches
            if any(topic_lower in str(t).lower() for t in analysis['topics']):
                related.append({
                    'dataset': dataset,
                    'analysis': analysis,
                    'relevance': analysis['relevance_score']
                })
            elif any(topic_lower in str(k).lower() for k in analysis['keywords']):
                related.append({
                    'dataset': dataset,
                    'analysis': analysis,
                    'relevance': analysis['relevance_score'] - 1
                })

        # Sort by relevance
        related.sort(key=lambda x: x['relevance'], reverse=True)
        return related

    def generate_woo_report(self, dataset: Dict[str, Any]) -> str:
        """Genereer een rapport over mogelijke Woo koppelingen"""
        analysis = self.analyze_dataset(dataset)

        report = []
        report.append("=" * 70)
        report.append(f"WOO KOPPELING ANALYSE: {analysis['title']}")
        report.append("=" * 70)
        report.append("")

        report.append(f"Dataset ID: {analysis['dataset_id']}")
        report.append(f"Relevantie score: {analysis['relevance_score']}/10")
        report.append("")

        report.append("GEÏDENTIFICEERDE ONDERWERPEN:")
        if analysis['topics']:
            for topic in analysis['topics']:
                report.append(f"  • {topic}")
        else:
            report.append("  (geen specifieke onderwerpen gevonden)")
        report.append("")

        report.append("GERELATEERDE WOO CATEGORIEËN:")
        if analysis['woo_categories']:
            for cat in analysis['woo_categories']:
                report.append(f"  • {cat['category']} - {cat['name']}")
                report.append(f"    Reden: {cat['reason']}")
        else:
            report.append("  (geen directe categorieën gevonden)")
        report.append("")

        report.append("AANBEVOLEN ZOEKTERMEN VOOR WOO-INDEX:")
        for term in analysis['woo_search_terms']:
            report.append(f"  • {term}")
        report.append("")

        report.append("WOO-INDEX LINKS:")
        report.append(f"  Gemeente Utrecht: {analysis['woo_index_url']}")
        report.append("")

        report.append("HOE TE GEBRUIKEN:")
        report.append("  1. Bezoek de Woo-index URL hierboven")
        report.append("  2. Zoek naar de aanbevolen zoektermen")
        report.append("  3. Filter op de relevante Woo categorieën")
        report.append("  4. Vergelijk gevonden documenten met deze dataset")
        report.append("")

        report.append("=" * 70)

        return "\n".join(report)


def main():
    """Test de WooConnector"""
    import sys

    # Voorbeeld dataset
    example_dataset = {
        'id': 'afvalbakken',
        'attributes': {
            'dct:title': 'Afvalbakken',
            'dct:description': 'Overzicht van bovengrondse afvalbakken in de gemeente Utrecht voor afvalbeleid',
            'dcat:keyword': ['afval', 'afvalbak', 'openbare ruimte']
        }
    }

    connector = WooConnector()

    print("🔗 Testing Woo-Dataset Connector\n")

    # Analyseer dataset
    analysis = connector.analyze_dataset(example_dataset)

    print("ANALYSE RESULTAAT:")
    print(f"  Topics: {', '.join(analysis['topics'])}")
    print(f"  Woo categorieën: {len(analysis['woo_categories'])}")
    print(f"  Zoektermen: {', '.join(analysis['woo_search_terms'])}")
    print(f"  Relevantie: {analysis['relevance_score']}/10")
    print()

    # Genereer rapport
    report = connector.generate_woo_report(example_dataset)
    print(report)


if __name__ == "__main__":
    main()
