import logging

import httpx
from mcpfire.http_models.models import HTTPRequest, HTTPResponse


async def async_request(req: HTTPRequest) -> HTTPResponse:
    """
    Executes the request asynchronously and returns a Pydantic Response model.
    """
    logging.info("Sending HTTP request %s %$...", req.method, req.url)

    # We use an AsyncClient context manager for efficient connection pooling
    async with httpx.AsyncClient(
        timeout=req.timeout,
        follow_redirects=req.follow_redirects,
        cookies=req.cookies
    ) as client:

        try:
            response = await client.request(
                method=req.method,
                url=str(req.url),
                headers=req.headers,
                params=req.params,
                auth=req.auth,
                json=req.json_payload,
                content=req.data_payload if isinstance(req.data_payload, (str, bytes)) else None,
                data=req.data_payload if isinstance(req.data_payload, dict) else None,
            )

            # Attempt to parse JSON body safely
            try:
                json_data = response.json()
            except Exception:
                json_data = None
            print(response.headers)
            # Map httpx Response -> Pydantic HTTPResponse
            return HTTPResponse(
                status_code=response.status_code,
                url=str(response.url),
                method=response.request.method,
                headers=dict(response.headers),
                cookies=dict(response.cookies),
                elapsed_seconds=response.elapsed.total_seconds(),
                text_body=response.text,
                json_body=json_data
            )

        except httpx.RequestError as exc:
            logging.info(f"An error occurred while requesting {exc.request.url!r}.")
            raise
