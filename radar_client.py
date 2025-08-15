"""
RADAR Framework API Client

A Python client for interacting with the RADAR (Regulatory Assessment for 
Digital Service Act Risks) Framework API with multi-version support.

Usage:
    client = RADARClient(
        base_url="http://api.radar.checkfirst.network",
        contact_url="https://yourcompany.com/contact",
        version="1.7"  # Optional: specify version
    )
    
    # List available versions
    versions = client.get_versions()
    
    # Search in a specific version
    results = client.search_infringements("dark patterns", version="1.6")
    
    # Get all categories from current version
    categories = client.get_categories()
"""

import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlencode
import json
from datetime import datetime


class RADARClient:
    """Client for interacting with the RADAR Framework API"""
    
    def __init__(self, base_url: str, contact_url: str, version: Optional[str] = None, timeout: int = 30):
        """
        Initialize the RADAR API client.
        
        Args:
            base_url: Base URL of the RADAR API (e.g., "http://api.radar.checkfirst.network")
            contact_url: URL where you can be contacted (required for User-Agent)
            version: Default framework version to use (optional)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.contact_url = contact_url
        self.default_version = version
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set required User-Agent header
        self.session.headers.update({
            'User-Agent': f'RADAR-Python-Client/2.0 ({contact_url})',
            'Accept': 'application/json'
        })
        
        # Cache current version info
        self._version_info = None
        self._last_version_check = None
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                      data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to the API"""
        url = urljoin(self.base_url, endpoint)
        
        # Add version parameter if set and not already in params
        if self.default_version and params is not None and 'version' not in params:
            params['version'] = self.default_version
        elif self.default_version and params is None:
            params = {'version': self.default_version}
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RADARAPIError(f"API request failed: {str(e)}")
    
    def get_versions(self) -> Dict:
        """
        Get all available framework versions
        
        Returns:
            Dict containing current_version, latest_version, and list of all versions
        """
        return self._make_request('GET', '/api/v1/versions')
    
    def set_default_version(self, version: str):
        """
        Set the default version for all subsequent requests
        
        Args:
            version: Version string (e.g., "1.7")
        """
        self.default_version = version
    
    def get_current_version(self) -> str:
        """Get the current framework version being used"""
        if not self._version_info or not self._last_version_check:
            self._version_info = self.get_versions()
            self._last_version_check = datetime.now()
        
        return self.default_version or self._version_info.get('current_version')
    
    def get_api_info(self) -> Dict:
        """Get API information and available endpoints"""
        return self._make_request('GET', '/api/v1')
    
    def get_framework(self, version: Optional[str] = None) -> Dict:
        """
        Get framework metadata and overview
        
        Args:
            version: Specific version to retrieve (overrides default)
        """
        params = {}
        if version:
            params['version'] = version
        return self._make_request('GET', '/api/v1/framework', params=params)
    
    def get_categories(self, version: Optional[str] = None) -> Dict:
        """
        Get all categories
        
        Args:
            version: Specific version to use (overrides default)
        """
        params = {}
        if version:
            params['version'] = version
        return self._make_request('GET', '/api/v1/categories', params=params)
    
    def get_category(self, category_id: str, version: Optional[str] = None) -> Dict:
        """
        Get specific category by ID
        
        Args:
            category_id: Category ID (e.g., 'dp' for Dark Patterns)
            version: Specific version to use (overrides default)
        """
        params = {}
        if version:
            params['version'] = version
        return self._make_request('GET', f'/api/v1/categories/{category_id}', params=params)
    
    def get_category_infringements(self, category_id: str, version: Optional[str] = None) -> Dict:
        """
        Get all infringements for a specific category
        
        Args:
            category_id: Category ID
            version: Specific version to use (overrides default)
        """
        params = {}
        if version:
            params['version'] = version
        return self._make_request('GET', f'/api/v1/categories/{category_id}/infringements', params=params)
    
    def get_infringement(self, infringement_id: str, version: Optional[str] = None) -> Dict:
        """
        Get specific infringement by ID
        
        Args:
            infringement_id: Infringement ID (e.g., 'dp_01')
            version: Specific version to use (overrides default)
        """
        params = {}
        if version:
            params['version'] = version
        return self._make_request('GET', f'/api/v1/infringements/{infringement_id}', params=params)
    
    def get_infringements(self, category: Optional[str] = None, 
                         dsa_article: Optional[str] = None,
                         page: int = 1, 
                         per_page: int = 20,
                         version: Optional[str] = None) -> Dict:
        """
        Get all infringements with optional filtering
        
        Args:
            category: Filter by category ID
            dsa_article: Filter by DSA article number
            page: Page number (default: 1)
            per_page: Results per page (default: 20, max: 100)
            version: Specific version to use (overrides default)
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        if category:
            params['category'] = category
        if dsa_article:
            params['dsa_article'] = dsa_article
        if version:
            params['version'] = version
            
        return self._make_request('GET', '/api/v1/infringements', params=params)
    
    def search_infringements(self, query: str, limit: int = 10, 
                           threshold: float = 15.0,
                           version: Optional[str] = None) -> Dict:
        """
        Search for infringements matching a query
        
        Args:
            query: Search query text
            limit: Maximum number of results (default: 10, max: 100)
            threshold: Minimum relevance score (default: 15.0)
            version: Specific version to use (overrides default)
        """
        params = {
            'q': query,
            'limit': limit,
            'threshold': threshold
        }
        if version:
            params['version'] = version
            
        return self._make_request('GET', '/api/v1/infringements/search', params=params)
    
    def get_dsa_articles(self, version: Optional[str] = None) -> Dict:
        """
        Get all DSA articles referenced in the framework
        
        Args:
            version: Specific version to use (overrides default)
        """
        params = {}
        if version:
            params['version'] = version
        return self._make_request('GET', '/api/v1/dsa-articles', params=params)
    
    def get_statistics(self, version: Optional[str] = None) -> Dict:
        """
        Get comprehensive statistics about the framework
        
        Args:
            version: Specific version to use (overrides default)
        """
        params = {}
        if version:
            params['version'] = version
        return self._make_request('GET', '/api/v1/stats', params=params)
    
    def health_check(self) -> Dict:
        """Check API health status"""
        return self._make_request('GET', '/api/v1/health')
    
    def search_and_analyze(self, query: str, verbose: bool = False, version: Optional[str] = None) -> Dict:
        """
        Search for infringements and provide analysis
        
        Args:
            query: Search query
            verbose: Include detailed information
            version: Specific version to use (overrides default)
        """
        results = self.search_infringements(query, version=version)
        
        analysis = {
            'query': query,
            'version': results.get('version'),
            'quality': results.get('search_quality', 'unknown'),
            'total_found': results.get('total_found', 0),
            'suggestion': results.get('suggestion'),
            'top_matches': []
        }
        
        # Analyze top matches
        for result in results.get('results', [])[:3]:
            match = {
                'id': result['infringement_id'],
                'name': result['infringement_name'],
                'category': result['category_name'],
                'score': result['relevance_score']
            }
            
            if verbose:
                match['description'] = result.get('description')
                match['matched_terms'] = result.get('matched_terms', [])
                match['observables'] = result.get('matched_observables', [])
            
            analysis['top_matches'].append(match)
        
        return analysis
    
    def get_infringement_full(self, infringement_id: str, version: Optional[str] = None) -> Dict:
        """
        Get full infringement details including category context
        
        Args:
            infringement_id: Infringement ID
            version: Specific version to use (overrides default)
        """
        infringement = self.get_infringement(infringement_id, version=version)
        
        # Add category details
        if 'category' in infringement:
            category_id = infringement['category']['id']
            category_full = self.get_category(category_id, version=version)
            infringement['category_full'] = {
                'id': category_full['id'],
                'name': category_full['name'],
                'description': category_full.get('description')
            }
        
        return infringement
    
    def compare_versions(self, version1: str, version2: str) -> Dict:
        """
        Compare statistics between two framework versions
        
        Args:
            version1: First version to compare
            version2: Second version to compare
        """
        stats1 = self.get_statistics(version=version1)
        stats2 = self.get_statistics(version=version2)
        
        comparison = {
            'version1': version1,
            'version2': version2,
            'changes': {
                'categories': stats2['totals']['categories'] - stats1['totals']['categories'],
                'infringements': stats2['totals']['infringements'] - stats1['totals']['infringements'],
                'observables': stats2['totals']['observables'] - stats1['totals']['observables'],
                'dsa_articles': stats2['totals']['dsa_articles'] - stats1['totals']['dsa_articles']
            },
            'stats': {
                'version1': stats1['totals'],
                'version2': stats2['totals']
            }
        }
        
        return comparison
    
    def search_across_versions(self, query: str, versions: Optional[List[str]] = None,
                              limit: int = 5, threshold: float = 15.0) -> Dict:
        """
        Search for infringements across multiple framework versions
        
        Args:
            query: Search query
            versions: List of versions to search (None = all available)
            limit: Results per version
            threshold: Minimum relevance score
        """
        if versions is None:
            version_info = self.get_versions()
            versions = [v['version'] for v in version_info['versions'][:3]]  # Last 3 versions
        
        results = {}
        for version in versions:
            try:
                search_results = self.search_infringements(query, limit=limit, 
                                                         threshold=threshold, 
                                                         version=version)
                results[version] = {
                    'total_found': search_results.get('total_found', 0),
                    'suggestion': search_results.get('suggestion'),
                    'top_results': search_results.get('results', [])[:3]
                }
            except RADARAPIError:
                results[version] = {'error': 'Failed to search this version'}
        
        return {
            'query': query,
            'versions_searched': versions,
            'results_by_version': results
        }
    
    def get_infringement_evolution(self, infringement_id: str, 
                                  versions: Optional[List[str]] = None) -> Dict:
        """
        Track how an infringement has evolved across versions
        
        Args:
            infringement_id: Infringement ID to track
            versions: List of versions to check (None = all available)
        """
        if versions is None:
            version_info = self.get_versions()
            versions = [v['version'] for v in version_info['versions']]
        
        evolution = {
            'infringement_id': infringement_id,
            'versions': {}
        }
        
        for version in versions:
            try:
                inf = self.get_infringement(infringement_id, version=version)
                evolution['versions'][version] = {
                    'exists': True,
                    'name': inf.get('name'),
                    'description': inf.get('description'),
                    'observable_count': len(inf.get('observables', [])),
                    'dsa_articles': inf.get('dsaArticles', [])
                }
            except RADARAPIError:
                evolution['versions'][version] = {'exists': False}
        
        return evolution


class RADARAPIError(Exception):
    """Exception raised for RADAR API errors"""
    pass


# Convenience functions for quick usage
def create_client(base_url: str, contact_url: str, version: Optional[str] = None) -> RADARClient:
    """
    Create a RADAR API client
    
    Args:
        base_url: API base URL
        contact_url: Your contact URL for the User-Agent header
        version: Default framework version (optional)
    """
    return RADARClient(base_url, contact_url, version)


def quick_search(base_url: str, contact_url: str, query: str, version: Optional[str] = None) -> List[Dict]:
    """
    Quick search without creating a client instance
    
    Args:
        base_url: API base URL
        contact_url: Your contact URL
        query: Search query
        version: Framework version (optional)
        
    Returns:
        List of search results
    """
    client = RADARClient(base_url, contact_url, version)
    results = client.search_infringements(query)
    return results.get('results', [])


if __name__ == "__main__":
    # Example usage
    print("RADAR API Client Example")
    print("-" * 50)
    
    # You need to provide your own contact URL
    CONTACT_URL = "https://example.com/contact"
    API_URL = "http://localhost:5000"
    
    try:
        # Create client
        client = RADARClient(API_URL, CONTACT_URL)
        
        # Check health
        health = client.health_check()
        print(f"API Status: {health['status']}")
        print(f"Framework: {health['framework']}")
        print(f"Current Version: {health['current_version']}")
        print(f"Available Versions: {health['available_versions']}")
        print()
        
        # Get versions
        versions = client.get_versions()
        print(f"Latest Version: {versions['latest_version']}")
        print("Recent Versions:")
        for v in versions['versions'][:3]:
            print(f"  - {v['version']} ({v.get('date', 'unknown')})")
        print()
        
        # Search example
        query = "dark patterns"
        print(f"Searching for: '{query}'")
        analysis = client.search_and_analyze(query, verbose=True)
        
        print(f"Version Used: {analysis['version']}")
        print(f"Search Quality: {analysis['quality']}")
        print(f"Total Found: {analysis['total_found']}")
        
        if analysis['suggestion']:
            print(f"\nSuggested Match:")
            print(f"  {analysis['suggestion']['infringement_name']}")
            print(f"  Confidence: {analysis['suggestion']['confidence']}")
            print(f"  Score: {analysis['suggestion']['score']}")
        
        print(f"\nTop Matches:")
        for match in analysis['top_matches']:
            print(f"  - [{match['id']}] {match['name']}")
            print(f"    Category: {match['category']}")
            print(f"    Score: {match['score']}")
            if 'description' in match and match['description']:
                print(f"    Description: {match['description'][:100]}...")
            print()
        
        # Compare versions if multiple available
        if len(versions['versions']) >= 2:
            v1 = versions['versions'][1]['version']
            v2 = versions['versions'][0]['version']
            print(f"\nComparing versions {v1} and {v2}:")
            comparison = client.compare_versions(v1, v2)
            print(f"  Categories: {comparison['changes']['categories']:+d}")
            print(f"  Infringements: {comparison['changes']['infringements']:+d}")
            print(f"  Observables: {comparison['changes']['observables']:+d}")
            
    except RADARAPIError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")