#!/usr/bin/env python3
"""
Utrecht Open Data MCP Server

Een Model Context Protocol server voor toegang tot de Utrecht Open Data API.
Ondersteunt DCAT datasets en (toekomstig) Woo documenten en dossiers.
"""

import asyncio
import json
import sys
from typing import Any, Optional, List
import urllib.request
import urllib.error

# Import Woo connector and DataOverheid connector
try:
    from woo_connector import WooConnector
except ImportError:
    WooConnector = None

try:
    from dataoverheid import DataOverheidConnector
except ImportError:
    DataOverheidConnector = None

# MCP Protocol
class MCPServer:
    """Utrecht Open Data MCP Server"""

    def __init__(self):
        self.api_base = "https://open.utrecht.nl/api"
        self.version = "1.1.0"
        self.woo_connector = WooConnector() if WooConnector else None
        self.dataoverheid = DataOverheidConnector() if DataOverheidConnector else None

    async def handle_request(self, request: dict) -> dict:
        """Handle incoming MCP requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                return self.initialize(request_id, params)
            elif method == "tools/list":
                return self.list_tools(request_id)
            elif method == "tools/call":
                return await self.call_tool(request_id, params)
            elif method == "resources/list":
                return self.list_resources(request_id)
            elif method == "resources/read":
                return await self.read_resource(request_id, params)
            else:
                return self.error_response(request_id, -32601, f"Method not found: {method}")
        except Exception as e:
            return self.error_response(request_id, -32603, str(e))

    def initialize(self, request_id: Any, params: dict) -> dict:
        """Initialize MCP server"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "utrecht-opendata",
                    "version": self.version
                }
            }
        }

    def list_tools(self, request_id: Any) -> dict:
        """List available tools"""
        tools = [
            {
                "name": "search_datasets",
                "description": "Zoek naar datasets in de Utrecht Open Data catalogus. Ondersteunt zoeken op trefwoorden in titel, beschrijving en tags.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Zoekterm (optioneel). Laat leeg voor alle datasets."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum aantal resultaten (standaard 20)",
                            "default": 20
                        }
                    }
                }
            },
            {
                "name": "get_dataset",
                "description": "Haal volledige details op van een specifieke dataset inclusief metadata, uitgever, licentie en publicatiedatum.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset_id": {
                            "type": "string",
                            "description": "Het unieke ID van de dataset"
                        }
                    },
                    "required": ["dataset_id"]
                }
            },
            {
                "name": "get_distributions",
                "description": "Haal beschikbare downloads (distributies) op voor een dataset. Toont formaten (CSV, JSON, XML) en download URLs.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset_id": {
                            "type": "string",
                            "description": "Het unieke ID van de dataset"
                        }
                    },
                    "required": ["dataset_id"]
                }
            },
            {
                "name": "list_all_datasets",
                "description": "Toon een overzicht van alle beschikbare datasets met basis informatie.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "analyze_woo_connection",
                "description": "Analyseer een dataset en vind mogelijke koppelingen met Woo documenten. Geeft Woo categorieën, zoektermen en relevantie score.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset_id": {
                            "type": "string",
                            "description": "Het unieke ID van de dataset"
                        }
                    },
                    "required": ["dataset_id"]
                }
            },
            {
                "name": "find_woo_related_datasets",
                "description": "Vind datasets die gerelateerd zijn aan een specifiek Woo onderwerp of keyword.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Woo onderwerp of keyword (bijv. 'milieu', 'subsidie', 'verkeer')"
                        }
                    },
                    "required": ["topic"]
                }
            },
            # Data.overheid.nl tools
            {
                "name": "dataoverheid_search",
                "description": "Zoek datasets op data.overheid.nl van alle Nederlandse overheidsorganisaties. Ondersteunt filteren op organisatie en tags.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Zoekterm voor fulltext search (optioneel)"
                        },
                        "organization": {
                            "type": "string",
                            "description": "Filter op organisatie naam (bijv. 'gemeente-utrecht')"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter op tags/keywords"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum aantal resultaten (standaard 20, max 100)",
                            "default": 20
                        }
                    }
                }
            },
            {
                "name": "dataoverheid_get_dataset",
                "description": "Haal details op van een specifieke dataset van data.overheid.nl inclusief alle resources en metadata.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset_id": {
                            "type": "string",
                            "description": "Het unieke ID of name van de dataset"
                        }
                    },
                    "required": ["dataset_id"]
                }
            },
            {
                "name": "dataoverheid_list_organizations",
                "description": "Lijst van alle overheidsorganisaties op data.overheid.nl met aantal datasets.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum aantal organisaties (standaard 50)",
                            "default": 50
                        }
                    }
                }
            },
            {
                "name": "dataoverheid_get_organization",
                "description": "Details van een specifieke overheidsorganisatie inclusief datasets.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "org_id": {
                            "type": "string",
                            "description": "ID of name van de organisatie"
                        },
                        "include_datasets": {
                            "type": "boolean",
                            "description": "Ook datasets ophalen (standaard false)",
                            "default": false
                        }
                    },
                    "required": ["org_id"]
                }
            }
        ]

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }

    async def call_tool(self, request_id: Any, params: dict) -> dict:
        """Execute a tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "search_datasets":
                result = await self.search_datasets(
                    arguments.get("query"),
                    arguments.get("limit", 20)
                )
            elif tool_name == "get_dataset":
                result = await self.get_dataset(arguments["dataset_id"])
            elif tool_name == "get_distributions":
                result = await self.get_distributions(arguments["dataset_id"])
            elif tool_name == "list_all_datasets":
                result = await self.list_all_datasets()
            elif tool_name == "analyze_woo_connection":
                result = await self.analyze_woo_connection(arguments["dataset_id"])
            elif tool_name == "find_woo_related_datasets":
                result = await self.find_woo_related_datasets(arguments["topic"])
            # Data.overheid.nl tools
            elif tool_name == "dataoverheid_search":
                result = await self.dataoverheid_search(
                    arguments.get("query"),
                    arguments.get("organization"),
                    arguments.get("tags"),
                    arguments.get("limit", 20)
                )
            elif tool_name == "dataoverheid_get_dataset":
                result = await self.dataoverheid_get_dataset(arguments["dataset_id"])
            elif tool_name == "dataoverheid_list_organizations":
                result = await self.dataoverheid_list_organizations(arguments.get("limit", 50))
            elif tool_name == "dataoverheid_get_organization":
                result = await self.dataoverheid_get_organization(
                    arguments["org_id"],
                    arguments.get("include_datasets", False)
                )
            else:
                return self.error_response(request_id, -32602, f"Unknown tool: {tool_name}")

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
        except Exception as e:
            return self.error_response(request_id, -32603, f"Tool execution failed: {str(e)}")

    def list_resources(self, request_id: Any) -> dict:
        """List available resources"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": [
                    {
                        "uri": "utrecht://datasets",
                        "name": "Utrecht Open Datasets",
                        "description": "Complete lijst van alle datasets",
                        "mimeType": "application/json"
                    }
                ]
            }
        }

    async def read_resource(self, request_id: Any, params: dict) -> dict:
        """Read a resource"""
        uri = params.get("uri")

        if uri == "utrecht://datasets":
            data = await self.fetch_api("/datasets")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(data, indent=2)
                        }
                    ]
                }
            }
        else:
            return self.error_response(request_id, -32602, f"Unknown resource: {uri}")

    def error_response(self, request_id: Any, code: int, message: str) -> dict:
        """Generate error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    async def fetch_api(self, endpoint: str, timeout: int = 30) -> dict:
        """Fetch data from API"""
        url = f"{self.api_base}{endpoint}"

        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/json')
        req.add_header('User-Agent', 'Utrecht-OpenData-MCP/1.0')

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: urllib.request.urlopen(req, timeout=timeout)
        )

        data = response.read()
        return json.loads(data.decode('utf-8'))

    def get_attr(self, obj: dict, key: str) -> Any:
        """Get attribute with namespace support"""
        if f"dct:{key}" in obj:
            return obj[f"dct:{key}"]
        if f"dcat:{key}" in obj:
            return obj[f"dcat:{key}"]
        if f"foaf:{key}" in obj:
            return obj[f"foaf:{key}"]
        if key in obj:
            return obj[key]
        return None

    async def search_datasets(self, query: Optional[str] = None, limit: int = 20) -> str:
        """Search datasets"""
        data = await self.fetch_api("/datasets")
        datasets = data.get("data", [])

        if query:
            query_lower = query.lower()
            datasets = [
                ds for ds in datasets
                if query_lower in self.get_attr(ds.get("attributes", {}), "title", "").lower()
                or query_lower in self.get_attr(ds.get("attributes", {}), "description", "").lower()
                or query_lower in ds.get("id", "").lower()
            ]

        datasets = datasets[:limit]

        result = f"Gevonden: {len(datasets)} datasets\n\n"

        for ds in datasets:
            attrs = ds.get("attributes", {})
            title = self.get_attr(attrs, "title") or ds.get("id", "Geen titel")
            desc = self.get_attr(attrs, "description") or "Geen beschrijving"

            result += f"📊 {title}\n"
            result += f"   ID: {ds.get('id')}\n"
            result += f"   {desc[:100]}{'...' if len(desc) > 100 else ''}\n\n"

        return result

    async def get_dataset(self, dataset_id: str) -> str:
        """Get dataset details"""
        data = await self.fetch_api(f"/datasets/{dataset_id}")
        dataset = data.get("data", data)

        attrs = dataset.get("attributes", {})
        title = self.get_attr(attrs, "title") or dataset_id
        desc = self.get_attr(attrs, "description") or "Geen beschrijving"
        modified = self.get_attr(attrs, "modified")
        issued = self.get_attr(attrs, "issued")
        publisher = self.get_attr(attrs, "publisher")
        keywords = self.get_attr(attrs, "keyword") or []

        result = f"📊 {title}\n"
        result += f"{'=' * 60}\n\n"
        result += f"ID: {dataset_id}\n\n"
        result += f"Beschrijving:\n{desc}\n\n"

        if keywords:
            result += f"Keywords: {', '.join(keywords)}\n\n"

        if publisher:
            pub_name = publisher.get("name") if isinstance(publisher, dict) else publisher
            result += f"Uitgever: {pub_name}\n"

        if issued:
            result += f"Gepubliceerd: {issued}\n"

        if modified:
            result += f"Laatst gewijzigd: {modified}\n"

        return result

    async def get_distributions(self, dataset_id: str) -> str:
        """Get distributions for dataset"""
        try:
            data = await self.fetch_api(f"/datasets/{dataset_id}/distributions")
            distributions = data.get("data", [])

            if not distributions:
                return "Geen downloads beschikbaar voor deze dataset."

            result = f"Beschikbare downloads voor {dataset_id}:\n\n"

            for i, dist in enumerate(distributions, 1):
                attrs = dist.get("attributes", {})

                format_raw = self.get_attr(attrs, "format") or "Onbekend"
                if "/" in format_raw:
                    format_name = format_raw.split("/")[-1].upper()
                else:
                    format_name = format_raw

                title = self.get_attr(attrs, "title") or format_name
                access_url = self.get_attr(attrs, "accessURL")

                result += f"{i}. Formaat: {format_name}\n"
                result += f"   Titel: {title}\n"

                if access_url:
                    result += f"   URL: {access_url}\n"

                result += "\n"

            return result

        except Exception as e:
            return f"Fout bij ophalen distributies: {str(e)}"

    async def list_all_datasets(self) -> str:
        """List all datasets"""
        data = await self.fetch_api("/datasets")
        datasets = data.get("data", [])
        meta = data.get("meta", {})

        result = f"Totaal aantal datasets: {meta.get('total', len(datasets))}\n\n"

        for ds in datasets[:50]:  # Limiteer tot 50 voor overzicht
            attrs = ds.get("attributes", {})
            title = self.get_attr(attrs, "title") or ds.get("id", "Geen titel")
            result += f"📊 {title} (ID: {ds.get('id')})\n"

        if len(datasets) > 50:
            result += f"\n... en nog {len(datasets) - 50} datasets meer\n"

        return result



    async def analyze_woo_connection(self, dataset_id: str) -> str:
        """Analyseer Woo koppeling voor een dataset"""
        if not self.woo_connector:
            return "⚠️ Woo connector niet beschikbaar"

        try:
            data = await self.fetch_api(f"/datasets/{dataset_id}")
            dataset = data.get("data", data)
            report = self.woo_connector.generate_woo_report(dataset)
            return report
        except Exception as e:
            return f"❌ Fout: {str(e)}"

    async def find_woo_related_datasets(self, topic: str) -> str:
        """Vind datasets gerelateerd aan een Woo onderwerp"""
        if not self.woo_connector:
            return "⚠️ Woo connector niet beschikbaar"

        try:
            data = await self.fetch_api("/datasets")
            datasets = data.get("data", [])
            related = self.woo_connector.find_related_datasets(topic, datasets)

            if not related:
                return f"Geen datasets gevonden gerelateerd aan '{topic}'"

            result = f"🔗 Datasets gerelateerd aan '{topic}':\n\nGevonden: {len(related)} dataset(s)\n\n"

            for item in related[:10]:
                ds, analysis, relevance = item['dataset'], item['analysis'], item['relevance']
                attrs = ds.get('attributes', {})
                title = self.get_attr(attrs, 'title') or ds.get('id', 'Geen titel')

                result += f"📊 {title}\n   ID: {ds.get('id')}\n   Relevantie: {relevance}/10\n"
                result += f"   Topics: {', '.join(analysis['topics'][:3])}\n"

                if analysis['woo_categories']:
                    woo_cats = [c['name'] for c in analysis['woo_categories'][:2]]
                    result += f"   Woo categorieën: {', '.join(woo_cats)}\n"
                result += "\n"

            if len(related) > 10:
                result += f"... en nog {len(related) - 10} datasets meer\n"

            return result
        except Exception as e:
            return f"❌ Fout: {str(e)}"

    # Data.overheid.nl tool implementations
    async def dataoverheid_search(self, query: Optional[str], organization: Optional[str],
                                  tags: Optional[List[str]], limit: int) -> str:
        """Zoek datasets op data.overheid.nl"""
        if not self.dataoverheid:
            return "⚠️ Data.overheid.nl connector niet beschikbaar"

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.dataoverheid.search_datasets(
                    query=query,
                    organization=organization,
                    tags=tags,
                    rows=min(limit, 100)
                )
            )

            return self.dataoverheid.format_search_results(result, compact=False)
        except Exception as e:
            return f"❌ Fout bij zoeken: {str(e)}"

    async def dataoverheid_get_dataset(self, dataset_id: str) -> str:
        """Haal dataset details op van data.overheid.nl"""
        if not self.dataoverheid:
            return "⚠️ Data.overheid.nl connector niet beschikbaar"

        try:
            loop = asyncio.get_event_loop()
            dataset = await loop.run_in_executor(
                None,
                lambda: self.dataoverheid.get_dataset(dataset_id)
            )

            return self.dataoverheid.format_dataset_summary(dataset)
        except Exception as e:
            return f"❌ Fout bij ophalen dataset: {str(e)}"

    async def dataoverheid_list_organizations(self, limit: int) -> str:
        """Lijst van overheidsorganisaties"""
        if not self.dataoverheid:
            return "⚠️ Data.overheid.nl connector niet beschikbaar"

        try:
            loop = asyncio.get_event_loop()
            orgs = await loop.run_in_executor(
                None,
                lambda: self.dataoverheid.list_organizations(all_fields=True)
            )

            result = f"🏛️ Nederlandse overheidsorganisaties op data.overheid.nl\n\n"
            result += f"Totaal: {len(orgs)} organisaties\n\n"

            for i, org in enumerate(orgs[:limit], 1):
                title = org.get('title', org.get('display_name', org.get('name', 'Onbekend')))
                package_count = org.get('package_count', 0)
                result += f"{i}. {title}\n"
                result += f"   ID: {org.get('name', 'onbekend')}\n"
                result += f"   Datasets: {package_count}\n"

                description = org.get('description', '')
                if description and len(description) > 0:
                    preview = description[:100] + '...' if len(description) > 100 else description
                    result += f"   {preview}\n"
                result += "\n"

            if len(orgs) > limit:
                result += f"... en nog {len(orgs) - limit} organisaties meer\n"

            return result
        except Exception as e:
            return f"❌ Fout bij ophalen organisaties: {str(e)}"

    async def dataoverheid_get_organization(self, org_id: str, include_datasets: bool) -> str:
        """Details van een organisatie"""
        if not self.dataoverheid:
            return "⚠️ Data.overheid.nl connector niet beschikbaar"

        try:
            loop = asyncio.get_event_loop()
            org = await loop.run_in_executor(
                None,
                lambda: self.dataoverheid.get_organization(org_id, include_datasets)
            )

            result = f"🏛️ {org.get('title', org.get('display_name', org_id))}\n"
            result += "=" * 70 + "\n\n"
            result += f"ID: {org.get('name', org_id)}\n"
            result += f"Datasets: {org.get('package_count', 0)}\n"

            description = org.get('description', '')
            if description:
                result += f"\nBeschrijving:\n{description}\n"

            # Image URL
            image_url = org.get('image_url', '')
            if image_url:
                result += f"\nLogo: {image_url}\n"

            # Datasets
            if include_datasets:
                packages = org.get('packages', [])
                if packages:
                    result += f"\n📊 Datasets ({len(packages)}):\n\n"
                    for i, pkg in enumerate(packages[:20], 1):
                        title = pkg.get('title', pkg.get('name', 'Geen titel'))
                        result += f"{i}. {title}\n"
                        result += f"   ID: {pkg.get('name', '')}\n"

                        notes = pkg.get('notes', '')
                        if notes:
                            preview = notes[:100] + '...' if len(notes) > 100 else notes
                            result += f"   {preview}\n"
                        result += "\n"

                    if len(packages) > 20:
                        result += f"... en nog {len(packages) - 20} datasets meer\n"

            result += "=" * 70
            return result
        except Exception as e:
            return f"❌ Fout bij ophalen organisatie: {str(e)}"

async def main():
    """Main entry point"""
    server = MCPServer()

    # Log to stderr
    sys.stderr.write("Utrecht Open Data MCP Server gestart\n")
    sys.stderr.flush()

    # Read from stdin, write to stdout
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line)
            response = await server.handle_request(request)

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError as e:
            sys.stderr.write(f"JSON parse error: {e}\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    asyncio.run(main())

    async def analyze_woo_connection(self, dataset_id: str) -> str:
        """Analyseer Woo koppeling voor een dataset"""
        if not self.woo_connector:
            return "⚠️ Woo connector niet beschikbaar. Installeer woo_connector.py"

        try:
            # Haal dataset op
            data = await self.fetch_api(f"/datasets/{dataset_id}")
            dataset = data.get("data", data)

            # Genereer Woo rapport
            report = self.woo_connector.generate_woo_report(dataset)
            return report

        except Exception as e:
            return f"❌ Fout bij analyseren Woo koppeling: {str(e)}"

    async def find_woo_related_datasets(self, topic: str) -> str:
        """Vind datasets gerelateerd aan een Woo onderwerp"""
        if not self.woo_connector:
            return "⚠️ Woo connector niet beschikbaar. Installeer woo_connector.py"

        try:
            # Haal alle datasets op
            data = await self.fetch_api("/datasets")
            datasets = data.get("data", [])

            # Vind gerelateerde datasets
            related = self.woo_connector.find_related_datasets(topic, datasets)

            if not related:
                return f"Geen datasets gevonden gerelateerd aan '{topic}'"

            result = f"🔗 Datasets gerelateerd aan '{topic}':\n\n"
            result += f"Gevonden: {len(related)} dataset(s)\n\n"

            for item in related[:10]:  # Top 10
                ds = item['dataset']
                analysis = item['analysis']
                relevance = item['relevance']

                attrs = ds.get('attributes', {})
                title = self.get_attr(attrs, 'title') or ds.get('id', 'Geen titel')

                result += f"📊 {title}\n"
                result += f"   ID: {ds.get('id')}\n"
                result += f"   Relevantie: {relevance}/10\n"
                result += f"   Topics: {', '.join(analysis['topics'][:3])}\n"

                if analysis['woo_categories']:
                    woo_cats = [c['name'] for c in analysis['woo_categories'][:2]]
                    result += f"   Woo categorieën: {', '.join(woo_cats)}\n"

                result += "\n"

            if len(related) > 10:
                result += f"... en nog {len(related) - 10} datasets meer\n"

            return result

        except Exception as e:
            return f"❌ Fout bij zoeken gerelateerde datasets: {str(e)}"
