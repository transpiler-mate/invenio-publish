# Copyright 2026 Transpiler-Mate
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import re
from functools import wraps
from http import HTTPStatus
from typing import TYPE_CHECKING, ParamSpec, cast

from httpx import Client, Headers, Request, RequestNotRead, Response
from loguru import logger
from transpiler_mate.api import PluginExecutionError

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

P = ParamSpec("P")


def _decode(value: bytes | str | None) -> str:
    if not value:
        return ""

    if isinstance(value, str):
        return value

    return value.decode("utf-8")


def _log_request(func: Callable[P, Request]) -> Callable[P, Request]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Request:
        request: Request = func(*args, **kwargs)

        logger.warning(f"{request.method} {request.url}")

        headers: Headers = request.headers
        for name, value in headers.raw:
            header_value = re.sub(
                r"(\bBearer\s+)[^\s]+",
                r"\1********",
                _decode(value),
                flags=re.IGNORECASE,
            )
            logger.warning(f"> {_decode(name)}: {header_value}")

        logger.warning(">")
        try:
            if request.content:
                logger.warning(_decode(request.content))
        except RequestNotRead:
            logger.warning("[REQUEST BUILT FROM STREAM, OMISSING]")

        return request

    return wrapper


def _log_response(func: Callable[P, Response]) -> Callable[P, Response]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Response:
        response: Response = func(*args, **kwargs)

        if HTTPStatus.MULTIPLE_CHOICES._value_ <= response.status_code:
            log = logger.error
        else:
            log = logger.success

        status: HTTPStatus = HTTPStatus(response.status_code)
        log(f"< {status._value_} {status.phrase}")

        headers: Mapping[str, str] = response.headers
        for name, value in headers.items():
            log(f"< {_decode(name)}: {_decode(value)}")

        log("")

        if response.content:
            log(_decode(response.content))

        if HTTPStatus.MULTIPLE_CHOICES._value_ <= response.status_code:
            raise PluginExecutionError(
                f"A server error occurred when invoking {cast('str', kwargs['method']).upper()} {kwargs['url']}, read the logs for details"
            )
        return response

    return wrapper


def init_http_logging(http_client: Client) -> None:
    http_client.build_request = _log_request(http_client.build_request)  # type: ignore
    http_client.request = _log_response(http_client.request)  # type: ignore
