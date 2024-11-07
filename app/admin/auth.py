# Аутентификация админки sqladmin
# TODO: добавить роли юзеров - https://stepik.org/lesson/926340/step/9?discussion=7562112&reply=7740346&unit=932223
from app.config import settings
from app.dependencies import authenticate_user, create_access_token, get_current_user
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = str(form["username"]), str(form["password"])

        user = await authenticate_user(email, password)
        if user:
            access_token = create_access_token({"sub": str(user.email)})
            request.session.update({"token": access_token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        try:
            user = await get_current_user(request)
        except HTTPException as exc:
            if exc.status_code == 401:
                return RedirectResponse(request.url_for("admin:login"), status_code=302)
        return True


authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
