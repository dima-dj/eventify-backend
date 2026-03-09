const list = document.querySelector(".registration-list")
const detailsBox = document.getElementById("userDetails")
const roleFilter = document.getElementById("roleFilter")

let registrations = []

// =============================
// LOAD DATA FROM BACKEND
// =============================
async function loadRegistrations() {

    try {

        const res = await fetch("http://127.0.0.1:8000/api/users")

        registrations = await res.json()

        renderRegistrations(registrations)

    } catch (err) {

        console.error("Error loading registrations:", err)

    }

}

// =============================
// RENDER REGISTRATIONS
// =============================
function renderRegistrations(data) {

    list.innerHTML = ""

    data.forEach((user) => {

        const card = document.createElement("div")

        card.classList.add("registration-card")

        card.innerHTML = `
            <div class="reg-info">
                <p><strong>Registration date</strong></p>
                <p>${user.registration_date || "-"}</p>
            </div>

            <div class="reg-info">
                <p><strong>User</strong></p>
                <p>${user.first_name} ${user.last_name}</p>
            </div>

            <div class="reg-actions">
                <button class="approve-btn">Approve</button>
                <button class="reject-btn">Reject</button>
                <button class="details-btn">View details</button>
            </div>
        `

        list.appendChild(card)

        card.querySelector(".details-btn").addEventListener("click", () => {
            showDetails(user)
        })

        card.querySelector(".approve-btn").addEventListener("click", () => {
            card.style.borderLeft = "5px solid green"
        })

        card.querySelector(".reject-btn").addEventListener("click", () => {
            card.style.borderLeft = "5px solid red"
        })

    })

}

// ROLE DETAILS
function buildRoleDetails(user) {

    if (user.role === "STAFF") {

        return `
            <p>Preferred role</p>
            <p>${user.preferred_role || "-"}</p>

            <p>Organized before</p>
            <p>${user.organized_before || "-"}</p>

            <p>Availability</p>
            <p>${user.availability || "-"}</p>
        `
    }

    if (user.role === "MENTOR") {

        return `
            <p>Years of experience</p>
            <p>${user.years_of_experience || "-"}</p>

            <p>Expertise area</p>
            <p>${user.area_of_expertise || "-"}</p>

            <p>Mentored before</p>
            <p>${user.mentored_before || "-"}</p>

            <p>Availability</p>
            <p>${user.availability || "-"}</p>
        `
    }

    // PARTICIPANT
    return `
        <p>Team name</p>
        <p>${user.team || "-"}</p>

        <p>Main skills</p>
        <p>${user.main_skills || "-"}</p>

        <p>Skill level</p>
        <p>${user.skill_level || "-"}</p>
    `
}


// SHOW USER DETAILS
function showDetails(user) {

    detailsBox.style.display = "block"

    detailsBox.innerHTML = `

        <h3>User details</h3>

        <div class="details-grid">

            <p>First Name</p>
            <p>${user.first_name}</p>

            <p>Last Name</p>
            <p>${user.last_name}</p>

            <p>Email</p>
            <p>${user.email}</p>

            <p>Discord username</p>
            <p>${user.discord_username}</p>

            <p>University</p>
            <p>${user.university || "-"}</p>

            <p>Field of study</p>
            <p>${user.field_of_study}</p>

            <p>Role</p>
            <p>${user.role}</p>

            ${buildRoleDetails(user)}

        </div>

        <div class="details-actions">

            <button class="approve-btn">Approve</button>
            <button class="reject-btn">Reject</button>

        </div>

    `
}

detailsBox.querySelector(".approve-btn").addEventListener("click", () => {
    detailsBox.style.borderLeft = "5px solid green";
});

detailsBox.querySelector(".reject-btn").addEventListener("click", () => {
    detailsBox.style.borderLeft = "5px solid red";
});


roleFilter.addEventListener("change", () => {

    const role = roleFilter.value

    if (role === "all") {

        renderRegistrations(registrations)

    } else {

        const filtered = registrations.filter(r => r.role.toLowerCase() === role)

        renderRegistrations(filtered)

    }

})
document.addEventListener("click", (e) => {

    if (!detailsBox.contains(e.target) && !e.target.classList.contains("details-btn")) {

        detailsBox.style.display = "none"

    }

})

loadRegistrations()