import httpx
import asyncio
import hashlib
import re
import socket
from urllib.parse import urlparse
import ipaddress
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import Client

class ResourceMonitor:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def is_safe_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                return False
            
            hostname = parsed.hostname
            if not hostname:
                return False

            if hostname in ['localhost', '127.0.0.1']:
                return False

            try:
                ip = socket.gethostbyname(hostname)
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved or ip_obj.is_multicast:
                    return False
            except socket.gaierror:
                return False # could not resolve

            return True
        except Exception:
            return False

    async def check_resource(self, resource_id: str, url: str, previous_hash: str = None, user_id: str = None, task_id: str = None) -> dict:
        if not self.is_safe_url(url):
            return self._record_result(resource_id, task_id, user_id, 'invalid_url', 'URL is not safe', None, previous_hash)

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, max_redirects=5) as client:
                response = await client.get(url)
                
                status_code = response.status_code
                if status_code == 200:
                    check_status = 'available'
                elif 300 <= status_code < 400:
                    check_status = 'redirected'
                elif status_code == 404:
                    check_status = 'not_found'
                elif status_code in (401, 403):
                    check_status = 'forbidden'
                elif 500 <= status_code < 600:
                    check_status = 'server_error'
                else:
                    check_status = 'unknown'

                content = response.content[:500000] # Read up to 500KB
                content_hash = hashlib.sha256(content).hexdigest() if content else None

                title = None
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    if soup.title and soup.title.string:
                        title = soup.title.string.strip()

                return self._record_result(resource_id, task_id, user_id, check_status, None, content_hash, previous_hash, title)

        except httpx.TimeoutException:
            return self._record_result(resource_id, task_id, user_id, 'timeout', 'Request timed out', None, previous_hash)
        except httpx.RequestError as e:
            return self._record_result(resource_id, task_id, user_id, 'network_error', str(e), None, previous_hash)
        except Exception as e:
            return self._record_result(resource_id, task_id, user_id, 'unknown', str(e), None, previous_hash)

    def _record_result(self, resource_id: str, task_id: str, user_id: str, check_status: str, error_message: str, content_hash: str, previous_hash: str, title: str = None) -> dict:
        change_type = None
        change_severity = None

        if previous_hash and content_hash and previous_hash != content_hash:
            change_type = 'content_changed'
            change_severity = 'minor' # Could be more sophisticated
        elif check_status in ['not_found', 'server_error', 'forbidden']:
            change_type = 'status_changed'
            change_severity = 'critical'

        # Update task_resources
        update_data = {
            'check_status': check_status,
            'last_checked_at': datetime.utcnow().isoformat()
        }
        if content_hash:
            update_data['content_hash'] = content_hash
        if title:
            update_data['title'] = title
            
        self.supabase.table('task_resources').update(update_data).eq('id', resource_id).execute()

        # Insert resource_checks
        check_data = {
            'resource_id': resource_id,
            'task_id': task_id,
            'user_id': user_id,
            'check_status': check_status,
            'change_type': change_type,
            'change_severity': change_severity,
            'content_hash': content_hash,
            'error_message': error_message
        }
        self.supabase.table('resource_checks').insert(check_data).execute()

        return check_data
