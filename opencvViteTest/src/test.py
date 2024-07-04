import cv2
import numpy as np


# Шаг 1: Загрузка изображения
def load_image():
    while True:
        file_path = input("Введите путь к изображению (png или jpg): ")
        image = cv2.imread(file_path)
        if image is not None:
            return image
        else:
            print(
                "Ошибка: Невозможно загрузить изображение. Убедитесь, что путь правильный."
            )


# Шаг 2: Показ изображения
def show_image(image, window_name="Image"):
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyWindow(window_name)  # Закрыть окно при нажатии на любую клавишу


# Шаг 3: Выбор канала
def show_color_channel(image, color="blue"):
    if color == "blue":
        blue_channel = image[:, :, 0]
        show_image(blue_channel, "Blue Channel")
    elif color == "green":
        green_channel = image[:, :, 1]
        show_image(green_channel, "Green Channel")
    elif color == "red":
        red_channel = image[:, :, 2]
        show_image(red_channel, "Red Channel")
    else:
        print("Ошибка: Недопустимый цвет.")


# Шаг 4: Обрезка изображения
def crop_image(image, x, y, w, h):
    cropped_image = image[y : y + h, x : x + w]
    return cropped_image


# Шаг 5: Вращение изображения
def rotate_image(image, angle):
    rows, cols = image.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (cols, rows))
    return rotated_image


# Шаг 6: Нарисовать прямоугольник
def draw_rectangle(image, x, y, w, h):
    image_with_rectangle = cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    show_image(image_with_rectangle, "Image with Rectangle")


# Основная программа
if __name__ == "__main__":
    image = load_image()
    show_image(image)

    color_choice = input("Выберите канал (red/green/blue): ")
    show_color_channel(image, color_choice)

    x = int(input("Введите координату x для обрезки: "))
    y = int(input("Введите координату y для обрезки: "))
    w = int(input("Введите ширину обрезки: "))
    h = int(input("Введите высоту обрезки: "))
    cropped_image = crop_image(image, x, y, w, h)
    show_image(cropped_image, window_name="Cropped Image")

    angle = float(input("Введите угол вращения: "))
    rotated_image = rotate_image(image, angle)
    show_image(rotated_image, window_name="Rotated Image")

    x_rect = int(input("Введите координату x верхнего левого угла прямоугольника: "))
    y_rect = int(input("Введите координату y верхнего левого угла прямоугольника: "))
    w_rect = int(input("Введите ширину прямоугольника: "))
    h_rect = int(input("Введите высоту прямоугольника: "))
    draw_rectangle(image, x_rect, y_rect, w_rect, h_rect)



"""
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import uvicorn
import cv2
import numpy as np
import io
from starlette.requests import Request
from starlette.templating import Jinja2Templates

app = FastAPI()


async def read_image(file) -> np.ndarray:
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def write_image_to_bytes(image) -> bytes:
    _, img_encoded = cv2.imencode(".png", image)
    return img_encoded.tobytes()


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    image = await read_image(file)
    return {
        "filename": file.filename,
        "width": image.shape[1],
        "height": image.shape[0],
    }


@app.get("/channel/{channel}")
async def show_channel(channel: str, file: UploadFile = File(...)):
    image = read_image(file)
    if channel.lower() == "red":
        channel_image = image.copy()
        channel_image[:, :, 1] = 0  # Zero out green channel
        channel_image[:, :, 2] = 0  # Zero out blue channel
        return write_image_to_bytes(channel_image)
    elif channel.lower() == "green":
        channel_image = image.copy()
        channel_image[:, :, 0] = 0  # Zero out blue channel
        channel_image[:, :, 2] = 0  # Zero out red channel
        return write_image_to_bytes(channel_image)
    elif channel.lower() == "blue":
        channel_image = image.copy()
        channel_image[:, :, 0] = 0  # Zero out red channel
        channel_image[:, :, 1] = 0  # Zero out green channel
        return write_image_to_bytes(channel_image)
    else:
        return {"error": "Invalid channel name. Please choose red, green, or blue."}


@app.get("/crop/")
async def crop_image(
    file: UploadFile = File(...), x1: int = 0, y1: int = 0, x2: int = 100, y2: int = 100
):
    image = read_image(file)
    cropped_image = image[y1:y2, x1:x2]
    return write_image_to_bytes(cropped_image)


@app.get("/rotate/")
async def rotate_image(file: UploadFile = File(...), angle: float = 0.0):
    image = read_image(file)
    rows, cols = image.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (cols, rows))
    return write_image_to_bytes(rotated_image)


@app.get("/draw_rectangle/")
async def draw_rectangle(
    file: UploadFile = File(...), x1: int = 0, y1: int = 0, x2: int = 100, y2: int = 100
):
    image = read_image(file)
    drawn_image = image.copy()
    cv2.rectangle(drawn_image, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Blue rectangle
    return write_image_to_bytes(drawn_image)


if __name__ == "__main__":
    uvicorn.run(app)
"""