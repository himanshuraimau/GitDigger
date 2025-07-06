import requests
import time
from typing import Dict, List, Optional
import dotenv
from src.config.config import GITHUB_API_URL, GITHUB_ACCESS_TOKEN

dotenv.load_dotenv()

class GitHubService:
    def __init__(self, access_token: str = None): # type: ignore
        self.access_token = access_token or GITHUB_ACCESS_TOKEN
        if not self.access_token:
            raise ValueError("GitHub access token required")
        
        self.base_url = GITHUB_API_URL
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def _make_request(self, url: str, params: Dict = None) -> Dict: # type: ignore
        """Make API request with basic error handling"""
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
        
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0)) - time.time()
                if reset_time > 0:
                    time.sleep(reset_time + 1)
                    return self._make_request(url, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException:
            return None # type: ignore
    
    def get_organization(self, org_name: str) -> Optional[Dict]:
        """Get organization details"""
        url = f"{self.base_url}/orgs/{org_name}"
        data = self._make_request(url)
        
        if not data:
            return None
            
        return {
            'login': data.get('login'),
            'name': data.get('name'),
            'public_repos': data.get('public_repos', 0),
            'public_members': data.get('public_members', 0),
            'created_at': data.get('created_at'),
            'location': data.get('location'),
            'description': data.get('description')
        }
    
    def get_organization_members(self, org_name: str) -> List[Dict]:
        url = f"{self.base_url}/orgs/{org_name}/public_members"
        members = []
        page = 1
        
        while True:
            params = {'page': page, 'per_page': 100}
            data = self._make_request(url, params)
            
            if not data:
                break
                
            if not data:  
                break
                
            for member in data:
                members.append({
                    'login': member.get('login'),
                    'avatar_url': member.get('avatar_url'),
                    'html_url': member.get('html_url'),
                    'type': member.get('type')
                })
            
            if len(data) < 100:
                break
                
            page += 1
        
        return members
    
    def get_organization_data(self, org_name: str) -> Dict:
        org_info = self.get_organization(org_name)
        if not org_info:
            return {
                'success': False,
                'company_name': None,
                'github_members': [],
                'error': 'Organization not found'
            }
        
        members = self.get_organization_members(org_name)
        
        return {
            'success': True,
            'company_name': org_info['name'] or org_info['login'],
            'github_members': members,
            'organization_info': org_info
        }