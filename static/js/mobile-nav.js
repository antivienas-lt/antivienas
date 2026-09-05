
const burgerClose = document.getElementById("BurgerCloseSVG");
const burger = document.getElementById("BurgerSVG");
const nav_links = document.getElementById("NavLinks");

function toggleNav() {
  burger.classList.toggle("burger-hidden");
  burgerClose.classList.toggle("burger-hidden");
  console.log(nav_links.style.display);

  if (nav_links.style.display == ""){
    nav_links.style.display = "flex";
  } 
  else{
    nav_links.style.display = ""
  }
}

// Open / Close when burger is clicked
burger.addEventListener("click", toggleNav);
burgerClose.addEventListener("click", toggleNav);

document.addEventListener("click", function (event) {
  const isClickInsideNav = nav_links.contains(event.target);
  const isClickOnBurger = burger.contains(event.target);
  const isClickOnClose = burgerClose.contains(event.target);

  const navIsOpen = nav_links.style.display === "flex";

  if (navIsOpen && !isClickInsideNav && !isClickOnBurger && !isClickOnClose) {
    nav_links.style.display = "";
    burgerClose.classList.add("burger-hidden");
    burger.classList.remove("burger-hidden");
  }
});
