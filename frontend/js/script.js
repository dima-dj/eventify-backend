
// Countdown

function startCountdown() {

    const eventDate = new Date("2026-03-10T00:00:00").getTime();

    const timer = setInterval(() => {

        const now = new Date().getTime();
        const distance = eventDate - now;

        if (distance < 0) {
            clearInterval(timer);
            return;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        document.getElementById("days").innerText = String(days).padStart(2, "0");
        document.getElementById("hours").innerText = String(hours).padStart(2, "0");
        document.getElementById("minutes").innerText = String(minutes).padStart(2, "0");
        document.getElementById("seconds").innerText = String(seconds).padStart(2, "0");

    }, 1000);

}


// Security / Sanitization
function sanitizeString(value, { maxLen = 300 } = {}) {

    if (!value) return "";

    let s = String(value);

    try {
        s = s.normalize("NFKC");
    } catch (e) { }

    s = s.trim();
    s = s.replace(/[\u0000-\u001F\u007F]/g, "");
    s = s.replace(/[<>]/g, "");

    if (s.length > maxLen) s = s.slice(0, maxLen);

    return s;
}

function sanitizeEmail(value) {
    return sanitizeString(value, { maxLen: 200 }).toLowerCase();
}

function sanitizePhone(value) {
    return sanitizeString(value, { maxLen: 20 }).replace(/[^0-9+\-() ]/g, "");
}


// MAIN SCRIPT
document.addEventListener("DOMContentLoaded", function () {

    startCountdown();

    // Check registration form status
    async function checkFormStatus() {
        try {
            const res = await fetch("http://127.0.0.1:8000/api/registration/form-status");
            const data = await res.json();

            if (data.status !== "open") {
                document.querySelector(".registration-form").innerHTML = `
                <div style="padding: 20px; text-align: center; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px;">
                    <h2>${data.status === "not_open" ? "Form Not Open Yet" : "Registration Closed"}</h2>
                    <p>${data.message}</p>
                </div>
            `;
            }
        } catch (err) {
            console.error("Error checking form status:", err);
        }
    }

    checkFormStatus();

    // Get active event ID for shifts
    getActiveEventId();

    const roleSelect = document.getElementById("roleSelect");
    const discordInput = document.getElementById("discordUsername");

    const form1 = document.getElementById("form1");
    const form2 = document.getElementById("form2");
    const form3 = document.getElementById("form3");
    const form4 = document.getElementById("form4");

    const final = document.getElementById("final");
    const otpForm = document.getElementById("otpForm");

    const steps = document.querySelectorAll(".step");

    let currentRole = "participant";
    let registrationPayload = null;
    let currentEventId = 1; // TODO: Get this from API or context

    // Get current active event ID
    async function getActiveEventId() {
        try {
            const res = await fetch("http://127.0.0.1:8000/api/registration/form-status");
            const data = await res.json();

            if (data.status === "open") {
                // Fetch events and get the active one
                const token = localStorage.getItem("token");
                if (token) {
                    const eventsRes = await fetch("http://127.0.0.1:8000/api/admin/events", {
                        method: "GET",
                        headers: {
                            "Authorization": `Bearer ${token}`,
                            "Content-Type": "application/json"
                        }
                    });

                    if (eventsRes.ok) {
                        const events = await eventsRes.json();
                        if (events.length > 0) {
                            currentEventId = events[0].id;
                        }
                    }
                }
            }
        } catch (err) {
            console.error("Error getting active event ID:", err);
        }
    }

    // Load shifts based on role (STAFF or MENTOR)
    async function loadShiftsForRole(role, eventId) {
        try {
            const endpoint = role === "staff"
                ? `/api/events/${eventId}/shifts/staff`
                : role === "mentor"
                    ? `/api/events/${eventId}/shifts/mentors`
                    : null;

            if (!endpoint) return;

            const res = await fetch("http://127.0.0.1:8000" + endpoint);

            if (!res.ok) {
                console.error("Failed to load shifts for role:", role);
                return;
            }

            const shifts = await res.json();
            console.log(`Shifts for ${role}:`, shifts);

            // You can use this data to populate shift selection in the form
            // For example: displayShiftsInForm(shifts);

        } catch (err) {
            console.error("Error loading shifts:", err);
        }
    }

    // Helpers
    function hideAll() {
        [form1, form2, form3, form4, final, otpForm].forEach(f => f.style.display = "none");
    }

    function show(el) {
        el.style.display = "block";
    }

    function setStep(index) {
        steps.forEach((s, i) => s.classList.toggle("active", i <= index));
    }


    // Discord Check Backend
    discordInput.addEventListener("blur", async function () {

        const username = sanitizeString(discordInput.value);

        if (!username) return;

        try {

            const res = await fetch("http://127.0.0.1:8000/api/registration/check-discord/" + username);

            const data = await res.json();

            roleSelect.innerHTML = "";

            data.roles.forEach(role => {

                const option = document.createElement("option");

                option.value = role.toLowerCase();
                option.textContent = role;

                roleSelect.appendChild(option);

            });

        } catch (err) {

            console.error("Discord check error", err);

        }

    });


    // Load shifts when role is selected
    roleSelect.addEventListener("change", async function () {
        const selectedRole = roleSelect.value;
        if (selectedRole === "staff" || selectedRole === "mentor") {
            await loadShiftsForRole(selectedRole, currentEventId);
        }
    });

    // Validation
    function validateForm(form) {

        let valid = true;

        form.querySelectorAll(".error-msg").forEach(e => e.remove());
        form.querySelectorAll(".input-error").forEach(e => e.classList.remove("input-error"));

        const fields = form.querySelectorAll("input[required],select[required]");

        fields.forEach(field => {

            if (!field.value.trim()) {

                field.classList.add("input-error");

                const err = document.createElement("span");
                err.className = "error-msg";
                err.textContent = "This field is required";

                field.insertAdjacentElement("afterend", err);

                valid = false;

            }

        });

        return valid;

    }


    // Step Navigation
    document.getElementById("next1").onclick = function () {

        if (!validateForm(form1)) return;

        currentRole = roleSelect.value;

        hideAll();

        if (currentRole === "participant") show(form2);
        else if (currentRole === "mentor") show(form3);
        else show(form4);

        setStep(1);

    };


    // Back Buttons
    ["back2", "back3", "back4"].forEach(id => {

        document.getElementById(id).onclick = function () {

            hideAll();
            show(form1);
            setStep(0);

        };

    });


    // Step2 → Final
    ["next2", "next3", "next4"].forEach(id => {

        document.getElementById(id).onclick = function () {

            const form = this.closest("form");

            if (!validateForm(form)) return;

            hideAll();
            show(final);
            setStep(2);

        };

    });


    // Submit Registration
    document.getElementById("submitFinal").onclick = async function () {

        const payload = {

            first_name: sanitizeString(document.getElementById("firstName").value),
            last_name: sanitizeString(document.getElementById("lastName").value),
            email: sanitizeEmail(document.getElementById("emailInput").value),
            phone_number: sanitizePhone(document.getElementById("phone").value),
            discord_username: sanitizeString(document.getElementById("discordUsername").value),
            university: sanitizeString(document.getElementById("university").value),
            field_of_study: sanitizeString(document.getElementById("fieldOfStudy").value),
            role: roleSelect.value.toUpperCase()

        };

        registrationPayload = payload;

        try {

            const res = await fetch("http://127.0.0.1:8000/api/registration/submit", {

                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: payload.email
                })

            });

            const data = await res.json();

            if (!res.ok) throw new Error(data.detail);

            alert("OTP sent to your email");

            hideAll();
            show(otpForm);

        } catch (err) {

            console.error(err);
            alert("Error sending OTP");

        }

    };


    // OTP Verify
    document.getElementById("verifyOtp").onclick = async function () {

        const otp = [...document.querySelectorAll(".otp-input")].map(i => i.value).join("");

        try {

            const res = await fetch("http://127.0.0.1:8000/api/registration/verify-otp", {

                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: registrationPayload.email,
                    otp: enteredOtp,
                    form: registrationPayload

                })

            });

            const data = await res.json();

            if (!res.ok) throw new Error(data.detail);

            alert("Registration successful ✔");

            window.location.reload();

        } catch (err) {

            console.error(err);
            alert("Invalid OTP");

        }

    };


    // OTP Auto Focus
    const otpInputs = document.querySelectorAll(".otp-input");

    otpInputs.forEach((input, index) => {

        input.addEventListener("input", function () {

            this.value = this.value.replace(/[^0-9]/g, "");

            if (this.value && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }

        });

        input.addEventListener("keydown", function (e) {

            if (e.key === "Backspace" && !this.value && index > 0) {
                otpInputs[index - 1].focus();
            }

        });

    });

});