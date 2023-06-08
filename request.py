import httpx

http = httpx.Client(timeout=20, transport=httpx.HTTPTransport(retries=5))