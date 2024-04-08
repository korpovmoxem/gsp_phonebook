async function getOrganization() {
  try {
    const response = await fetch("get_organization_tree");
    const data = await response.json();
    const newData = JSON.parse(data);
    renderOrganization(newData);
  } catch (err) {
    console.log(err);
  }
}
getOrganization();

// function renderOrganization(jsonData) {
//   const menuContainer = document.querySelector(".menu__list");
//   jsonData.forEach((item) => {
//     const menuItems = createMenuItems(item.Name, item.Children);
//     menuContainer.insertAdjacentHTML("beforeend", menuItems);
//   });

//   applySavedMenuState();
// }
function renderOrganization(jsonData) {
  const menuContainer = document.querySelector(".menu__list");
  jsonData.forEach((item) => {
    const menuItems = createMenuItems(item.Name, item.Children, item.Inn);
    menuContainer.insertAdjacentHTML("beforeend", menuItems);
  });

  applySavedMenuState();
}

function applySavedMenuState() {
  let savedState = localStorage.getItem("menuState");
  if (savedState) {
    let menuState = JSON.parse(savedState);
    const menuItems = document.querySelectorAll(".menu__item");

    menuItems.forEach((item) => {
      let menuText = item.parentNode
        .querySelector(".menu__items")
        .textContent.trim();
      let menuItemsDown = item.parentNode.querySelector(".menu__items");
      let currentState = menuState[menuText] || false;

      item.classList.toggle("active", currentState);
      menuItemsDown.classList.toggle("menu__items-down", currentState);
    });
  }
}

// Вызываем функцию при загрузке страницы
applySavedMenuState();

// Сохраняем состояние элементов меню при изменении
document.querySelectorAll(".menu__item").forEach((item) => {
  item.addEventListener("click", () => {
    let menuText = item.parentNode
      .querySelector(".menu__items")
      .textContent.trim();
    let menuState = JSON.parse(localStorage.getItem("menuState")) || {};

    menuState[menuText] = !menuState[menuText]; // Изменяем состояние при каждом клике

    localStorage.setItem("menuState", JSON.stringify(menuState));
    applySavedMenuState(); // Перерисовываем меню при каждом клике
  });
});
// КОД-------------------------------
// function createMenuItems(name, children) {
//   let html = `<li class="myMainClass">
//       <span class="menu__items"><a href="">${name}</a></span>
//       <ul class="menu__item">`;
//   children.forEach((value) => {
//     const hasChildren =
//       Array.isArray(value.Children) && value.Children.length > 0;
//     html += createMenuItem(hasChildren, value);
//   });

//   html += `</ul>
//   </li>`;

//   return html;
// }
function createMenuItems(name, children, Inn) {
  console.log(Inn);
  let html = `<li class="myMainClass">
      <span class="menu__items"><a href="/organizations/${Inn}">${name}</a></span>
      <ul class="menu__item">`;
  children.forEach((value) => {
    const hasChildren =
      Array.isArray(value.Children) && value.Children.length > 0;
    html += createMenuItem(hasChildren, value);
  });

  html += `</ul>
  </li>`;

  return html;
}

function createMenuItem(hasChildren, value) {
  let html = "";

  if (hasChildren) {
    html += `<li>
        <span class="menu__items"><a href='/?organization=${
          value.Inn
        }&department=${value.ID}' style="${
      value.Filial === 1 ? "color: #007FFF;" : ""
    }">${value.Name}</a></span>
        <ul class="menu__item">`;

    value.Children.forEach((child) => {
      if (Array.isArray(child.Children) && child.Children.length === 0) {
        html += `<li><a href='/?organization=${child.Inn}&department=${
          child.ID
        }' style="${child.Filial === 1 ? "color: #007FFF;" : ""}">${
          child.Name
        }</a></li>`;
      }
      if (Array.isArray(child.Children) && child.Children.length > 0) {
        html += `<li><span class="menu__items"><a href='/?organization=${
          child.Inn
        }&department=${child.ID}' style="${
          child.Filial === 1 ? "color: #007FFF;" : ""
        }">${child.Name}</a></span>
            <ul class="menu__item">
            ${createChildItems(child.Children)}
            </ul></li>`;
      }
    });

    html += `</ul></li>`;
  } else {
    html += `<li><a href='/?organization=${value.Inn}&department=${
      value.ID
    }' style="${value.Filial === 1 ? "color: #007FFF;" : ""}">${
      value.Name
    }</a></li>`;
  }
  return html;
}

function createChildItems(children) {
  let html = "";
  children.forEach((child) => {
    if (Array.isArray(child.Children) && child.Children.length === 0) {
      html += `<li><a href='/?organization=${child.Inn}&department=${child.ID}'>${child.Name}</a></li>`;
    }
    if (Array.isArray(child.Children) && child.Children.length > 0) {
      html += `<li><span class="menu__items"><a href='/?organization=${
        child.Inn
      }&department=${child.ID}'>${child.Name}</a></span>
      <ul class="menu__item">
      ${createChildItems(child.Children)}
      </ul></li>`;
    }
  });
  return html;
}

// Сохранение состояния меню
function saveMenuState() {
  let menuState = {};
  document.querySelectorAll(".menu__item").forEach((subMenuItem) => {
    let key = subMenuItem.parentNode
      .querySelector(".menu__items")
      .textContent.trim();
    menuState[key] = subMenuItem.classList.contains("active");
  });

  localStorage.setItem("menuState", JSON.stringify(menuState));
}

