const menuBtn = document.getElementById("menuBtn");
const sidebar = document.getElementById("sidebar");

menuBtn.addEventListener("click", () => {
    sidebar.classList.toggle("active");
});

// Load current admin information when page loads
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "login.html";
            return;
        }

        // Call GET /api/auth/me to verify token and get admin info
        const res = await fetch("http://127.0.0.1:8000/api/auth/me", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!res.ok) {
            console.warn("Token invalid - redirecting to login");
            localStorage.removeItem("token");
            window.location.href = "login.html";
            return;
        }

        const adminData = await res.json();
        console.log("Admin logged in:", adminData.email, "Role:", adminData.role);

        // Display admin info if element exists
        const adminInfoElement = document.getElementById("adminInfo");
        if (adminInfoElement) {
            adminInfoElement.textContent = `Logged in as: ${adminData.email} (${adminData.role})`;
        }
    } catch (err) {
        console.error("Error loading admin info:", err);
        window.location.href = "login.html";
    }

    // Set active tab based on current page
    const currentUrl = window.location.href;
    const currentPage = currentUrl.split('/').pop().split('?')[0];
    const links = document.querySelectorAll('.links-ul li a');

    links.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href && href === currentPage) {
            link.classList.add('active');
        }
    });
});

// Load all admins (Super Admin only)
async function loadAllAdmins() {
    try {
        const token = localStorage.getItem("token");
        const res = await fetch("http://127.0.0.1:8000/api/admin/admins", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!res.ok) {
            console.error("Failed to load admins - you may not have super admin access");
            return [];
        }

        const admins = await res.json();
        console.log("Admins loaded:", admins);
        return admins;
    } catch (err) {
        console.error("Error loading admins:", err);
        return [];
    }
}

// Create new admin (Super Admin only)
async function createNewAdmin(email, password, role = "ADMIN") {
    try {
        const token = localStorage.getItem("token");
        const res = await fetch("http://127.0.0.1:8000/api/admin/admins", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password,
                role: role
            })
        });

        if (!res.ok) {
            const error = await res.json();
            console.error("Failed to create admin:", error);
            return null;
        }

        const newAdmin = await res.json();
        console.log("Admin created:", newAdmin);
        return newAdmin;
    } catch (err) {
        console.error("Error creating admin:", err);
        return null;
    }
}

// Delete admin (Super Admin only)
async function deleteAdmin(adminId) {
    try {
        const token = localStorage.getItem("token");
        const res = await fetch(`http://127.0.0.1:8000/api/admin/admins/${adminId}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!res.ok) {
            const error = await res.json();
            console.error("Failed to delete admin:", error);
            return false;
        }

        console.log("Admin deleted successfully");
        return true;
    } catch (err) {
        console.error("Error deleting admin:", err);
        return false;
    }
}