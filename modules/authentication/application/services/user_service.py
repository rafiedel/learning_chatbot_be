from modules.authentication.domain.entities.user_entitiy import UserEntity
from modules.authentication.infrastructure.token_provider import TokenProvider
from modules.authentication.infrastructure.repositories.user_repository import UserRepository

class UserService:
    def __init__(
        self,
        repository: UserRepository | None = None,
        token_provider: TokenProvider | None = None,
    ):
        self.repo = repository or UserRepository()
        self.tokens = token_provider or TokenProvider()

    def register(self, *, username: str, email: str, password: str) -> UserEntity:
        model = self.repo.add_user(username, email, password)
        return UserEntity(id=model.id, username=model.username, email=model.email)

    def login(
        self, *, username: str, password: str
    ) -> dict | None:
        model = self.repo.get_user(username, password)
        if model is None:
            return None
        return self.tokens.tokens_for(model)