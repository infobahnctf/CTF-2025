function getOrigin() {
  return window.location.origin;
}
const loginInput = document.querySelector(
  "input[type='email'], input[name='username'], input[type='text']"
);
const passwordInput = document.querySelector("input[type='password']");

function addSaveButton() {
  const form = document.querySelector("form");
  if (!form || !loginInput || !passwordInput) return;

  const btn = document.createElement("button");
  btn.innerText = "Save to Infopass";
  btn.type = "button";
  btn.style.margin = "10px";
  btn.id = "infopass-save";
  form.appendChild(btn);

  btn.addEventListener("click", () => {
    chrome.runtime.sendMessage(
      {
        action: "saveCredential",
        origin: getOrigin(),
        login: loginInput.value,
        password: passwordInput.value,
      },
      (res) => {
        btn.innerHTML = res.success ? "Saved!" : "Failed to save";
      }
    );
  });
}

addSaveButton();

if (loginInput && passwordInput) {
  chrome.runtime.sendMessage(
    { action: "getCredential", origin: getOrigin() },
    (cred) => {
      if (cred) {
        loginInput.value = cred.login;
        passwordInput.value = cred.password;
      }
    }
  );
}