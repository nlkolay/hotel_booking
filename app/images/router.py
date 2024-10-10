import aiohttp
from fastapi import APIRouter, UploadFile

from app.tasks.tasks import process_pic


router = APIRouter(
    prefix='/images',
    tags=['Load images']
)

@router.post('/hotels')
# async def add_hotel_image(name: int, file: UploadFile):
#     with open(f'app/static/images/{name}.webp', 'wb+') as file_object:
#             # shutil.copyfileobj(file.file, file_object)


async def download_file(name: int, url: str, file_path: str = "app/static/images/") -> None:
    """
    Асинхронно скачивает файл из указанного URL и сохраняет его в указанное место на диске.\n    
    :param url: URL на файл для скачивания\n
    :param file_path: Путь на диске для сохранения файла\n
    """
    file_path += f"{name}.webp"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(file_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        file.write(chunk)
                print(f"Файл успешно сохранен в {file_path}")
            else:
                print(f"Не удалось скачать файл. Статус код: {response.status}")
    
    process_pic.delay(file_path)
