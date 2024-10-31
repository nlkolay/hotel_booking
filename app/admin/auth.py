from typing import Optional
from fastapi import HTTPException, Request
from sqladmin.authentication import AuthenticationBackend
# from starlette.requests import Request
# from starlette.responses import RedirectResponse
from fastapi.responses import RedirectResponse
from app.dependencies import authenticate_user, create_access_token, get_current_user
from app.config import settings


class AdminAuth(AuthenticationBackend):
    async def login(
            self, 
            request: Request
            ) -> bool:
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
