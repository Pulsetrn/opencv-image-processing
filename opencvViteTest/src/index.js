// Global variables defined for various elements and configuration
// The initial values for some variables are set here
const form = document.querySelector("form");
const btn = document.querySelector("#submit");
const imageDiv = document.querySelector("#resultContainer");
const select = document.querySelector("#select-method");
const inputImage = document.querySelector("#inputfilename");
const deleteBtn = document.querySelector("#delete-photo");
const deleteWebPhotoBtn = document.querySelector("#endbutton");
const useWebcamBtn = document.querySelector("#startvideo");
deleteWebPhotoBtn.disabled = true;
deleteBtn.disabled = true;

let flagWebCam = false;
let errorWebcam = null;
let width = 320; // Этим создадим ширину фотографии
let height = 0; // Это будет вычисляться на основе входящего потока

// Убрать из глобальных переменных
let photoData = null;
let fileconvertedphoto = null;

let streaming = false;
let video = document.getElementById("video");
let canvas = document.getElementById("canvas");
let photo = document.getElementById("photo");
let startbutton = document.getElementById("startbutton");
startbutton.disabled = true;

useWebcamBtn.addEventListener("click", handleStartVideo);
deleteWebPhotoBtn.addEventListener("click", handleWebDelete);
deleteBtn.addEventListener("click", handleDelete);
form.addEventListener("submit", handleSubmit);
inputImage.addEventListener("change", handleChange);
video.addEventListener(
  "canplay",
  function (ev) {
    if (!streaming) {
      height = video.videoHeight / (video.videoWidth / width);

      video.setAttribute("width", width);
      video.setAttribute("height", height);
      canvas.setAttribute("width", 0);
      canvas.setAttribute("height", 0);
      streaming = true;
    }
  },
  false
);
startbutton.addEventListener(
  "click",
  function (ev) {
    takepicture();
    ev.preventDefault();
  },
  false
);

// sync main logic

/**
 * Checks whether the response that came from the backend is correct
 *
 * @param {Response} res - Response that came from backend
 * @returns {Boolean}
 */
function validate(res) {
  return res.ok;
}

/**
 * Creates an <img> tag with the received base64 image data and inserts it into the HTML div.
 *
 * @param {string} imageB - Base64 image data
 */
function loadImageHTML(imageB) {
  // С сервера приходит картинка, преобразованная в последовательность байтов с основанием 64
  // соответственно принимая ее на фронтенде, нам следует перевести ее обратно, чтобы отобразить
  const imagesrc = `data:image/jpeg;base64,${imageB}`;
  const newImageHTML = '<img src="' + imagesrc + '" alt="Uploaded Image" />';
  imageDiv.innerHTML = newImageHTML;
}

/**
 * A function that generates formdata, which is subsequently used to send a request
 *
 * @param {}
 * @returns {FormData}
 */
function chooseImage() {
  // input с type file хранит в себе все загруженные пользователем файлы, которые доступны по атрибуту files
  const fileInputs = document.querySelector("#inputfilename");
  // FormData - класс, позволяющий использовать формат ключ: значение
  const formData = new FormData();
  if (fileconvertedphoto) {
    formData.append("file", fileconvertedphoto);
  } else {
    formData.append("file", fileInputs.files[0]);
  }
  return formData;
}

/**
 * A function that validates a number entered by the user
 *
 * @param {String} message - message for alert
 * @returns {Number}
 */
function promptInteger(message) {
  let value;
  while (true) {
    value = prompt(message);
    if (!isNaN(value) && value >= 0) {
      return parseInt(value);
    } else {
      alert("Please enter a valid value: positive NUMBER");
    }
  }
}

// webcam logic

// Предоставление пользователю вомзонжости использования веб-камеры
/**
 * Handles starting the video stream from the webcam.
 *
 * @param {Event} e - The event object.
 */
function handleStartVideo(e) {
  e.preventDefault();
  navigator.mediaDevices
    .getUserMedia({ video: true, audio: false })
    .then(function (stream) {
      video.srcObject = stream;
      video.play();
      startbutton.disabled = false;
      flagWebCam = true;
    })
    .catch(function (err) {
      errorWebcam = true;
      alert(
        "An error occurred: " +
          err +
          ", try one more time to connect your webcam"
      );
    });
}

/**
 * Clears the photo displayed on the canvas.
 */
function clearphoto() {
  let context = canvas.getContext("2d");
  context.fillStyle = "#AAA";
  context.fillRect(0, 0, canvas.width, canvas.height);

  // Содзаем путь до img на base64 кодировке
  photoData = canvas.toDataURL("image/png");
  // photo.setAttribute("src", data);
}

/**
 * Captures a photo from the video stream and displays it on the canvas.
 * Converts the captured photo to a base64-encoded format.
 */
