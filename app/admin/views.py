from sqladmin import ModelView
from app.models import Bookings, Users, Rooms, Hotels


class UsersAdmin(ModelView, model=Users):
    can_delete = True
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"
    column_exclude_list = [Users.hashed_password]
    column_details_exclude_list = [Users.hashed_password]
    page_size = 100


class BookingsAdmin(ModelView, model=Bookings):
    can_delete = True
    name = "Бронирование"
    name_plural = "Бронирования"
    icon = "fa-solid fa-book"
    column_list = "__all__"
    page_size = 100


class HotelsAdmin(ModelView, model=Hotels):
    can_delete = True
    name = "Отель"
    name_plural = "Отели"
    icon = "fa-solid fa-hotel"
    column_list = "__all__"
    page_size = 100


class RoomsAdmin(ModelView, model=Rooms):
    can_delete = True
    name = "Комната"
    name_plural = "Комнаты"
    icon = "fa-solid fa-bed"
    column_list = "__all__"
    page_size = 100
