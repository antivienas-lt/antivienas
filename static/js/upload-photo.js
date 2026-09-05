const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('img-uploader');
const form = document.getElementById("upload-form");

uploadBtn.addEventListener('click', () => {
  fileInput.click();
});

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    form.submit();
  }
});