const createBtn = document.getElementById("createBtn")
const form = document.getElementById("createForm")
const saveBtn = document.getElementById("saveEvent")
const container = document.querySelector(".event-container")
const daysInput = document.getElementById("daysNumber")
const agendaContainer = document.getElementById("agendaContainer")

let currentEventId = null;
let allEvents = [];

// Load all events from API
async function loadEvents() {
    try {
        const token = localStorage.getItem("token");
        const res = await fetch("http://127.0.0.1:8000/api/admin/events", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!res.ok) {
            console.error("Failed to load events");
            return;
        }

        allEvents = await res.json();
        renderEvents(allEvents);
    } catch (err) {
        console.error("Error loading events:", err);
    }
}

// Render events list
function renderEvents(events) {
    container.innerHTML = "";

    events.forEach((event) => {
        const eventBox = document.createElement("div");
        eventBox.classList.add("event-box");
        eventBox.dataset.eventId = event.id;

        eventBox.innerHTML = `
            <h2>Event Overview</h2>
            <p><strong>Event Name:</strong> ${event.name || "Event " + event.id}</p>
            <p><strong>Max Participants:</strong> ${event.max_nbr_participant}</p>
            <p><strong>Registration Period:</strong> ${event.start_registration} to ${event.end_registration}</p>
            <p><strong>Shifts:</strong> ${event.shifts ? event.shifts.length : 0} créneaux</p>
            <div class="event-actions">
                <button class="edit-btn">Edit event</button>
                <button class="delete-btn">Delete event</button>
            </div>
        `;

        eventBox.querySelector(".edit-btn").addEventListener("click", () => {
            loadEventForEditing(event.id);
        });

        eventBox.querySelector(".delete-btn").addEventListener("click", () => {
            deleteEvent(event.id);
        });

        container.appendChild(eventBox);
    });
}

// Load event details for editing
async function loadEventForEditing(eventId) {
    try {
        const token = localStorage.getItem("token");
        const res = await fetch(`http://127.0.0.1:8000/api/admin/events/${eventId}`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!res.ok) {
            console.error("Failed to load event details");
            return;
        }

        const event = await res.json();
        currentEventId = event.id;

        // Populate form
        document.getElementById("eventName").value = event.name || "";
        document.getElementById("participants").value = event.max_nbr_participant;
        document.getElementById("staff").value = event.max_nbr_staff || 0;
        document.getElementById("mentor").value = event.max_nbr_mentor || 0;

        form.style.display = "block";
    } catch (err) {
        console.error("Error loading event:", err);
    }
}

// Function to add shift rows
function addShift(containerId) {
    const container = document.getElementById(containerId);
    const daysNumber = parseInt(document.getElementById("daysNumber").value) || 3;

    let dayOptions = '<option value="">Day</option>';
    for (let i = 1; i <= daysNumber; i++) {
        dayOptions += `<option value="day${i}">Day ${i}</option>`;
    }

    const row = document.createElement("div");
    row.className = "shift-row";
    row.innerHTML = `
        <select class="shift-day">
            ${dayOptions}
        </select>
        <select class="shift-time">
            <option value="">Shift</option>
            <option value="morning">Morning</option>
            <option value="afternoon">Afternoon</option>
            <option value="evening">Evening</option>
            <option value="full">Full day</option>
        </select>
        <button type="button" onclick="this.parentElement.remove()" 
            style="background:none;border:none;color:#e74c3c;font-size:18px;cursor:pointer;">×</button>
    `;
    container.appendChild(row);
}

// Delete event via API
async function deleteEvent(eventId) {
    if (!confirm("Êtes-vous sûr de vouloir supprimer cet événement?")) return;

    try {
        const token = localStorage.getItem("token");
        const res = await fetch(`http://127.0.0.1:8000/api/admin/events/${eventId}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!res.ok) {
            const error = await res.json();
            alert("Erreur: " + error.detail);
            return;
        }

        alert("Événement supprimé avec succès");
        loadEvents();
    } catch (err) {
        console.error("Error deleting event:", err);
        alert("Erreur lors de la suppression de l'événement");
    }
}

createBtn.addEventListener("click", () => {
    currentEventId = null;
    document.getElementById("eventName").value = "";
    document.getElementById("participants").value = 0;
    document.getElementById("staff").value = 0;
    document.getElementById("mentor").value = 0;
    form.style.display = "block";
});


daysInput.addEventListener("input", () => {

    agendaContainer.innerHTML = ""

    const days = daysInput.value

    for (let i = 1; i <= days; i++) {

        const block = document.createElement("div")

        block.classList.add("agenda-day")

        block.innerHTML = `

            <h4>Day ${i}</h4>

            <input
                type="text"
                class="dayTitle"
                placeholder="Title"
            >

            <textarea
                class="dayDesc"
                placeholder="Description"
            ></textarea>

        `

        agendaContainer.appendChild(block)

    }

})


saveBtn.addEventListener("click", async () => {

    const name = document.getElementById("eventName").value
    const participants = parseInt(document.getElementById("participants").value) || 0
    const staff = parseInt(document.getElementById("staff").value) || 0
    const mentor = parseInt(document.getElementById("mentor").value) || 0

    if (!name) {
        alert("Event name is required");
        return;
    }

    // Prepare event data
    const eventData = {
        name: name,
        max_nbr_participant: participants,
        max_nbr_staff: staff,
        max_nbr_mentor: mentor,
        start_registration: "2026-04-01T08:00:00",
        end_registration: "2026-04-10T23:59:00",
        shifts: [
            {
                day: "2026-04-14",
                start_time: "09:00:00",
                end_time: "12:00:00",
                shift_type: "STAFFING"
            },
            {
                day: "2026-04-14",
                start_time: "09:00:00",
                end_time: "12:00:00",
                shift_type: "MENTORING"
            }
        ]
    };

    try {
        const token = localStorage.getItem("token");
        const method = currentEventId ? "PUT" : "POST";
        const endpoint = currentEventId
            ? `http://127.0.0.1:8000/api/admin/events/${currentEventId}`
            : "http://127.0.0.1:8000/api/admin/events";

        const res = await fetch(endpoint, {
            method: method,
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(eventData)
        });

        if (!res.ok) {
            const error = await res.json();
            alert("Erreur: " + error.detail);
            return;
        }

        alert(currentEventId ? "Événement mis à jour avec succès" : "Événement créé avec succès");
        form.style.display = "none";
        currentEventId = null;
        loadEvents();
    } catch (err) {
        console.error("Error saving event:", err);
        alert("Erreur lors de la sauvegarde de l'événement");
    }

})

// Add cancel button handler
const cancelBtn = document.getElementById("cancelEvent");
if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
        form.style.display = "none";
        currentEventId = null;
    });
}

// Load events when page loads
document.addEventListener("DOMContentLoaded", () => {
    loadEvents();
});