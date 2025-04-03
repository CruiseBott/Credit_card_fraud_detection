const baseURL = "/api/auth"; // Adjust if your API path differs

// ✅ Function to Get the Logged-in Username
function getLoggedInUsername() {
    console.log("🔍 Checking localStorage for username...");
    const username = localStorage.getItem("username");
    console.log("📌 Retrieved username:", username);

    return username || "Guest"; // Fallback to 'Guest'
}

// ✅ Function to Display Username in user.html
function displayUsername() {
    console.log("🚀 Running displayUsername()...");

    const usernameSpan = document.getElementById("username");
    console.log("✅ Found username span:", usernameSpan);

    const username = getLoggedInUsername();

    if (username === "Guest") {
        console.warn("⚠️ No user logged in! Redirecting to login page...");
        window.location.href = "/login"; // Redirect if no user is logged in
    } else {
        console.log("🖊️ Updating username display to:", username);
        usernameSpan.textContent = username; // Update UI with username
    }
}

// ✅ Admin Security Check
function checkAdminAccess() {
    const role = localStorage.getItem("user_role");
    if (!role) {
        console.log("No role found, redirecting to login.");
        window.location.href = "/login";
        return;
    }
    if (role !== "admin" && window.location.pathname.includes("/admin")) {
        alert("⚠️ Unauthorized access!");
        window.location.href = "/user";
    }
}

// ✅ User Authentication (Login/Register)
async function handleAuth(endpoint) {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    if (!username || !password) {
        alert("⚠️ Please enter all fields.");
        return;
    }

    try {
        const response = await fetch(`${baseURL}/${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Something went wrong!");

        alert(data.message || "Success");

        if (endpoint === "login") {
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("user_role", data.role);
            localStorage.setItem("username", username);

            // Redirect based on role
            window.location.href = data.role === "admin" ? "/admin" : "/user";
        } else {
            window.location.href = "/login"; // Redirect to login after registering
        }
    } catch (error) {
        alert("❌ Error: " + error.message);
        console.error("Error:", error);
    }
}

// ✅ Logout Function
function logout() {
    localStorage.clear();
    alert("✅ Logged out successfully!");
    window.location.href = "/login";
}

// ✅ Secure API Calls with JWT Token
async function fetchWithAuth(endpoint, method = "GET", body = null) {
    const token = localStorage.getItem("token");
    if (!token) {
        console.warn("No token found, redirecting to login.");
        if (!window.location.pathname.includes("/login")) {
            window.location.href = "/login";
        }
        return;
    }

    try {
        const response = await fetch(endpoint, {
            method,
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: body ? JSON.stringify(body) : null,
        });

        if (response.status === 401) {
            alert("⚠️ Session expired, please login again.");
            localStorage.clear();
            window.location.href = "/login";
            return;
        }

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Something went wrong!");
        return data;
    } catch (error) {
        console.error("❌ Error in fetchWithAuth:", error);
    }
}


// ✅ Load Admin Panel Data (Users & Fraud Transactions)
async function loadAdminPanel() {
    checkAdminAccess(); // Ensure only admins can load this

    try {
        const users = await fetchWithAuth("/api/admin/users");
        const userTable = document.getElementById("userTable");
        userTable.innerHTML = ""; // Clear table before populating

        if (users && users.length > 0) {
            users.forEach(user => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${user.username}</td>
                    <td>${user.role}</td>
                    <td>
                        <select onchange="changeUserRole('${user.username}', this.value)">
                            <option value="user" ${user.role === "user" ? "selected" : ""}>User</option>
                            <option value="admin" ${user.role === "admin" ? "selected" : ""}>Admin</option>
                        </select>
                    </td>
                `;
                userTable.appendChild(row);
            });
        } else {
            userTable.innerHTML = "<tr><td colspan='3'>No users found.</td></tr>";
        }

        loadFraudTransactions(); // Load fraud transactions separately
    } catch (error) {
        console.error("Error loading admin panel:", error);
        alert("❌ Failed to load admin panel.");
    }
}

// ✅ Update User Role Function
async function changeUserRole(username, newRole) {
    if (!confirm(`Are you sure you want to change ${username}'s role to ${newRole}?`)) return;

    try {
        const response = await fetchWithAuth(`/api/admin/update-role`, "POST", {
            username,
            role: newRole,
        });

        alert(response.message || "Role updated successfully!");
        loadAdminPanel(); // Refresh user list

    } catch (error) {
        console.error("Error updating role:", error);
        alert("❌ Failed to update role.");
    }
}

