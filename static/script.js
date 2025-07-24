function getUsers() {
  fetch("/users").then(res => res.json()).then(data => {
    const ul = document.getElementById("userList");
    ul.innerHTML = "";
    data.forEach(u => {
      const li = document.createElement("li");
      li.textContent = `${u.id}: ${u.name} (${u.email})`;
      ul.appendChild(li);
    });
  });
}

function createUser() {
  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  fetch("/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email })
  })
  .then(res => res.json())
  .then(d => alert(d.message));
}
