from app.services.nl_to_sql_service import NLToSQLService


class ServiceContainer:
    def __init__(self):
        self._nl_to_sql_service: NLToSQLService | None = None

    @property
    def nl_to_sql_service(self) -> NLToSQLService:
        if self._nl_to_sql_service is None:
            self._nl_to_sql_service = NLToSQLService()

        return self._nl_to_sql_service

    def override_nl_to_sql_service(self, service) -> None:
        self._nl_to_sql_service = service

    def reset(self) -> None:
        self._nl_to_sql_service = None


service_container = ServiceContainer()