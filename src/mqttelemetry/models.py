"""This module contains the models for telemetry logging."""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class MessagePayload(BaseModel):
    """Represents a message payload for telemetry logging."""

    request_method: str
    request_body: str | None = None
    request_url_path: str
    request_query_params: dict[str, Any] = {}
    request_path_params: dict[str, Any] = {}
    headers: dict[str, Any] = {}
    response_body: Any | None = None
    response_status_code: int

    @classmethod
    async def from_request_response(
        cls, request: Request, response: Response
    ) -> MessagePayload:
        # Extract request body as string
        request_body_str = None
        try:
            raw_body = await request.body()
            if raw_body:
                request_body_str = raw_body.decode("utf-8")
                request_body_str = " ".join(request_body_str.split())
        except Exception as exc:
            logger.warning("Could not extract request body: %s", exc)

        # Extract request details
        endpoint_path = request.url.path
        query_params = dict(request.query_params)
        path_params = dict(request.path_params)
        method = request.method
        headers = dict(request.headers)

        # Extract and process response body
        response_body = None
        try:
            if hasattr(response, "body"):
                response_body = response.body
                if response_body is not None:
                    if isinstance(response_body, bytes):
                        response_body = response_body.decode("utf-8") # type: ignore [assignment]
                    try:
                        response_body = json.loads(response_body)
                    except json.JSONDecodeError as decode_error:
                        logger.warning(
                            "Failed to decode the JSON body response: %s", decode_error
                        )

        except Exception as exc:
            logger.warning("Could not extract response body: %s", exc)

        status_code = getattr(response, "status_code", 500)

        return cls(
            request_method=method,
            request_body=request_body_str,
            request_url_path=endpoint_path,
            request_query_params=query_params,
            request_path_params=path_params,
            headers=headers,
            response_body=response_body,
            response_status_code=status_code,
        )
