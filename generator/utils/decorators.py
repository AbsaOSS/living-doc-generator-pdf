#
# Copyright 2023 ABSA Group Limited
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
#

"""Decorators used across the project.

This file is intentionally dependency-light to keep the action runtime small.
"""

import logging

from functools import wraps
from typing import Callable, Optional, Any
from requests.exceptions import Timeout, RequestException

logger = logging.getLogger(__name__)


def debug_log_decorator(method: Callable) -> Callable:
    """
    Decorator to add debug logging for a method call.

    @param method: The method to decorate.
    @return: The decorated method.
    """

    @wraps(method)
    def wrapped(*args, **kwargs) -> Optional[Any]:
        logger.debug("Calling method %s with args: %s and kwargs: %s", method.__name__, args, kwargs)
        result = method(*args, **kwargs)
        logger.debug("Method %s returned %s", method.__name__, result)
        return result

    return wrapped


# pylint: disable=broad-except
def safe_call_decorator(rate_limiter: Callable) -> Callable:
    """
    Decorator factory to create a rate-limited safe call function.

    @param rate_limiter: The rate limiter to use.
    @return: The decorator.
    """

    def decorator(method: Callable) -> Callable:
        # Note: Keep log decorator first to log correct method name.
        @debug_log_decorator
        @wraps(method)
        @rate_limiter
        def wrapped(*args, **kwargs) -> Optional[Any]:
            try:
                return method(*args, **kwargs)
            except (ConnectionError, Timeout) as e:
                logger.error("Network error calling %s: %s", method.__name__, e, exc_info=True)
                return None
            except RequestException as e:
                logger.error("HTTP error calling %s: %s", method.__name__, e, exc_info=True)
                return None
            except Exception as e:
                logger.error("Unexpected error calling %s: %s", method.__name__, e, exc_info=True)
                return None

        return wrapped

    return decorator
