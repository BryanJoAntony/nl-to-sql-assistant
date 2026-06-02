from app.services.nl_to_sql_service import NLToSQLService


class ServiceContainer:
    def __init__(self):
        self._nl_to_sql_service: NLToSQLService | None = None

    @property
    def nl_to_sql_service(self) -> NLToSQLService:
        if self._nl_to_sql_service is None:
            self._nl_to_sql_service = NLToSQLService()

        return self._nl_to_sql_service


service_container = ServiceContainer()