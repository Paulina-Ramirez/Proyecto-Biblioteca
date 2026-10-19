if (getMe()) {
  location.href = "dashboard.html";
}

let mode = "login";

const authForm = $("#auth-form");
const loginTab = $("#login-tab");
const registerTab = $("#register-tab");
const authTitle = $("#auth-title");
const authDescription = $("#auth-description");
const submitButton = $("#submit-button");
const errorMessage = $("#error");

const nameField = $("#name-field");
const nameInput = $("#nombre");
const confirmField = $("#confirm-field");
const confirmInput = $("#confirm");
const roleField = $("#role-field");
const roleSelect = $("#rol");
const passwordInput = $("#password");

function setFieldVisibility(container, input, visible) {
  container.hidden = !visible;
  input.disabled = !visible;
  input.required = visible;
}

function drawMode() {
  const registering = mode === "register";

  authTitle.textContent = registering ? "Crear cuenta" : "Iniciar sesión";
  authDescription.textContent = registering
    ? "Completa tus datos para registrarte."
    : "Ingresa con tu correo registrado.";

  loginTab.classList.toggle("on", !registering);
  registerTab.classList.toggle("on", registering);
  loginTab.setAttribute("aria-selected", String(!registering));
  registerTab.setAttribute("aria-selected", String(registering));

  setFieldVisibility(nameField, nameInput, registering);
  setFieldVisibility(confirmField, confirmInput, registering);
  setFieldVisibility(roleField, roleSelect, registering);

  passwordInput.autocomplete = registering ? "new-password" : "current-password";
  submitButton.innerHTML = registering
    ? 'Crear cuenta <span aria-hidden="true">→</span>'
    : 'Entrar <span aria-hidden="true">→</span>';

  errorMessage.textContent = "";
}

loginTab.addEventListener("click", () => {
  mode = "login";
  drawMode();
});

registerTab.addEventListener("click", () => {
  mode = "register";
  drawMode();
});

authForm.addEventListener("submit", async event => {
  event.preventDefault();
  errorMessage.textContent = "";

  const formData = new FormData(authForm);
  const form = Object.fromEntries(formData);

  try {
    if (mode === "register") {
      if (form.password.length < 6) {
        throw new Error("La contraseña debe tener al menos 6 caracteres.");
      }

      if (form.password !== form.confirm) {
        throw new Error("Las contraseñas no coinciden.");
      }

      await api("/usuarios/", {
        method: "POST",
        body: {
          nombre: form.nombre.trim(),
          email: form.email,
          password: form.password,
          rol: form.rol
        }
      });

      mode = "login";
      drawMode();
      authForm.reset();
      toast("Cuenta creada. Ya puedes iniciar sesión.");
    } else {
      const user = await api("/usuarios/login", {
        method: "POST",
        body: {
          email: form.email,
          password: form.password
        }
      });

      localStorage.setItem("me", JSON.stringify(user));
      location.href = "dashboard.html";
    }
  } catch (error) {
    errorMessage.textContent = error.message || "No fue posible completar la operación.";
  }
});

// Deja el formulario inicial en modo de inicio de sesión.
drawMode();
