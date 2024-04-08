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
