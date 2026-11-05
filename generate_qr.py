
import qrcode
import psycopg
from pathlib import Path


# Папка для сохранения QR-кодов
QR_FOLDER = Path("qr_codes")
QR_FOLDER.mkdir(exist_ok=True)

# Адрес страницы создания заявки в FastAPI
BASE_URL = "http://192.168.1.107:8000/tickets/create"

# Настройки подключения к College Helper
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "dbname": "college_helper",
    "user": "admin",
    "password": "admin123"
}


def generate_qr(location_id, room_number):
    url = f"{BASE_URL}?location_id={location_id}"

    qr = qrcode.make(url)

    file_path = QR_FOLDER / f"location_{location_id}.png"
    qr.save(file_path)

    print(f"QR-код для помещения {room_number} создан: {file_path}")


def generate_all_qr():
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, room_number FROM locations ORDER BY id"
                )

                locations = cursor.fetchall()

        if not locations:
            print("В таблице locations пока нет помещений.")
            return

        for location_id, room_number in locations:
            generate_qr(location_id, room_number)

        print("Генерация QR-кодов завершена!")

    except psycopg.Error as error:
        print(f"Ошибка подключения к базе данных: {error}")


if __name__ == "__main__":
    generate_all_qr()

