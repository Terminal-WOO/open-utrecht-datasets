#!/usr/bin/env python3
"""
Utrecht Open Data API Zoeksysteem

Een command-line tool om datasets te zoeken en op te halen van de
Open Data API van de gemeente Utrecht.
"""

import requests
import json
import argparse
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime


class UtrechtOpenDataAPI:
    """Client voor de Utrecht Open Data API."""

    BASE_URL = "https://open.utrecht.nl/api"

    def __init__(self, bearer_token: Optional[str] = None):
        """
        Initialiseer de API client.

        Args:
            bearer_token: Optionele bearer token voor authenticatie
        """
        self.bearer_token = bearer_token
        self.session = requests.Session()
        if bearer_token:
            self.session.headers.update({
                'Authorization': f'Bearer {bearer_token}'
            })

    def search_datasets(self,
                       query: Optional[str] = None,
                       start: int = 0,
                       limit: int = 20) -> Dict[str, Any]:
        """
        Zoek naar datasets in de catalogus.

        Args:
            query: Zoekterm (optioneel)
            start: Startpositie voor paginering
            limit: Maximaal aantal resultaten

        Returns:
            Dictionary met zoekresultaten
        """
        url = f"{self.BASE_URL}/datasets"
        params = {
            'start': start,
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Filter op zoekterm indien opgegeven
            if query and 'data' in data:
                filtered_data = []
                query_lower = query.lower()
                for dataset in data['data']:
                    # Zoek in titel, beschrijving en keywords
                    attributes = dataset.get('attributes', {})
                    title = attributes.get('title', '').lower()
                    description = attributes.get('description', '').lower()
                    keywords = ' '.join(attributes.get('keyword', [])).lower()

                    if (query_lower in title or
                        query_lower in description or
                        query_lower in keywords):
                        filtered_data.append(dataset)

                data['data'] = filtered_data

            return data

        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'data': []}

    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Haal details op van een specifieke dataset.

        Args:
            dataset_id: Het ID van de dataset

        Returns:
            Dictionary met dataset details
        """
        url = f"{self.BASE_URL}/datasets/{dataset_id}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def get_distributions(self, dataset_id: str) -> Dict[str, Any]:
        """
        Haal distributies (data formaten) op voor een dataset.

        Args:
            dataset_id: Het ID van de dataset

        Returns:
            Dictionary met distributies
        """
        url = f"{self.BASE_URL}/datasets/{dataset_id}/distributions"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'data': []}


class OutputFormatter:
    """Formatteer output in verschillende formaten."""

    @staticmethod
    def format_json(data: Any, pretty: bool = True) -> str:
        """Formatteer als JSON."""
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def format_table(datasets: List[Dict[str, Any]]) -> str:
        """Formatteer datasets als tabel."""
        if not datasets:
            return "Geen datasets gevonden."

        lines = []
        lines.append("=" * 80)
        lines.append(f"{'ID':<30} {'Titel':<50}")
        lines.append("=" * 80)

        for dataset in datasets:
            dataset_id = dataset.get('id', 'N/A')
            attributes = dataset.get('attributes', {})
            title = attributes.get('title', 'Geen titel')

            # Beperk lengte voor weergave
            if len(title) > 47:
                title = title[:44] + "..."

            lines.append(f"{dataset_id:<30} {title:<50}")

        lines.append("=" * 80)
        return "\n".join(lines)

    @staticmethod
    def format_detailed(dataset: Dict[str, Any]) -> str:
        """Formatteer een dataset in detail."""
        if 'error' in dataset:
            return f"Fout: {dataset['error']}"

        data = dataset.get('data', dataset)
        if isinstance(data, dict):
            attributes = data.get('attributes', {})
        else:
            attributes = data

        lines = []
        lines.append("=" * 80)
        lines.append(f"Dataset: {attributes.get('title', 'N/A')}")
        lines.append("=" * 80)
        lines.append(f"\nID: {data.get('id', 'N/A')}")
        lines.append(f"\nBeschrijving:\n{attributes.get('description', 'Geen beschrijving')}")

        if 'keyword' in attributes and attributes['keyword']:
            lines.append(f"\nKeywords: {', '.join(attributes['keyword'])}")

        if 'issued' in attributes:
            lines.append(f"\nGepubliceerd: {attributes['issued']}")

        if 'modified' in attributes:
            lines.append(f"Laatst gewijzigd: {attributes['modified']}")

        if 'publisher' in attributes:
            publisher = attributes['publisher']
            if isinstance(publisher, dict):
                lines.append(f"\nUitgever: {publisher.get('name', 'N/A')}")

        lines.append("=" * 80)
        return "\n".join(lines)

    @staticmethod
    def format_distributions(distributions: Dict[str, Any]) -> str:
        """Formatteer distributies (beschikbare formaten)."""
        if 'error' in distributions:
            return f"Fout: {distributions['error']}"

        data = distributions.get('data', [])
        if not data:
            return "Geen distributies gevonden."

        lines = []
        lines.append("=" * 80)
        lines.append("Beschikbare formaten:")
        lines.append("=" * 80)

        for i, dist in enumerate(data, 1):
            attributes = dist.get('attributes', {})
            lines.append(f"\n{i}. Formaat: {attributes.get('format', 'N/A')}")

            if 'title' in attributes:
                lines.append(f"   Titel: {attributes['title']}")

            if 'accessURL' in attributes:
                lines.append(f"   URL: {attributes['accessURL']}")

            if 'mediaType' in attributes:
                lines.append(f"   Media type: {attributes['mediaType']}")

            if 'byteSize' in attributes:
                size = attributes['byteSize']
                if isinstance(size, (int, float)):
                    size_mb = size / (1024 * 1024)
                    lines.append(f"   Grootte: {size_mb:.2f} MB")

        lines.append("=" * 80)
        return "\n".join(lines)


def main():
    """Hoofdfunctie voor de command-line interface."""
    parser = argparse.ArgumentParser(
        description='Utrecht Open Data API Zoeksysteem',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Voorbeelden:
  %(prog)s search verkeer                    # Zoek naar datasets over verkeer
  %(prog)s search "openbare ruimte" -n 10    # Zoek max 10 resultaten
  %(prog)s get DATASET_ID                    # Toon details van een dataset
  %(prog)s formats DATASET_ID                # Toon beschikbare formaten
  %(prog)s search verkeer -f json -o verkeer.json  # Exporteer naar JSON
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Beschikbare commando\'s')

    # Search command
    search_parser = subparsers.add_parser('search', help='Zoek naar datasets')
    search_parser.add_argument('query', nargs='?', help='Zoekterm')
    search_parser.add_argument('-n', '--limit', type=int, default=20,
                              help='Maximum aantal resultaten (standaard: 20)')
    search_parser.add_argument('-s', '--start', type=int, default=0,
                              help='Startpositie voor paginering (standaard: 0)')
    search_parser.add_argument('-f', '--format', choices=['table', 'json', 'compact'],
                              default='table', help='Output formaat (standaard: table)')
    search_parser.add_argument('-o', '--output', help='Output bestand (optioneel)')

    # Get command
    get_parser = subparsers.add_parser('get', help='Haal dataset details op')
    get_parser.add_argument('dataset_id', help='Dataset ID')
    get_parser.add_argument('-f', '--format', choices=['detail', 'json'],
                           default='detail', help='Output formaat (standaard: detail)')
    get_parser.add_argument('-o', '--output', help='Output bestand (optioneel)')

    # Formats command
    formats_parser = subparsers.add_parser('formats',
                                          help='Toon beschikbare formaten voor een dataset')
    formats_parser.add_argument('dataset_id', help='Dataset ID')
    formats_parser.add_argument('-f', '--format', choices=['detail', 'json'],
                               default='detail', help='Output formaat (standaard: detail)')
    formats_parser.add_argument('-o', '--output', help='Output bestand (optioneel)')

    # Global options
    parser.add_argument('--token', help='Bearer token voor authenticatie')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialiseer API client
    api = UtrechtOpenDataAPI(bearer_token=args.token)
    formatter = OutputFormatter()

    output = ""

    try:
        if args.command == 'search':
            # Zoek datasets
            results = api.search_datasets(
                query=args.query,
                start=args.start,
                limit=args.limit
            )

            if 'error' in results:
                print(f"Fout bij zoeken: {results['error']}", file=sys.stderr)
                sys.exit(1)

            datasets = results.get('data', [])

            if args.format == 'json':
                output = formatter.format_json(results)
            elif args.format == 'compact':
                output = formatter.format_json(results, pretty=False)
            else:  # table
                output = formatter.format_table(datasets)
                if datasets:
                    output += f"\n\nAantal resultaten: {len(datasets)}"

        elif args.command == 'get':
            # Haal dataset details op
            dataset = api.get_dataset(args.dataset_id)

            if 'error' in dataset:
                print(f"Fout bij ophalen dataset: {dataset['error']}", file=sys.stderr)
                sys.exit(1)

            if args.format == 'json':
                output = formatter.format_json(dataset)
            else:  # detail
                output = formatter.format_detailed(dataset)

        elif args.command == 'formats':
            # Haal distributies op
            distributions = api.get_distributions(args.dataset_id)

            if 'error' in distributions:
                print(f"Fout bij ophalen formaten: {distributions['error']}", file=sys.stderr)
                sys.exit(1)

            if args.format == 'json':
                output = formatter.format_json(distributions)
            else:  # detail
                output = formatter.format_distributions(distributions)

        # Output weergeven of opslaan
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Resultaten opgeslagen in: {args.output}")
        else:
            print(output)

    except KeyboardInterrupt:
        print("\n\nOnderbroken door gebruiker.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Onverwachte fout: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
