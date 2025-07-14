document.addEventListener("DOMContentLoaded", function () {
    const thumbnails = document.querySelectorAll(".thumbnail-image");
    const focusedImg = document.getElementById("focused-slide-img");
    const contrastSpan = document.getElementById("slide-contrast");
    const wordsSpan = document.getElementById("slide-words");
    const fontSizes = document.getElementById("slide-font-sizes");
    const feedback = document.getElementById("slide-feedback-words");

    thumbnails.forEach((thumb) => {
      thumb.addEventListener("click", function () {
        const newSrc = this.dataset.slideSrc;
        const newContrast = this.dataset.contrast;
        const newWords = this.dataset.words;
        const feedbackContrastText = this.dataset.fontSize;
        const feedbackWordsText = this.dataset.feedback;

        focusedImg.src = newSrc;
        contrastSpan.textContent = newContrast;
        wordsSpan.textContent = newWords;
        fontSizes.textContent = feedbackContrastText;
        feedback.textContent = feedbackWordsText;
    });
  });
});