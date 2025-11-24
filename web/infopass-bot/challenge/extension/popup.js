document.addEventListener("DOMContentLoaded", async () => {
  const originListUl = document.getElementById("origin-list");

  const origins = await chrome.runtime.sendMessage({
    action: "getOrigins",
  });
  if (origins) {
    originListUl.innerHTML = "";
    for (const o of origins) {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.innerText = o;
      a.href = "#";
      li.appendChild(a);
      originListUl.appendChild(li);

      a.addEventListener("click", () => {
        chrome.tabs.create({ url: o, active: true });
      });
    }
  } else {
    originListUl.innerHTML = "<li>Error retreiving origins</li>";
  }
});