// ✅ Load Fraud Transactions
// ✅ Load Fraud Transactions and Populate Table
function loadFraudTransactions() {
    fetch('/api/admin/fraud-transactions', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token')  // Ensure token is passed
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("🚀 Received Transactions:", data);  // Debugging

        const transactionTable = document.getElementById("transactionTable");
        transactionTable.innerHTML = ""; // Clear existing data before inserting new ones

        data.forEach((transaction, index) => {
            const fraudProbability = transaction.fraud_probability !== undefined 
                ? transaction.fraud_probability.toFixed(2) 
                : "N/A";

            // Create row element
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${transaction.transaction.amt}</td>
                <td>${transaction.transaction.category}</td>
                <td>${transaction.transaction.merchant}</td>
                <td>${fraudProbability}</td>
                <td><button onclick="showTransactionDetails(${index})">View</button></td>
            `;

            transactionTable.appendChild(row);
        });

        // Store transactions globally for click events
        window.transactions = data;
    })
    .catch(error => console.error("❌ Error loading fraud transactions:", error));
}
function checkUserRole() {
    const role = localStorage.getItem("user_role");

    if (!role) {
        alert("⚠️ No user role found. Redirecting to login.");
        window.location.href = "/login";
        return;
    }

    if (role === "admin") {
        window.location.href = "/admin";
    } else {
        window.location.href = "/user";
    }
}


// ✅ Function to Display Transaction Details on Click
function showTransactionDetails(index) {
    const transaction = window.transactions[index];

    if (!transaction) {
        alert("⚠️ Transaction data not found!");
        return;
    }

    const detailsContainer = document.getElementById("transactionDetails");

    if (!detailsContainer) {
        console.error("❌ Error: #transactionDetails element not found!");
        return;
    }

    detailsContainer.innerHTML = `
        <h3>Transaction Details</h3>
        <p><strong>Amount:</strong> ${transaction.transaction.amt}</p>
        <p><strong>Category:</strong> ${transaction.transaction.category}</p>
        <p><strong>Merchant:</strong> ${transaction.transaction.merchant}</p>
        <p><strong>Transaction Day:</strong> ${transaction.transaction.trans_day}</p>
        <p><strong>Fraud Probability:</strong> ${transaction.fraud_probability}</p>
    `;
}

// ✅ Delete User Account
async function deleteUserAccount() {
    try {
        const response = await fetchWithAuth("/api/user/delete", "DELETE");
        if (response) {
            alert(response.message);
            logout();
        }
    } catch (error) {
        alert("❌ Error deleting account: " + error.message);
    }
}

// ✅ Fraud Detection & Prediction
async function predictFraud() {
    const token = localStorage.getItem("token"); // Retrieve JWT from local storage

    if (!token) {
        alert("⚠️ Unauthorized! Please login first.");
        return;
    }

    const amt = document.getElementById("amt").value;
    const trans_hour = document.getElementById("trans_hour").value;
    const trans_day = document.getElementById("trans_day").value;
    const merchant = document.getElementById("merchant").value;
    const category = document.getElementById("category").value;
    const gender = document.getElementById("gender").value;

    if (!amt || !trans_hour || !trans_day || !merchant || !category || !gender) {
        alert("⚠️ Please fill all fields!");
        return;
    }

    const transactionData = {
        amt: parseFloat(amt),
        trans_hour: parseInt(trans_hour),
        trans_day: parseInt(trans_day),
        merchant,
        category,
        gender
    };

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}` // Include JWT in headers
            },
            body: JSON.stringify(transactionData)
        });

        const result = await response.json();
        console.log("API Response:", result);

        if (result.error) {
            alert("❌ Error: " + result.error);
            return;
        }

        let resultText = result.fraudulent
            ? `🚨 High Fraud Risk! Probability: ${(result.fraud_probability * 100).toFixed(2)}%`
            : `✅ Legitimate Transaction (Fraud Probability: ${(result.fraud_probability * 100).toFixed(2)}%)`;

        document.getElementById("result").innerText = resultText;
        document.getElementById("result").style.color = result.fraudulent ? "red" : "green";

    } catch (error) {
        console.error("Error:", error);
        alert("⚠️ Failed to predict. Please check the backend.");
    }
}



function goToHome() {
    window.location.href = "/predict"; // Change this to the correct route if needed
}


// ✅ Load user profile on page load
document.addEventListener("DOMContentLoaded", function () {
    if (window.location.pathname.includes("/admin")) {
        loadAdminPanel();
    }
});


document.addEventListener("DOMContentLoaded", function () {
    console.log("Script loaded and DOM fully loaded.");

    // Retrieve the username from localStorage
    const username = localStorage.getItem("username");
    console.log("Retrieved username:", username);

    // Select the span element where the username should be displayed
    const usernameElement = document.getElementById("username");
    console.log("Username element found:", usernameElement);

    // Check if the element and username exist before updating the text
    if (usernameElement && username) {
        usernameElement.textContent = username;
        console.log("Username updated in HTML.");
    } else {
        console.error("Failed to update username. Either username is null or element is not found.");
    }
});
