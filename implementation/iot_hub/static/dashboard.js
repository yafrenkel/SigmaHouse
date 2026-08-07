// Dashboard for the IoT hub.
// Polls /api/houses every second and rebuilds the table.
// Buttons inside the table call /api/houses/<uid>/... endpoints.

const REFRESH_MS = 1000;

async function refresh() {
  try {
    const resp = await fetch("/api/houses");
    const houses = await resp.json();
    render(houses);
  } catch (err) {
    console.error("refresh failed:", err);
  }
}

function render(houses) {
  const table = document.getElementById("houses");
  const empty = document.getElementById("empty");
  const tbody = table.querySelector("tbody");

  if (houses.length === 0) {
    table.hidden = true;
    empty.hidden = false;
    return;
  }
  empty.hidden = true;
  table.hidden = false;

  tbody.innerHTML = "";
  for (const h of houses) {
    tbody.appendChild(rowFor(h));
  }
}

function rowFor(h) {
  const tr = document.createElement("tr");
  tr.appendChild(cell(h.unique_id));
  tr.appendChild(cell(h.ip_address));
  tr.appendChild(statusCell(h));
  tr.appendChild(alarmCell(h));
  tr.appendChild(toggleCell(h, "led"));
  tr.appendChild(toggleCell(h, "fan"));
  tr.appendChild(toggleCell(h, "buzzer"));
  tr.appendChild(motionCell(h));
  tr.appendChild(msgCell(h));
  tr.appendChild(cell(h.last_seen));
  return tr;
}

function cell(text) {
  const td = document.createElement("td");
  td.textContent = text;
  return td;
}

function statusCell(h) {
  const td = cell(h.status);
  td.className = h.status === "Active" ? "green" : "red";
  return td;
}

function alarmCell(h) {
  const td = document.createElement("td");
  const btn = document.createElement("button");
  if (h.alarm_triggered) {
    td.className = "red";
    btn.textContent = "TRIGGERED (disarm)";
  } else if (h.alarm_armed) {
    td.className = "yellow";
    btn.textContent = "Armed (disarm)";
  } else {
    btn.textContent = "Disarmed (arm)";
  }
  btn.onclick = () => arm(h.unique_id, !h.alarm_armed);
  td.appendChild(btn);
  return td;
}

function toggleCell(h, device) {
  const td = document.createElement("td");
  const active = h.state[device].active;
  const btn = document.createElement("button");
  btn.textContent = active ? "ON" : "off";
  if (active) td.className = "green";
  btn.onclick = () => toggle(h.unique_id, device);
  td.appendChild(btn);
  return td;
}

function motionCell(h) {
  const detected = h.state.motion.detected;
  const td = cell(detected ? "Motion!" : "clear");
  if (detected) td.className = "red";
  return td;
}

function msgCell(h) {
  const td = document.createElement("td");
  const btn = document.createElement("button");
  btn.textContent = "Send";
  btn.onclick = () => sendMessage(h.unique_id);
  td.appendChild(btn);
  return td;
}

async function toggle(uid, device) {
  await fetch(`/api/houses/${uid}/toggle/${device}`, { method: "POST" });
  refresh();
}

async function arm(uid, armed) {
  await fetch(`/api/houses/${uid}/arm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ armed }),
  });
  refresh();
}

async function sendMessage(uid) {
  // prompt() is a modal, so it's safe from the every-second table redraw.
  const text = prompt("Message to send to " + uid + ":");
  if (!text) return;                 // Cancel or empty -> do nothing
  await fetch(`/api/houses/${uid}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ from: "dashboard", text }),
  });
  refresh();
}

refresh();
setInterval(refresh, REFRESH_MS);
