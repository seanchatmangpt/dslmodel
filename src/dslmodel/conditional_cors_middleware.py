# conditional_cors_middleware.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send


class ConditionalCORSMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app: ASGIApp,
            allow_origins: list,
            allow_credentials: bool = True,
            allow_methods: list = ["*"],
            allow_headers: list = ["*"],
            exclude_paths: list = None,
    ):
        super().__init__(app)
        self.allow_origins = allow_origins
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.exclude_paths = exclude_paths or []

    async def dispatch(self, request, call_next):
        # Check if the request path is excluded from CORS
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Handle CORS
        origin = request.headers.get("origin")
        if origin and origin in self.allow_origins:
            if request.method == "OPTIONS":
                # Preflight request
                response = Response(status_code=200)
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
                response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
                response.headers["Access-Control-Allow-Credentials"] = "true" if self.allow_credentials else "false"
                return response
            else:
                # Actual request
                response = await call_next(request)
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true" if self.allow_credentials else "false"
                return response
        else:
            # No CORS headers if origin is not allowed
            return await call_next(request)
