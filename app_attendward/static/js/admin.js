// Script para cambiar el texto y el estilo del botón cuando se hace clic en él
document
  .getElementById("entrenar_form")
  .addEventListener("submit", function () {
    let entrenarButton = document.getElementById("entrenar_button");
    entrenarButton.innerText = "Entrenando...";
    entrenarButton.disabled = true;
    entrenarButton.classList.add("btn-secondary");
    entrenarButton.classList.remove("btn-primary");
  });

// Script para cambiar el texto y el estilo del botón cuando se hace clic en él
document
  .getElementById("entrenar_form")
  .addEventListener("submit", function () {
    let entrenarButton = document.getElementById("entrenar_button");
    entrenarButton.innerText = "Entrenando...";
    entrenarButton.disabled = true;
    entrenarButton.classList.add("btn-secondary");
    entrenarButton.classList.remove("btn-primary");

    // Mostrar el contenedor de carga
    document.getElementById("contenedor").classList.remove("invisible");
  });
