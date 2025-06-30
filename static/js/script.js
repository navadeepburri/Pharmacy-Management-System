document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById("darkModeToggle");

    const enableDarkMode = () => {
        document.body.classList.add("dark-mode");
        toggle.textContent = "☀️ Toggle Light Mode";
        localStorage.setItem("dark-mode", "true");
    };

    const disableDarkMode = () => {
        document.body.classList.remove("dark-mode");
        toggle.textContent = "🌙 Toggle Dark Mode";
        localStorage.setItem("dark-mode", "false");
    };

    // On page load
    if (localStorage.getItem("dark-mode") === "true") {
        enableDarkMode();
    } else {
        disableDarkMode();
    }

    if (toggle) {
        toggle.addEventListener("click", () => {
            if (document.body.classList.contains("dark-mode")) {
                disableDarkMode();
            } else {
                enableDarkMode();
            }
        });
    }
});
