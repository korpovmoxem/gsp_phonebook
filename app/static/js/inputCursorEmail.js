// Скрипт подсказка при наведении на инпут
// после загрузки страницы
$(function () {
  // инициализации подсказок для всех элементов на странице, имеющих атрибут data-toggle="tooltip"
  $('[data-toggle="tooltip"]').tooltip();
});

// Скрипт для Курсора(появляется при наведении на ссылку)

document.addEventListener("DOMContentLoaded", () => {
  const followCursor = () => {
    // объявляем функцию followCursor
    const el = document.querySelector(".follow-cursor"); // ищем элемент, который будет следовать за курсором

    window.addEventListener("mousemove", (e) => {
      // при движении курсора
      const target = e.target; // определяем, где находится курсор
      if (!target) return;

      if (target.closest(".page_number")) {
        // если курсор наведён на ссылку
        el.classList.add("follow-cursor_active"); // элементу добавляем активный класс
      } else {
        // иначе
        el.classList.remove("follow-cursor_active"); // удаляем активный класс
      }

      el.style.left = e.pageX + "px"; // задаём элементу позиционирование слева
      el.style.top = e.pageY + "px"; // задаём элементу позиционирование сверху
    });
  };

  followCursor(); // вызываем функцию followCursor
});
document.querySelector(".input").addEventListener("click", function () {
  this.removeAttribute("title");
});

// Скрипт для копирования EMAIL адресов

document
  .querySelector(".container__icon")
  .addEventListener("click", function (e) {
    let emails = document.querySelectorAll(".email__adress");
    let emailText = "";
    emails.forEach((email) => {
      emailText += email.textContent + "\n";
    });
    navigator.clipboard.writeText(emailText).catch(function (error) {
      console.error("Unable to copy to clipboard", error);
    });
  });
