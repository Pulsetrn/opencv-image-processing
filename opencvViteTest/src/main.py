import asyncio
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
import cv2
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Разрешение CORS для всех доменов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def read_image(file) -> np.ndarray:
    """
    Read an image file uploaded via FastAPI and return it as a NumPy array.

    Parameters:
    file (UploadFile): The uploaded image file.

    Returns:
    np.ndarray: The image as a NumPy array (NumPy ndarray).

    """
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def write_image_to_bytes(image) -> bytes:
    """
    Convert the given image array to a base64-encoded bytes format.

    Parameters:
    image (np.ndarray): The input image as a NumPy array.

    Returns:
    bytes: The base64-encoded bytes representation of the image.

    """
    _, buffer = cv2.imencode(".jpg", image)
    image_str = base64.b64encode(buffer).decode("utf-8")
    return image_str


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    """
    Endpoint to upload an image file and return metadata along with the base64 representation of the image.

    Parameters:
    file (UploadFile): The uploaded image file.

    Returns:
    dict: A dictionary containing imageBase64, filename, width, and height of the uploaded image.

    """
    image = await read_image(file)
    return {
        "imageBase64": write_image_to_bytes(image),
        "filename": file.filename,
        "width": image.shape[1],
        "height": image.shape[0],
    }


@app.post("/channel/{channel}")
async def show_channel(file: UploadFile = File(...), channel: str = None):
    """
    Endpoint to manipulate the color channels of an uploaded image and return the modified image.

    Parameters:
    file (UploadFile): The uploaded image file.
    channel (str): The color channel to be extracted ("red", "green", or "blue").

    Returns:
    dict: A dictionary containing the base64 representation of the modified image.

    Raises:
    HTTPException: If an invalid or unsupported channel is specified.

    """
    image = await read_image(file)
    if channel.lower() == "red":
        channel_image = image.copy()
        channel_image[:, :, 1] = 0  # Zero out green channel
        channel_image[:, :, 2] = 0  # Zero out blue channel
        return {"imageBase64": write_image_to_bytes(channel_image)}
    elif channel.lower() == "green":
        channel_image = image.copy()
        channel_image[:, :, 0] = 0  # Zero out blue channel
        channel_image[:, :, 2] = 0  # Zero out red channel
        return {"imageBase64": write_image_to_bytes(channel_image)}
    elif channel.lower() == "blue":
        channel_image = image.copy()
        channel_image[:, :, 0] = 0  # Zero out red channel
        channel_image[:, :, 1] = 0  # Zero out green channel
        return {"imageBase64": write_image_to_bytes(channel_image)}
    else:
        raise HTTPException(
            status_code=404,
            detail="Error was occured",
            headers={"X-Error": "There goes my error"},
        )


@app.post("/crop/{x}/{y}/{w}/{h}")
async def crop_image(x: int, y: int, w: int, h: int, file: UploadFile = File(...)):
    """
    Endpoint to crop an uploaded image based on the provided coordinates and dimensions.

    Parameters:
    x (int): The x-coordinate of the top-left corner of the crop.
    y (int): The y-coordinate of the top-left corner of the crop.
    w (int): The width of the crop.
    h (int): The height of the crop.
    file (UploadFile): The uploaded image file.

    Returns:
    dict: A dictionary containing the base64 representation of the cropped image.

    """
    image = await read_image(file)
    cropped_image = image[y : y + h, x : x + w]
    return {"imageBase64": write_image_to_bytes(cropped_image)}


@app.post("/rotate/{angle}")
async def rotate_image(file: UploadFile = File(...), angle: float = 0.0):
    """
    Endpoint to rotate an uploaded image by a specified angle.

    Parameters:
    file (UploadFile): The uploaded image file.
    angle (float): The angle in degrees by which the image should be rotated.

    Returns:
    dict: A dictionary containing the base64 representation of the rotated image.

    """
    image = await read_image(file)
    rows, cols = image.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (cols, rows))
    return {"imageBase64": write_image_to_bytes(rotated_image)}


@app.post("/draw/{x}/{y}/{w}/{h}")
async def draw_rectangle(x: int, y: int, w: int, h: int, file: UploadFile = File(...)):
    """
    Endpoint to draw a blue rectangle on an uploaded image based on the provided coordinates and dimensions.

    Parameters:
    x (int): The x-coordinate of the top-left corner of the rectangle.
    y (int): The y-coordinate of the top-left corner of the rectangle.
    w (int): The width of the rectangle.
    h (int): The height of the rectangle.
    file (UploadFile): The uploaded image file.

    Returns:
    dict: A dictionary containing the base64 representation of the image with the drawn rectangle.

    """
    image = await read_image(file)
    drawn_image = image.copy()
    drawn_image = cv2.rectangle(
        drawn_image, (x, y), (x + w, y + h), (255, 0, 0), 2
    )  # Blue rectangle
    return {"imageBase64": write_image_to_bytes(drawn_image)}


async def main():
    """
    Asynchronous function to configure uvicorn server and run the FastAPI application.

    """
    config = uvicorn.Config("main:app", reload=True)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
