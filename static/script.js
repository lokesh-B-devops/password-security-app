console.log("JS LOADED");

function calculateStrength(password) {
    let score = 0;
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[!@#$%^&*()]/.test(password)) score++;
    return score;
}

// ---- NEW: crack time estimation ----
function estimateCrackTime(password) {
    let charset = 0;
    if (/[a-z]/.test(password)) charset += 26;
    if (/[A-Z]/.test(password)) charset += 26;
    if (/\d/.test(password)) charset += 10;
    if (/[!@#$%^&*()]/.test(password)) charset += 32;

    if (charset === 0) return "instantly";

    const entropy = Math.log2(Math.pow(charset, password.length));
    const guessesPerSecond = 1e10; // strong attacker
    const seconds = Math.pow(2, entropy) / guessesPerSecond;

    if (seconds < 1) return "instantly";
    if (seconds < 60) return `${Math.round(seconds)} seconds`;
    if (seconds < 3600) return `${Math.round(seconds / 60)} minutes`;
    if (seconds < 86400) return `${Math.round(seconds / 3600)} hours`;
    if (seconds < 31536000) return `${Math.round(seconds / 86400)} days`;

    return `${Math.round(seconds / 31536000)} years`;
}

function updateStrength(password) {
    const meter = document.getElementById("meter-fill");
    const text = document.getElementById("strength-text");
    const crackTime = document.getElementById("crack-time");

    const score = calculateStrength(password);

    const strengthMap = [
        { text: "Very Weak", color: "red", width: "20%" },
        { text: "Weak", color: "orange", width: "40%" },
        { text: "Medium", color: "gold", width: "60%" },
        { text: "Strong", color: "blue", width: "80%" },
        { text: "Very Strong", color: "green", width: "100%" }
    ];

    if (score === 0) {
        meter.style.width = "0%";
        text.innerText = "";
        crackTime.innerText = "";
        return;
    }

    const strength = strengthMap[score - 1];
    meter.style.width = strength.width;
    meter.style.background = strength.color;
    text.innerText = "Strength: " + strength.text;

    crackTime.innerText =
        "Estimated time to crack: " + estimateCrackTime(password);
}

function suggestPassword() {
    fetch("/generate-password")
        .then(res => res.json())
        .then(data => {
            const pwd = data.password;
            document.getElementById("password").value = pwd;
            updateStrength(pwd);
        });
}

function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert("Registered successfully\nStrength: " + data.strength);
        }
    });
}

function login() {
    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            username: document.getElementById("login-username").value,
            password: document.getElementById("login-password").value
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.token) {
            localStorage.setItem("token", data.token);
            window.location.href = "/dashboard";
        } else {
            alert("Login failed");
        }
    });
}

