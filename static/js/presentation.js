document.addEventListener('DOMContentLoaded', () => {
  const thumbnails = document.querySelectorAll('.thumbnail-image');
  const focusedImg = document.getElementById('focused-slide-img');

  thumbnails.forEach(thumbnail => {
    thumbnail.addEventListener('click', () => {
      focusedImg.src = thumbnail.dataset.slideSrc;
    });
  });
});