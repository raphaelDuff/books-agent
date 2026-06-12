# infra/db/mappers/user_mapper.py
from app.domain.entities.user import UserDomain
from app.domain.value_objects import Email, UserRole
from app.infra.db.models.user_model import UserSQLModel


class UserMapper:
    @staticmethod
    def to_domain(model: UserSQLModel) -> UserDomain:
        user = UserDomain(
            name=model.name,
            email=Email(model.email),
            password_hash=model.password_hash,
            role=UserRole(model.role),
            birth_date=model.birth_date,
            is_active=model.is_active,
            created_at=model.created_at,
        )
        user.id = model.id
        return user

    @staticmethod
    def to_model(entity: UserDomain, model: UserSQLModel | None = None) -> UserSQLModel:
        if model is None:
            # Creating a new row
            model = UserSQLModel(
                id=entity.id,
                name=entity.name,
                email=str(entity.email),
                password_hash=entity.password_hash,
                role=entity.role,
                birth_date=entity.birth_date,
                is_active=entity.is_active,
                created_at=entity.created_at,
            )
            return model
        model.name = entity.name
        model.email = entity.email
        model.password_hash = entity.password_hash
        model.created_at = entity.created_at
        model.role = entity.role
        model.birth_date = entity.birth_date
        model.is_active = entity.is_active
        return model
