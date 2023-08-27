function fetchHouses() {
  const api_url = "/smarthouse/v1/houses"

  fetch(api_url)
    .then(response => response.json())
    .then(data => {
      const tableBody = document.getElementById("house_container");

      tableBody.innerHTML = "";

      data.forEach(house => {
        const row = document.createElement("tr");
        row.setAttribute("id", house.unique_id)

        const unique_id = document.createElement("td");
        unique_id.textContent = house.unique_id;
        row.appendChild(unique_id);

        const ip_address = document.createElement("td");
        ip_address.textContent = house.ip_address;
        row.appendChild(ip_address);

        const status = document.createElement("td");
        status.textContent = house.status;
        status.className = house.status == "Lost" ? "status red" : "status green"
        row.appendChild(status);

        const state_alarm = document.createElement("td");
        if (house.state.alarm.armed) {
          if (house.state.alarm.triggered) {
            state_alarm.textContent = "Triggered";
            state_alarm.className = "status red";
          } else {
            if (house.state.alarm.mode == 1) {
              state_alarm.textContent = "Armed [Local]";
            } else if (house.state.alarm.mode == 2) {
              state_alarm.textContent = "Armed [Global]";
            } else if (house.state.alarm.mode == 3) {
              state_alarm.textContent = "Armed [Sensor]";
            }
            state_alarm.className = "status yellow";
          }
        } else {
          state_alarm.textContent = "Disarmed";
          state_alarm.className = "status green";
        };
        row.appendChild(state_alarm);

        const state_buzzer = document.createElement("td");
        state_buzzer.textContent = house.state.buzzer.active ? "On" : "Off";
        state_buzzer.className = "status";
        state_buzzer.setAttribute("house_device_name", "buzzer");
        state_buzzer.addEventListener("click", toggleDevice);
        row.appendChild(state_buzzer);

        const state_fan = document.createElement("td");
        state_fan.textContent = house.state.fan.active ? "On" : "Off";
        state_fan.className = "status";
        state_fan.setAttribute("house_device_name", "fan");
        state_fan.addEventListener("click", toggleDevice);
        row.appendChild(state_fan);

        const state_led = document.createElement("td");
        state_led.textContent = house.state.led.active ? "On" : "Off";
        state_led.className = "status";
        state_led.setAttribute("house_device_name", "led");
        state_led.addEventListener("click", toggleDevice);
        row.appendChild(state_led);

        const state_motion = document.createElement("td");
        state_motion.textContent = house.state.motion.motion_detected ? "Yes" : "No";
        state_motion.className = house.state.motion.motion_detected ? "status red" : "status green";
        row.appendChild(state_motion);

        const timestamp_keepalive = document.createElement("td");
        timestamp_keepalive.textContent = house.timestamp_keepalive;
        row.appendChild(timestamp_keepalive);

        const timestamp_created = document.createElement("td");
        timestamp_created.textContent = house.timestamp_created;
        row.appendChild(timestamp_created);

        const timestamp_modified = document.createElement("td");
        timestamp_modified.textContent = house.timestamp_modified;
        row.appendChild(timestamp_modified);

        const timestamp_deleted = document.createElement("td");
        timestamp_deleted.textContent = house.timestamp_deleted;
        row.appendChild(timestamp_deleted);

        const state_wall_msg = document.createElement("td");
        state_wall_msg.textContent = house.state.wall_msg;
        row.appendChild(state_wall_msg);

        tableBody.appendChild(row);
      });
    })
    .catch(error => {
      console.error("Error:", error);
    });
}

function toggleDevice() {
  const unique_id = this.closest("tr").getAttribute("id");
  const device = this.getAttribute("house_device_name");
  const api_url = "/smarthouse/v1/houses/" + unique_id + "/toggle_device/" + device;

  fetch(api_url, {
    "method": "PUT",
  })
}

// function toggleBuzzer() {
//   const unique_id = this.closest("tr").getAttribute("id");
//   const api_url = "/smarthouse/v1/houses/" + unique_id + "/toggle_device/buzzer";

//   fetch(api_url, {
//     "method": "PUT",
//   })
// }

// function toggleFan() {
//   const unique_id = this.closest("tr").getAttribute("id");
//   const api_url = "/smarthouse/v1/houses/" + unique_id + "/toggle_device/fan";

//   fetch(api_url, {
//     "method": "PUT",
//   })
// }

// function toggleLed() {
//   const unique_id = this.closest("tr").getAttribute("id");
//   const api_url = "/smarthouse/v1/houses/" + unique_id + "/toggle_device/led";

//   fetch(api_url, {
//     "method": "PUT",
//   })
// }

