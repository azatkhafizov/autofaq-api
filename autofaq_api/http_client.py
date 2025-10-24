import aiohttp
import requests

from contextlib import asynccontextmanager, contextmanager
from typing import Dict, Any, AsyncGenerator, Generator, Optional


class AutoFaqHTTPClient:
    def __init__(self, base_url: str = "", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self._sync_session: Optional[requests.Session] = None
        self._async_session: Optional[aiohttp.ClientSession] = None
        self._default_headers: Dict[str, str] = {}
    
    @property
    def sync_session(self) -> requests.Session:
        if self._sync_session is None:
            self._sync_session = requests.Session()
            if self._default_headers:
                self._sync_session.headers.update(self._default_headers)
        return self._sync_session
    
    @property
    def async_session(self) -> aiohttp.ClientSession:
        if self._async_session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._async_session = aiohttp.ClientSession(
                headers=self._default_headers.copy(), 
                timeout=timeout
            )
        return self._async_session
    
    def set_default_headers(self, headers: Dict[str, str]) -> None:
        self._default_headers.update(headers)
        if self._sync_session: self._sync_session.headers.update(headers)
            
    async def async_set_default_headers(self, headers: Dict[str, str]) -> None:
        self._default_headers.update(headers)
        
        if self._async_session:
            await self._async_session.close()
            self._async_session = None
    
    def update_default_headers(self, headers: Dict[str, str]) -> None:
        self.set_default_headers(headers)
    
    def clear_default_headers(self) -> None:
        self._default_headers.clear()
        if self._sync_session:
            self._sync_session.headers.clear()
            
    async def async_clear_default_headers(self) -> None:
        self._default_headers.clear()
        if self._async_session:
            if self._async_session:
                await self._async_session.close()
                self._async_session = None
    
    @contextmanager
    def temporary_sync_session(self, headers: Dict[str, str] = None) -> Generator[requests.Session, None, None]:
        session = requests.Session()
        if headers:
            session.headers.update(headers)
        elif self._default_headers:
            session.headers.update(self._default_headers)
            
        try:
            yield session
        finally:
            session.close()
    
    @asynccontextmanager
    async def temporary_async_session(self, headers: Dict[str, str] = None) -> AsyncGenerator[aiohttp.ClientSession, None]:
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        session_headers = self._default_headers.copy()
        if headers:
            session_headers.update(headers)
            
        async with aiohttp.ClientSession(
            headers=session_headers, 
            timeout=timeout
        ) as session:
            yield session
    
    def _build_url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint
    
    def _handle_response(self, response: requests.Response, return_json: bool = True) -> Any:
        self._check_status(response)
        if return_json: 
            try: return response.json()
            except: return response.text
        return response.text
    
    async def _handle_async_response(self, response: aiohttp.ClientResponse, return_json: bool = True) -> Any:
        await self._check_async_status(response)
        if return_json: 
            try: return await response.json()
            except: return await response.text()
        return await response.text()
    
    def _check_status(self, response: requests.Response) -> None:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                error_text = response.text
                error_json = response.json()
                error_details = f"Response JSON: {error_json}"
            except:
                error_details = f"Response text: {error_text}"
            
            raise requests.exceptions.HTTPError(
                f"{str(e)}\n{error_details}", 
                response=response
            ) from e
    
    async def _check_async_status(self, response: aiohttp.ClientResponse) -> None:
        if response.status >= 400:
            try:
                error_text = await response.text()
                try:
                    error_json = await response.json()
                    error_details = f"Response JSON: {error_json}"
                except:
                    error_details = f"Response text: {error_text}"
            except Exception as e:
                error_details = f"Could not read response: {str(e)}"
            
            raise aiohttp.ClientResponseError(
                request_info=response.request_info,
                history=response.history,
                status=response.status,
                message=f"HTTP {response.status}: {response.reason}\n{error_details}",
                headers=response.headers
            )
    
    def close_sync_session(self) -> None:
        if self._sync_session:
            self._sync_session.close()
            self._sync_session = None
    
    async def close_async_session(self) -> None:
        if self._async_session:
            await self._async_session.close()
            self._async_session = None
    
    async def close(self) -> None:
        self.close_sync_session()
        await self.close_async_session()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_sync_session()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    def sync_get(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        response = self.sync_session.get(url, **kwargs)
        return self._handle_response(response, return_json)
    
    def sync_post(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        response = self.sync_session.post(url, **kwargs)
        return self._handle_response(response, return_json)
    
    def sync_put(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        response = self.sync_session.put(url, **kwargs)
        return self._handle_response(response, return_json)
    
    def sync_patch(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        response = self.sync_session.patch(url, **kwargs)
        return self._handle_response(response, return_json)
    
    def sync_delete(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        response = self.sync_session.delete(url, **kwargs)
        return self._handle_response(response, return_json)
    
    def sync_head(self, endpoint: str, **kwargs) -> Dict[str, str]:
        url = self._build_url(endpoint)
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        response = self.sync_session.head(url, **kwargs)
        self._check_status(response)
        return dict(response.headers)
    
    def sync_options(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = self._build_url(endpoint)
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        response = self.sync_session.options(url, **kwargs)
        self._check_status(response)
        return {
            'headers': dict(response.headers),
            'allowed_methods': response.headers.get('allow', '').split(', ')
        }
    
    async def async_get(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        async with self.async_session.get(url, **kwargs) as response:
            return await self._handle_async_response(response, return_json)
    
    async def async_post(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        async with self.async_session.post(url, **kwargs) as response:
            return await self._handle_async_response(response, return_json)
    
    async def async_put(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        async with self.async_session.put(url, **kwargs) as response:
            return await self._handle_async_response(response, return_json)
    
    async def async_patch(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        async with self.async_session.patch(url, **kwargs) as response:
            return await self._handle_async_response(response, return_json)
    
    async def async_delete(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        async with self.async_session.delete(url, **kwargs) as response:
            return await self._handle_async_response(response, return_json)
    
    async def async_head(self, endpoint: str, **kwargs) -> Dict[str, str]:
        url = self._build_url(endpoint)
        async with self.async_session.head(url, **kwargs) as response:
            await self._check_async_status(response)
            return dict(response.headers)
    
    async def async_options(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = self._build_url(endpoint)
        async with self.async_session.options(url, **kwargs) as response:
            await self._check_async_status(response)
            return {
                'headers': dict(response.headers),
                'allowed_methods': response.headers.get('allow', '').split(', ')
            }
    
    def sync_get_temp(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        with self.temporary_sync_session() as session:
            url = self._build_url(endpoint)
            response = session.get(url, **kwargs)
            return self._handle_response(response, return_json)
    
    def sync_post_temp(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        with self.temporary_sync_session() as session:
            url = self._build_url(endpoint)
            response = session.post(url, **kwargs)
            return self._handle_response(response, return_json)
    
    async def async_get_temp(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        async with self.temporary_async_session() as session:
            url = self._build_url(endpoint)
            async with session.get(url, **kwargs) as response:
                return await self._handle_async_response(response, return_json)
    
    async def async_post_temp(self, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        async with self.temporary_async_session() as session:
            url = self._build_url(endpoint)
            async with session.post(url, **kwargs) as response:
                return await self._handle_async_response(response, return_json)
    
    def sync_request(self, method: str, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        response = self.sync_session.request(method.upper(), url, **kwargs)
        return self._handle_response(response, return_json)
    
    async def async_request(self, method: str, endpoint: str, return_json: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        async with self.async_session.request(method.upper(), url, **kwargs) as response:
            return await self._handle_async_response(response, return_json)