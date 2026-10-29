
const uploadBtn = document.getElementById("upload-btn");
const fileInput = document.getElementById("img-uploader");
const form = document.getElementById("upload-form");

const cropModal = document.getElementById("crop-modal");
const cropImage = document.getElementById("crop-image");
const cropCloseBtn = document.getElementById("crop-close");
const cropUploadBtn = document.getElementById("crop-upload");

let cropper = null;
let originalFile = null;

uploadBtn.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;

  if (!file.type.startsWith("image/")) {
    alert("Pasirinkite nuotraukos failą.");
    fileInput.value = "";
    return;
  }

  originalFile = file;

  if (cropper) {
    cropper.destroy();
    cropper = null;
  }

  const reader = new FileReader();

  reader.onload = () => {
    cropImage.src = reader.result;
    cropModal.hidden = false;

    cropImage.onload = () => {
      cropper = new Cropper(cropImage, {
        aspectRatio: 1,
        viewMode: 1,
        dragMode: "move",
        autoCropArea: 0.9,
        responsive: true,
        background: false,
        zoomable: true,
        movable: true,
      });
    };
  };

  reader.readAsDataURL(file);
});

function closeCropModal() {
  cropModal.hidden = true;

  if (cropper) {
    cropper.destroy();
    cropper = null;
  }

  cropImage.removeAttribute("src");
  fileInput.value = "";
  originalFile = null;
}

cropCloseBtn.addEventListener("click", closeCropModal);

cropModal.addEventListener("click", (event) => {
  if (event.target === cropModal) {
    closeCropModal();
  }
});

cropUploadBtn.addEventListener("click", () => {
  if (!cropper || !originalFile) return;

  cropUploadBtn.disabled = true;
  cropUploadBtn.textContent = "Įkeliama...";

  const canvas = cropper.getCroppedCanvas({
    width: 512,
    height: 512,
    imageSmoothingEnabled: true,
    imageSmoothingQuality: "high",
  });

  canvas.toBlob((blob) => {
    if (!blob) {
      alert("Nepavyko apkirpti nuotraukos.");
      cropUploadBtn.disabled = false;
      cropUploadBtn.textContent = "Apkirpti ir įkelti";
      return;
    }

    const croppedFile = new File(
      [blob],
      "profile-photo.jpg",
      { type: "image/jpeg" }
    );

    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(croppedFile);

    fileInput.files = dataTransfer.files;

    // Submit the original form, including its CSRF token.
    HTMLFormElement.prototype.submit.call(form);
  }, "image/jpeg", 0.92);
});
