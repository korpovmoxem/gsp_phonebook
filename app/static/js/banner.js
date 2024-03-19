let banner = document.querySelector(".banner"); // Банер на 27 строке
let header = document.querySelector(".header"); // Хедер, который появляется вместо банера на 42 строке
let switchEl = document.querySelector(".switch"); // Инпут на 61

if (localStorage.getItem("switchState")) {
  switchEl.checked = JSON.parse(localStorage.getItem("switchState"));
}
switchEl.addEventListener("change", () => {
  const { checked } = switchEl;
  localStorage.setItem("switchState", checked);
});

switchEl.addEventListener("click", () => {
  const bannerHidden = localStorage.getItem("toggleBanner");
  const headerVisible = localStorage.getItem("toggleHeader");
  if (bannerHidden) {
    banner.classList.remove("hidden");
    localStorage.removeItem("toggleBanner");
  } else {
    banner.classList.add("hidden");
    localStorage.setItem("toggleBanner", "true");
  }

  if (headerVisible) {
    header.classList.add("hidden");
    localStorage.removeItem("toggleHeader");
  } else {
    header.classList.remove("hidden");
    localStorage.setItem("toggleHeader", "true");
  }
});

if (localStorage.getItem("toggleBanner")) {
  document.querySelector(".header").classList.remove("hidden");
  document.querySelector(".banner").classList.add("hidden");
}
