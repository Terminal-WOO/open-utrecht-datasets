#!/usr/bin/env python3
"""
Data.overheid.nl Connector

Een integratie module voor toegang tot data.overheid.nl via de CKAN API.
Ondersteunt zoeken, filteren en ophalen van datasets van alle Nederlandse
overheidsorganisaties.

API documentatie: https://docs.ckan.org/en/latest/api/
Base URL: https://data.overheid.nl/data/api/3/action/
"""

import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any, Optional
import sys


class DataOverheidConnector:
    """Connector voor data.overheid.nl CKAN API"""

    def __init__(self):
        self.api_base = "https://data.overheid.nl/data/api/3/action"
        self.portal_base = "https://data.overheid.nl"

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Maak een API request"""
        url = f"{self.api_base}/{endpoint}"

        if params:
            # Filter None values
            params = {k: v for k, v in params.items() if v is not None}
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/json')
        req.add_header('User-Agent', 'DataOverheid-Connector/1.0')

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()
                result = json.loads(data.decode('utf-8'))

                if result.get('success'):
                    return result.get('result', {})
                else:
                    raise Exception(f"API error: {result.get('error', {}).get('message', 'Unknown error')}")
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"Connection error: {e.reason}")

    def search_datasets(self,
                       query: Optional[str] = None,
                       organization: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       rows: int = 20,
                       start: int = 0) -> Dict[str, Any]:
        """
        Zoek datasets op data.overheid.nl

        Args:
            query: Zoekterm voor fulltext search
            organization: Filter op organisatie naam of ID
            tags: Filter op tags/keywords
            rows: Aantal resultaten (max 1000)
            start: Offset voor paginering

        Returns:
            Dict met 'count' (totaal) en 'results' (datasets)
        """
        # Build filter query
        fq_parts = []

        if organization:
            fq_parts.append(f'organization:"{organization}"')

        if tags:
            for tag in tags:
                fq_parts.append(f'tags:"{tag}"')

        fq = ' AND '.join(fq_parts) if fq_parts else None

        params = {
            'q': query or '*:*',
            'fq': fq,
            'rows': min(rows, 1000),
            'start': start,
            'sort': 'score desc, metadata_modified desc'
        }

        result = self._make_request('package_search', params)

        return {
            'count': result.get('count', 0),
            'results': result.get('results', []),
            'facets': result.get('facets', {})
        }

    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Haal details van een specifieke dataset op

        Args:
            dataset_id: ID of name van de dataset

        Returns:
            Dataset details
        """
        params = {'id': dataset_id}
        return self._make_request('package_show', params)

    def list_organizations(self, all_fields: bool = False) -> List[Dict[str, Any]]:
        """
        Lijst van alle organisaties op data.overheid.nl

        Args:
            all_fields: Inclusief alle metadata (anders alleen name en title)

        Returns:
            List van organisaties
        """
        params = {'all_fields': all_fields}
        return self._make_request('organization_list', params)

    def get_organization(self, org_id: str, include_datasets: bool = False) -> Dict[str, Any]:
        """
        Details van een organisatie

        Args:
            org_id: ID of name van de organisatie
            include_datasets: Ook datasets ophalen

        Returns:
            Organisatie details
        """
        params = {
            'id': org_id,
            'include_datasets': include_datasets
        }
        return self._make_request('organization_show', params)

    def list_tags(self) -> List[Dict[str, Any]]:
        """Lijst van alle tags/keywords"""
        return self._make_request('tag_list', {'all_fields': True})

    def get_popular_datasets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Haal populaire datasets op (gesorteerd op views)

        Args:
            limit: Aantal datasets

        Returns:
            List van populaire datasets
        """
        result = self.search_datasets(rows=limit)
        return result['results']

    def search_by_license(self, license_id: str, rows: int = 20) -> Dict[str, Any]:
        """
        Zoek datasets op licentie

        Args:
            license_id: Licentie ID (bijv. 'cc-zero', 'cc-by-4.0')
            rows: Aantal resultaten

        Returns:
            Search resultaten
        """
        params = {
            'q': '*:*',
            'fq': f'license_id:"{license_id}"',
            'rows': rows,
            'sort': 'metadata_modified desc'
        }
        result = self._make_request('package_search', params)
        return {
            'count': result.get('count', 0),
            'results': result.get('results', [])
        }

    def get_dataset_url(self, dataset_name: str) -> str:
        """Genereer URL naar dataset pagina"""
        return f"{self.portal_base}/dataset/{dataset_name}"

    def get_resource_url(self, dataset_name: str, resource_id: str) -> str:
        """Genereer URL naar resource pagina"""
        return f"{self.portal_base}/dataset/{dataset_name}/resource/{resource_id}"

    def format_dataset_summary(self, dataset: Dict[str, Any]) -> str:
        """Formatteer dataset als readable text"""
        lines = []

        name = dataset.get('name', '')
        title = dataset.get('title', name)

        lines.append(f"📊 {title}")
        lines.append("=" * 70)
        lines.append(f"ID: {name}")
        lines.append(f"URL: {self.get_dataset_url(name)}")

        # Organisatie
        org = dataset.get('organization', {})
        if org:
            lines.append(f"Organisatie: {org.get('title', org.get('name', 'Onbekend'))}")

        # Beschrijving
        notes = dataset.get('notes', '')
        if notes:
            # Truncate lange beschrijvingen
            if len(notes) > 300:
                notes = notes[:297] + '...'
            lines.append(f"\nBeschrijving:\n{notes}")

        # Licentie
        license_title = dataset.get('license_title', '')
        if license_title:
            lines.append(f"\nLicentie: {license_title}")

        # Tags
        tags = dataset.get('tags', [])
        if tags:
            tag_names = [t.get('display_name', t.get('name', '')) for t in tags[:5]]
            lines.append(f"Tags: {', '.join(tag_names)}")

        # Resources
        resources = dataset.get('resources', [])
        if resources:
            lines.append(f"\n📦 Resources ({len(resources)}):")
            for i, res in enumerate(resources[:5], 1):
                res_name = res.get('name', 'Naamloos')
                res_format = res.get('format', 'Onbekend').upper()
                lines.append(f"  {i}. {res_name} ({res_format})")
                if res.get('url'):
                    lines.append(f"     URL: {res['url']}")

        # Metadata
        lines.append(f"\nAangemaakt: {dataset.get('metadata_created', 'Onbekend')[:10]}")
        lines.append(f"Gewijzigd: {dataset.get('metadata_modified', 'Onbekend')[:10]}")

        lines.append("=" * 70)
        return "\n".join(lines)

    def format_search_results(self, search_result: Dict[str, Any], compact: bool = False) -> str:
        """Formatteer zoekresultaten als readable text"""
        count = search_result.get('count', 0)
        results = search_result.get('results', [])

        lines = [f"Gevonden: {count} datasets", ""]

        if not results:
            lines.append("Geen resultaten gevonden.")
            return "\n".join(lines)

        for i, dataset in enumerate(results, 1):
            title = dataset.get('title', dataset.get('name', 'Geen titel'))
            name = dataset.get('name', '')

            if compact:
                org = dataset.get('organization', {})
                org_name = org.get('title', '') if org else ''
                lines.append(f"{i}. {title}")
                lines.append(f"   ID: {name} | Organisatie: {org_name}")
            else:
                lines.append(f"{i}. {title}")
                lines.append(f"   ID: {name}")

                notes = dataset.get('notes', '')
                if notes:
                    preview = notes[:150] + '...' if len(notes) > 150 else notes
                    lines.append(f"   {preview}")

                org = dataset.get('organization', {})
                if org:
                    lines.append(f"   Organisatie: {org.get('title', '')}")

                resources = dataset.get('resources', [])
                if resources:
                    formats = set(r.get('format', '').upper() for r in resources if r.get('format'))
                    lines.append(f"   Formaten: {', '.join(sorted(formats))}")

            lines.append("")

        return "\n".join(lines)


def main():
    """Test de DataOverheidConnector"""
    print("🔗 Testing Data.overheid.nl Connector\n")

    connector = DataOverheidConnector()

    # Test 1: Zoeken naar datasets
    print("TEST 1: Zoeken naar 'Utrecht' datasets")
    print("-" * 70)
    result = connector.search_datasets(query="Utrecht", rows=5)
    print(connector.format_search_results(result, compact=True))
    print()

    # Test 2: Organisaties
    print("TEST 2: Top 10 organisaties")
    print("-" * 70)
    try:
        orgs = connector.list_organizations(all_fields=True)[:10]
        for i, org in enumerate(orgs, 1):
            title = org.get('title', org.get('display_name', org.get('name', 'Onbekend')))
            package_count = org.get('package_count', 0)
            print(f"{i}. {title} ({package_count} datasets)")
    except Exception as e:
        print(f"Error: {e}")
    print()

    # Test 3: Dataset details
    print("TEST 3: Dataset details ophalen")
    print("-" * 70)
    if result['results']:
        first_dataset = result['results'][0]
        dataset_id = first_dataset['name']
        try:
            details = connector.get_dataset(dataset_id)
            print(connector.format_dataset_summary(details))
        except Exception as e:
            print(f"Error: {e}")

    print("\n✅ Tests completed")


if __name__ == "__main__":
    main()
