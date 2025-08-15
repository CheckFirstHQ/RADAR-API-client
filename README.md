# RADAR API Python Client

A Python client library for interacting with the RADAR Framework API.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from radar_client import RADARClient

# Initialize client (contact URL is required)
client = RADARClient(
    base_url="https://api.radar.checkfirst.network",
    contact_url="https://yourcompany.com/contact"
)

# Search for infringements
results = client.search_infringements("dark patterns")
for result in results['results']:
    print(f"{result['infringement_id']}: {result['infringement_name']}")

# Get all categories
categories = client.get_categories()
for cat in categories['categories']:
    print(f"{cat['id']}: {cat['name']}")
```

## Features

### Basic Operations

```python
# Get framework info
info = client.get_framework_info()

# Get specific category
category = client.get_category("dp")

# Get specific infringement
infringement = client.get_infringement("dp_01")

# List DSA articles
articles = client.get_dsa_articles()

# Get statistics
stats = client.get_stats()
```

### Search

```python
# Basic search
results = client.search_infringements("age verification")

# Search with parameters
results = client.search_infringements(
    query="minors",
    limit=5,
    threshold=20.0
)
```

### Version Management

```python
# Use specific version
client = RADARClient(
    base_url="https://api.radar.checkfirst.network",
    contact_url="https://yourcompany.com/contact",
    version="1.7"
)

# Or specify per request
categories = client.get_categories(version="1.6")

# List available versions
versions = client.get_versions()

# Compare versions
comparison = client.compare_versions("1.6", "1.7")

# Search across versions
results = client.search_across_versions(
    query="political ads",
    versions=["1.6", "1.7"]
)
```

### Pagination

```python
# Get paginated infringements
infringements = client.get_infringements(
    page=2,
    per_page=50,
    category="dp"
)
```

## User-Agent Requirement

The RADAR API requires a descriptive User-Agent header with contact information. The client handles this automatically using the `contact_url` provided during initialization.

Format: `RADAR-Python-Client/{version} ({contact_url})`

## Error Handling

```python
try:
    result = client.get_category("invalid_id")
except Exception as e:
    print(f"Error: {e}")
```

## Rate Limiting

The API implements rate limiting (100 requests/minute per IP). If you exceed the limit, you'll receive a 429 error and your IP will be blocked for 24 hours.

## Complete Example

```python
from radar_client import RADARClient

# Initialize
client = RADARClient(
    base_url="https://api.radar.checkfirst.network",
    contact_url="https://example.com/contact"
)

# Search for dark patterns
results = client.search_infringements("dark patterns")

# Print top result
if results['results']:
    top = results['results'][0]
    print(f"Most relevant: {top['infringement_name']}")
    print(f"Score: {top['relevance_score']}")
    print(f"Category: {top['category_name']}")
    
    # Get full details
    details = client.get_infringement(top['infringement_id'])
    print(f"Observables: {len(details['observables'])}")
```

## License

This client library is provided as-is. The RADAR framework data is licensed under CC-BY-4.0 by CheckFirst.