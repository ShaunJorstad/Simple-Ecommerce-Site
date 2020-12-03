const loadFile = function (event, imageId) {
    const image = document.getElementById(imageId);
    image.src = URL.createObjectURL(event.target.files[0]);
};