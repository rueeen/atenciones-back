from django.db import connections
from django.db.utils import OperationalError, ProgrammingError
from django.http import HttpResponse


_auth_table_check_done = False
_auth_table_exists = True


class DatabaseMigrationGuardMiddleware:
    """
    Shows a clear setup message when required auth tables are missing.

    This prevents an opaque OperationalError crash on login when migrations
    have not been executed yet.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _auth_table_check_done, _auth_table_exists

        if not _auth_table_check_done:
            try:
                table_names = connections["default"].introspection.table_names()
                _auth_table_exists = "auth_user" in table_names
            except (OperationalError, ProgrammingError):
                _auth_table_exists = False
            finally:
                _auth_table_check_done = True

        if not _auth_table_exists:
            return HttpResponse(
                (
                    "Base de datos no inicializada. "
                    "Ejecuta `python manage.py migrate` y vuelve a intentar."
                ),
                status=503,
            )

        return self.get_response(request)
