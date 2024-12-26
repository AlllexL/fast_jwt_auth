from auth import utils as utils_auth
from users.schemas import UserSchemas

john = UserSchemas(
    username="john",
    password=utils_auth.hash_password("qwerty"),
    email="john@example.com",
)
sam = UserSchemas(
    username="sam",
    password=utils_auth.hash_password("secret"),
)
users_db: dict[str, UserSchemas] = {john.username: john, sam.username: sam}
