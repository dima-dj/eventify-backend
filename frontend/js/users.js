const usersList = document.getElementById("usersList");
const userDetailsBox = document.getElementById("userDetails");
const userRoleFilter = document.getElementById("userRoleFilter");

let allUsers = [];

// Load users from API
async function loadUsers() {
    try {
        const token = localStorage.getItem("token");
        const res = await fetch("http://127.0.0.1:8000/api/users", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!res.ok) {
            console.error("Failed to load users");
            usersList.innerHTML = "<p>Error loading users</p>";
            return;
        }

        allUsers = await res.json();
        renderUsers(allUsers);
    } catch (err) {
        console.error("Error loading users:", err);
        usersList.innerHTML = "<p>Error loading users</p>";
    }
}

function renderUsers(data) {
    usersList.innerHTML = "";

    if (data.length === 0) {
        usersList.innerHTML = "<p>No users yet.</p>";
        return;
    }

    const header = document.createElement("div");
    header.className = "users-header";
    header.innerHTML = `
        <span>Last name</span>
        <span>First name</span>
        <span>Role</span>
        <span></span>
    `;
    usersList.appendChild(header);

    data.forEach((user) => {
        const row = document.createElement("div");
        row.className = "user-row";
        row.innerHTML = `
            <span>${user.last_name || "-"}</span>
            <span>${user.first_name || "-"}</span>
            <span>${user.role || "-"}</span>
            <button class="details-link">View details</button>
        `;
        row.querySelector(".details-link").addEventListener("click", () => {
            showUserDetails(user);
        });
        usersList.appendChild(row);
    });
}

function buildRoleSpecificDetails(user) {
    if (user.role === "STAFF") {
        return `
            <p>Preferred role</p>
            <p>${user.preferred_role || "-"}</p>
            <p>Organized before</p>
            <p>${user.organized_before || "-"}</p>
            <p>Availability</p>
            <p>${user.availability || "-"}</p>
        `;
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
        `;
    }

    // participant
    return `
        <p>Team name</p>
        <p>${user.team || "-"}</p>
        <p>Main skills</p>
        <p>${user.main_skills || "-"}</p>
        <p>Skill level</p>
        <p>${user.skill_level || "-"}</p>
    `;
}

function showUserDetails(user) {
    userDetailsBox.style.display = "block";
    userDetailsBox.innerHTML = `
        <h3>User details</h3>
        <div class="details-grid">
            <p>First Name</p>
            <p>${user.first_name || "-"}</p>
            <p>Last Name</p>
            <p>${user.last_name || "-"}</p>
            <p>Email</p>
            <p>${user.email || "-"}</p>
            <p>Discord username</p>
            <p>${user.discord_username || "-"}</p>
            <p>University</p>
            <p>${user.university || "-"}</p>
            <p>Field of study</p>
            <p>${user.field_of_study || "-"}</p>
            <p>Role</p>
            <p>${user.role || "-"}</p>
            ${buildRoleSpecificDetails(user)}
        </div>
        <div class="details-actions">
            <button class="approve-btn">Approve</button>
            <button class="reject-btn">Reject</button>
        </div>
    `;
}

userRoleFilter.addEventListener("change", () => {
    const role = userRoleFilter.value;
    if (role === "all") {
        renderUsers(allUsers);
    } else {
        renderUsers(allUsers.filter((u) => u.role.toUpperCase() === role.toUpperCase()));
    }
});

document.addEventListener("click", (e) => {
    if (
        userDetailsBox.style.display === "block" &&
        !userDetailsBox.contains(e.target) &&
        !e.target.classList.contains("details-link")
    ) {
        userDetailsBox.style.display = "none";
    }
});

// Load users when page loads
document.addEventListener("DOMContentLoaded", () => {
    loadUsers();
});

