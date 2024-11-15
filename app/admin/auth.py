# Аутентификация админки sqladmin
# TODO: добавить роли юзеров - https://stepik.org/lesson/926340/step/9?discussion=7562112&reply=7740346&unit=932223
from app.config import settings
from app.dependencies import authenticate_user, create_access_token, get_current_user
from fastapi import HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request, response: Response) -> bool:
        form = await request.form()
        email, password = str(form["username"]), str(form["password"])

        user = await authenticate_user(email, password)
        if user:
            access_token = create_access_token({"sub": str(user.email)})
            #request.session.update({"token_admin": access_token})
            # Set cookie in response
            response.set_cookie(
                key="token",
                value=access_token,
                httponly=True,
                secure=True,  # Use a setting to determine if HTTPS is used
                samesite="None"  # Adjust based on your CORS policy
            )
        return True

    async def logout(self, response: Response) -> bool:
        response.delete_cookie(key="token")
        return True

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        try:
            await get_current_user(request)
        except HTTPException as exc:
            if exc.status_code == 401:
                return RedirectResponse(request.url_for("admin:login"), status_code=302)
        return True


authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