document
  .querySelector(".menu__list")
  .addEventListener("click", function (event) {
    if (event.target.classList.contains("menu__items")) {
      event.preventDefault();

      let menuItems = event.target;
      let menuItem = menuItems.nextElementSibling;

      while (menuItem && menuItem.tagName !== "UL") {
        menuItem = menuItem.nextElementSibling;
      }

      if (menuItem) {
        menuItem.classList.toggle("active");
      }

      menuItems.classList.toggle("menu__items-down");

      saveMenuState();
    }
  });
// Восстановление состояния меню при загрузке страницы
document.addEventListener("DOMContentLoaded", function () {
  let savedState = localStorage.getItem("menuState");
  if (savedState) {
    let menuState = JSON.parse(savedState);
    Object.keys(menuState).forEach((key) => {
      let subMenuItem = Array.from(
        document.querySelectorAll(".menu__item")
      ).find((item) => {
        let menuItemsText = item.parentNode
          .querySelector(".menu__items")
          .textContent.trim();
        return menuItemsText === key;
      });

      if (subMenuItem) {
        subMenuItem.classList.toggle("active", menuState[key]);
        subMenuItem.parentNode
          .querySelector(".menu__items")
          .classList.toggle("menu__items-down", menuState[key]);
      }
    });
  }
});

// Обработчик события для кнопки "Свернуть все"
document.getElementById("toggleButton").addEventListener("click", function () {
  // Свернуть все элементы
  document.querySelectorAll(".menu__item").forEach((item) => {
    item.classList.remove("active");
  });
  document.querySelectorAll(".menu__items").forEach((menuItems) => {
    menuItems.classList.remove("menu__items-down");
  });

  saveMenuState(); // Сохранить состояние после сворачивания всех элементов
});

// -------------Появление теста с организацией и департаментом------------------------------

// // Убираем надпись через крестик при нажатии
// document.querySelector(".newText").addEventListener("click", () => {
//   document.querySelector(".newText").style.display = "none";
//   localStorage.removeItem("myText");
// });

// // Убираем надпись при нажатии кнопки "Искать"
// // document.querySelector('.btn ').addEventListener('click', () => {
// //   localStorage.removeItem('myText');
// // })

// // Добавляем надпись при нажатии на ссылку без плюса
// document.querySelectorAll(".menu__item > li > a").forEach((item) => {
//   item.addEventListener("click", function (e) {
//     let stroke = [];
//     let current = item.parentNode;
//     while (current.className != "myMainClass") {
//       if (current.nodeName == "UL") {
//         stroke.push(current.previousElementSibling.textContent);
//       }
//       current = current.parentNode;

//       //Сохранение данных после перезагрузки страницы
//       localStorage.setItem(
//         "myText",
//         "Поиск по: " + stroke.reverse().join(" -> ") + " -> " + item.textContent
//       );
//       localStorage.getItem("myText");
//     }
//     document.querySelector(".newText").innerText =
//       "Поиск по: " + stroke.join(" -> ") + " -> " + item.textContent;
//     document.querySelector(".newText").style.display = "flex";
//   });
// });

// // Добавляем надпись при нажатии на ссылку с плюсом
// document.querySelectorAll(".menu__item > li > span > a").forEach((item) => {
//   item.addEventListener("click", function (e) {
//     let stroke = [];
//     let current = item.parentNode;
//     while (current.className != "myMainClass") {
//       if (current.nodeName == "UL") {
//         stroke.push(current.previousElementSibling.textContent);
//       }
//       current = current.parentNode;

//       //Сохранение данных после перезагрузки страницы
//       localStorage.setItem(
//         "myText",
//         "Поиск по: " + stroke.reverse().join(" -> ") + " -> " + item.textContent
//       );
//       localStorage.getItem("myText");
//     }
//     document.querySelector(".newText").innerText =
//       "Поиск по: " + stroke.join(" -> ") + " -> " + item.textContent;
//     document.querySelector(".newText").style.display = "flex";
//   });
// });

// // Добавляем надпись при нажатии на ссылку с плюсом в другой структуре
// document.querySelectorAll(".menu__item > span > a").forEach((item) => {
//   item.addEventListener("click", function (e) {
//     let stroke = [];
//     let current = item.parentNode;
//     while (current.className != "myMainClass") {
//       if (current.nodeName == "UL") {
//         stroke.push(current.previousElementSibling.textContent);
//       }
//       current = current.parentNode;

//       //Сохранение данных после перезагрузки страницы
//       localStorage.setItem(
//         "myText",
//         "Поиск по: " + stroke.reverse().join(" -> ") + " -> " + item.textContent
//       );
//       localStorage.getItem("myText");
//     }
//     document.querySelector(".newText").innerText =
//       "Поиск по: " + stroke.join(" -> ") + " -> " + item.textContent;
//     document.querySelector(".newText").style.display = "flex";
//   });
// });

// // Вывод данных после перезагрузки страницы
// if (localStorage.getItem("myText") !== null) {
//   document.querySelector(".newText").innerText = localStorage.getItem("myText");
//   document.querySelector(".newText").style.display = "flex";
// }

// // Скрипт модального окна, появление надписи при нажатии на отдел внутри модального окна
// document.querySelectorAll(".department").forEach((item) => {
//   stroke = [];
//   item.addEventListener("click", (e) => {
//     document.querySelectorAll(".menu__item > li > a").forEach((subitem) => {
//       if (subitem.textContent === item.textContent) {
//         subitem.click();
//       }
//     });
//     document
//       .querySelectorAll(".menu__item > li > span > a")
//       .forEach((subitem) => {
//         if (subitem.textContent === item.textContent) {
//           subitem.click();
//         }
//       });
//     document.querySelectorAll(".menu__item > span > a").forEach((subitem) => {
//       if (subitem.textContent === item.textContent) {
//         subitem.click();
//       }
//     });
//   });
// });
