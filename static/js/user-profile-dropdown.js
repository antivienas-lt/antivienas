const dropdown = document.getElementById('avatarDropdown');
const menuButton = document.getElementById('avatarMenuButton');

document.addEventListener('click', (e) => {
  if (!dropdown.contains(e.target) && e.target !== menuButton) {
    dropdown.style.display = 'none';
  }
});
// Toggle dropdown
menuButton.addEventListener('click', (e) => {
  e.stopPropagation();
  dropdown.style.display = dropdown.style.display === 'flex' ? 'none' : 'flex';
});

dropdown.addEventListener('click', (e) => {
  e.stopPropagation();
});