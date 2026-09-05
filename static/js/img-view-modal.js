const modal = document.getElementById("modal");
const closeBtn = document.querySelector(".close");
const modalImage = document.getElementById("modalImage");
const miniatures = Array.from(document.querySelectorAll(".miniature-img"));

let currentIndex = 0;

function openImage(index) {
    currentIndex = index;
    modalImage.src = miniatures[currentIndex].src;
    modal.style.display = "flex";
}

function showImage(index) {
    // Wrap around at either end
    if (index >= miniatures.length) {
        index = 0;
    }

    if (index < 0) {
        index = miniatures.length - 1;
    }

    currentIndex = index;
    modalImage.src = miniatures[currentIndex].src;
}

function closeModal() {
    modal.style.display = "none";
}

closeBtn.addEventListener("click", closeModal);

// Close when clicking outside the image
modal.addEventListener("click", (e) => {
    if (e.target === modal) {
        closeModal();
    }
});

// Open miniature
miniatures.forEach((element, index) => {
    element.addEventListener("click", () => {
        openImage(index);
    });
});

// Keyboard navigation
document.addEventListener("keydown", (e) => {
    // Don't do anything if modal isn't open
    if (modal.style.display !== "flex") {
        return;
    }

    switch (e.key) {
        case "Escape":
            closeModal();
            break;

        case "ArrowRight":
            e.preventDefault();
            showImage(currentIndex + 1);
            break;

        case "ArrowLeft":
            e.preventDefault();
            showImage(currentIndex - 1);
            break;
    }
});