function takepicture() {
  if (errorWebcam) {
    alert(
      "An error occurred while displaying the webcam image, therefore it is impossible to take a photo, check the connection"
    );
  } else {
    let context = canvas.getContext("2d");
    if (width && height) {
      canvas.width = width;
      canvas.height = height;
      context.drawImage(video, 0, 0, width, height);

      // Содзаем путь до img на base64 кодировке
      // Изменяем глобальную переменную, с которой впсоледствии будем работать
      photoData = canvas.toDataURL("image/png");
      fileconvertedphoto = convertToFile(prompt("Input file name"), photoData);
      inputImage.disabled = true;
      deleteWebPhotoBtn.disabled = false;
    } else {
      clearphoto();
    }
  }
}

/**
 * Converts a base64-encoded image to a File object.
 *
 * @param {string} filename - The name to assign to the File object.
 * @param {string} data - The base64-encoded image data.
 * @returns {File} - The converted File object.
 */
function convertToFile(filename, data) {
  let byteCharacters = atob(
    data.replace(/^data:image\/(png|jpeg);base64,/, "")
  );
  let byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  let byteArray = new Uint8Array(byteNumbers);
  return new File([byteArray], filename, { type: "image/png" }); // Замените 'image/png' на соответствующий MIME-тип, если необходимо
}

// event handlers
/**
 * Handles form submission by uploading the chosen image based on the selected option.
 *
 * @param {Event} event - The form submission event.
 */
function handleSubmit(event) {
  event.preventDefault();
  // Вызываем функцию, которая заполнит formData, которая в свою очередь будет использоваться
  // при отправке HTTP запроса на сервер
  formData = chooseImage();
  const option = form.iselect.value;
  uploadImage(formData, option);
}

/**
 * Handles deleting the displayed image and resetting related variables and elements.
 */
function handleDelete() {
  imageDiv.innerHTML = "";
  photoData = null;
  fileconvertedphoto = null;
  if (startbutton.disabled && flagWebCam) {
    startbutton.disabled = false;
  }
  if (inputImage.disabled) {
    inputImage.disabled = false;
  }
  if (inputImage.value) {
    inputImage.value = "";
  }
}

/**
 * Handles changes in the selected image input.
 */
function handleChange() {
  startbutton.disabled = true;
}

/**
 * Handles deleting the webcam photo displayed on the canvas.
 */
function handleWebDelete() {
  canvas.width = 0;
  canvas.height = 0;
  photoData = null;
  fileconvertedphoto = null;
  deleteWebPhotoBtn.disabled = true;
  inputImage.disabled = false;
}

// async logic
/**
 * Uploads the image data to the server based on the selected option.
 *
 * @param {FormData} data - The image data to be uploaded.
 * @param {string} optn - The selected processing option.
 */
async function uploadImage(data, optn) {
  const response = await makeHttpRequest(data, optn);
  if (validate(response)) {
    const data = await response.json();
    alert(`The image was successfully processed`);
    deleteBtn.disabled = false;
    loadImageHTML(data.imageBase64);
  } else {
    alert("An error occurred while loading the image");
  }
}

/**
 * Makes an HTTP request to the server based on the selected processing option.
 *
 * @param {FormData} data - The image data to be sent in the request.
 * @param {string} optn - The selected processing option.
 * @returns {Promise<Response>} - The response from the server.
 */
async function makeHttpRequest(data, optn) {
  if (optn === "default-option") {
    return useFetch("http://127.0.0.1:8000/upload/", {
      method: "POST",
      body: data,
    });
  } else if (optn === "blue-option") {
    return useFetch(`http://127.0.0.1:8000/channel/${"red"}`, {
      method: "POST",
      body: data,
    });
  } else if (optn === "green-option") {
    return useFetch(`http://127.0.0.1:8000/channel/${"green"}`, {
      method: "POST",
      body: data,
    });
  } else if (optn === "red-option") {
    return useFetch(`http://127.0.0.1:8000/channel/${"blue"}`, {
      method: "POST",
      body: data,
    });
  } else if (optn === "crop-option") {
    x = promptInteger("Enter the left corner coordinate");
    y = promptInteger("Enter the coordinate of the right corner");
    w = promptInteger("Enter width");
    h = promptInteger("Enter coordinate height");
    return fetch(`http://127.0.0.1:8000/crop/${x}/${y}/${w}/${h}`, {
      method: "POST",
      body: data,
    });
  } else if (optn === "rotate-option") {
    angle = promptInteger("enter the rotation angle value");
    return useFetch(`http://127.0.0.1:8000/rotate/${angle}`, {
      method: "POST",
      body: data,
    });
  } else if (optn === "draw-option") {
    x = promptInteger("Enter the left corner coordinate");
    y = promptInteger("Enter the coordinate of the right corner");
    w = promptInteger("Enter width");
    h = promptInteger("Enter coordinate height");
    return useFetch(`http://127.0.0.1:8000/draw/${x}/${y}/${w}/${h}`, {
      method: "POST",
      body: data,
    });
  }
}

/**
 * Makes a fetch request to the specified URL with the provided options.
 *
 * @param {string} url - The URL to send the request to.
 * @param {Object} options - The options for the fetch request.
 * @returns {Promise<Response>} - The response from the fetch request.
 */
async function useFetch(url, options) {
  return fetch(url, options).catch(() => {
    alert(
      "An error occurred while sending the request, please try again later"
    );
  });
}
