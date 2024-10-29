from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.database import get_db
from app.dependencies import authenticate_user, create_access_token, get_current_user


class AdminAuth(AuthenticationBackend):
    async def login(
            self, 
            request: Request, 
            db: AsyncSession = Depends(get_db)
            ) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]

        user = await authenticate_user(db, email, password)
        if user:
            access_token = create_access_token(data={"sub": user.email})
            request.session.update({"token": "..."})

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return RedirectResponse(request.url_for('admin:login'), status_code=302)
                
        user = await get_current_user(token)

        if not user:
            return RedirectResponse(request.url_for('admin:login'), status_code=302)

        # Check the token in depth
        return True


authentication_backend = AdminAuth(secret_key="...")
