import pytest
from app.dao import UserDAO


@pytest.mark.parametrize('user_id, user_email, is_present', [
    (1, 'test@test.com',  True),
    (2, "artem@example.com",  True),
    (3, 'test2@test.com', False),
])
async def test_get_user_by_email(user_id, user_email, is_present):
    user = await UserDAO.get_user_by_email(user_email)
    if  is_present:
        assert user
        assert user.id == user_id
        assert user.email == user_email
    else:
        assert user is None