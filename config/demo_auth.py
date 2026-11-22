import base64
import hmac
import os

from django.http import HttpResponse


class DemoBasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.username = os.environ["DEMO_AUTH_USER"]
        self.password = os.environ["DEMO_AUTH_PASSWORD"]

        if not self.username or not self.password:
            raise RuntimeError("Demo credentials must not be empty")

    def __call__(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")

        try:
            scheme, encoded = header.split(" ", 1)
            if scheme.lower() != "basic":
                raise ValueError()

            decoded = base64.b64decode(
                encoded, validate=True
            ).decode("utf-8")

            username, password = decoded.split(":", 1)

            valid = (
                hmac.compare_digest(username, self.username)
                and hmac.compare_digest(password, self.password)
            )

        except (ValueError, UnicodeError):
            valid = False

        if not valid:
            response = HttpResponse(
                "TCF Demo Preview - Authentication required",
                status=401
            )
            response["WWW-Authenticate"] = 'Basic realm="TCF Demo Preview"'
            response["Cache-Control"] = "no-store"
            return response

        return self.get_response(request)
