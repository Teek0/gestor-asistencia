document.addEventListener("DOMContentLoaded", function () {
    // Agregar escuchador de eventos para el clic del botón "Agregar"
    document.getElementById("agregarAsistenciaBtn").addEventListener("click", function (event) {
      // Evitar que el formulario se envíe normalmente
      event.preventDefault();
  
      // Obtener el valor ingresado en el campo de entrada
      const rutInput = document.getElementById("rutInput").value.trim();
  
      // Verificar si el valor no está vacío
      if (rutInput !== "") {
        // Enviar el valor al servidor a través de una solicitud AJAX
        fetch("/agregar_manualmente", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ rut: rutInput }),
        })
        .then(handleResponse)
        .catch(handleError);
  
        // Borrar el campo de entrada después de agregar el valor
        document.getElementById("rutInput").value = "";
      } else {
        // Mostrar mensaje de alerta si el campo está vacío
        showAlert("Por favor ingresa un valor válido antes de agregarlo.");
      }
    });
  
    // Agregar escuchadores de eventos para los botones de quitar asistencia
    const quitarAsistenciaBtns = document.querySelectorAll(".quitar-asistencia-btn");
    quitarAsistenciaBtns.forEach((btn) => {
      btn.addEventListener("click", function () {
        // Obtener el rut del alumno correspondiente
        const rutAlumno = btn.parentNode.parentNode.querySelector(".rut-cell").textContent.trim();
  
        // Realizar la solicitud AJAX al servidor Flask
        fetch("/quitar_asistencia", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ rut_estudiante: rutAlumno }),
        })
        .then(handleResponse)
        .catch(handleError);
      });
    });
  
    // Función para manejar la respuesta de la solicitud AJAX
    function handleResponse(response) {
      if (response.ok) {
        // La operación se realizó correctamente, actualizar la tabla si es necesario
        updateTable();
      } else {
        // Mostrar mensaje de alerta en caso de error
        showAlert("Error: El Rut proporcionado no está registrado");
        console.error("Error al realizar la operación.");
      }
    }
  
    // Función para manejar errores en la solicitud AJAX
    function handleError(error) {
      // Mostrar mensaje de alerta en caso de error
      showAlert("Error: No se pudo enviar la solicitud al servidor");
      console.error("Error al enviar la solicitud:", error);
    }
  
    // Función para mostrar un mensaje de alerta
    function showAlert(message) {
      alert(message);
    }
  
    // Función para actualizar la tabla con los ruts recibidos del backend
    function updateTable() {
      // Realizar una solicitud al endpoint /listaDetectados
      fetch("/listaDetectados")
        .then((response) => response.json())
        .then((data) => {
          const ruts = data.arreglo; // Obtener los ruts del arreglo recibido del backend
          console.log(ruts); // Imprimir la lista de ruts recibidos del backend
  
          const tableRows = document.querySelectorAll("#tabla-alumnos tr");
  
          // Iterar sobre los elementos de la tabla y cambiar el color de los ruts coincidentes
          tableRows.forEach((row) => {
            const rutCell = row.querySelector(".rut-cell");
            if (rutCell && ruts.includes(rutCell.textContent)) {
              row.style.backgroundColor = "yellow";
            } else {
              row.style.backgroundColor = "white";
            }
          });
        })
        .catch((error) => console.error("Error al actualizar la tabla:", error));
    }
  
    // Llamar a la función updateTable() cada segundo
    setInterval(updateTable, 1000);
  
    // Agregar escuchador de eventos para el clic del botón "Generar documento"
    document.getElementById("btn").addEventListener("click", function (event) {
      // Evitar que el formulario se envíe normalmente
      event.preventDefault();
  
      // Realizar una solicitud AJAX al servidor para generar el documento Excel
      fetch("/generar_documento_excel", {
        method: "POST",
      })
      .then((response) => {
        if (response.ok) {
          // Descargar el archivo Excel generado
          return response.blob();
        } else {
          console.error("Error al generar el documento Excel.");
        }
      })
      .then((blob) => {
        // Crear un enlace temporal para descargar el archivo
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = "alumnos_detectados.xlsx";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      })
      .catch((error) => console.error("Error al generar el documento Excel:", error));
    });
  });
  