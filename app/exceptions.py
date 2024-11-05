# Описание исключений HTTP

from fastapi import HTTPException, status


class Exception(HTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = ""
    
    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

class RoomIsNotAvailable(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    detail="Комната недоступна на выбранные даты."

class InvalidCredentials(Exception):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверные данные пользователя."

class NotLoggedIn(Exception):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Пожалуйста, войдите в аккаунт."

class BookingNotFound(Exception):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Бронирование не найдено."

class EmailNotValid(Exception):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Некорректный e-mail."

class EmailAlreadyUsed(Exception):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="E-mail уже использован."

class NoVacation(Exception):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Нет доступных номеров на указанные даты."

class DatesInvalid(Exception):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Дата начала бронирования должна быть меньше или равна дате окончания."

class TooLong(Exception):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Длительность бронирования не может превышать 30 дней."

