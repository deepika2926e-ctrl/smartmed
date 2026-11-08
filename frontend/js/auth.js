/**
 * SmartMed Auth & UI State Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  checkAuthProtection();
  renderUserNavbar();
  highlightActiveSidebar();
  initMobileSidebar();
  startNotificationPolling();
});

// Initialize Theme from localStorage or settings
function initTheme() {
  const savedTheme = localStorage.getItem("smartmed_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  
  const themeToggles = document.querySelectorAll(".theme-toggle-btn");
  themeToggles.forEach(btn => {
    btn.innerHTML = savedTheme === "dark" 
      ? '<i class="fa-solid fa-sun text-warning"></i>' 
      : '<i class="fa-solid fa-moon"></i>';
    btn.onclick = toggleTheme;
  });
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("smartmed_theme", next);

  const themeToggles = document.querySelectorAll(".theme-toggle-btn");
  themeToggles.forEach(btn => {
    btn.innerHTML = next === "dark" 
      ? '<i class="fa-solid fa-sun text-warning"></i>' 
      : '<i class="fa-solid fa-moon"></i>';
  });

  // Optionally update backend settings if logged in
  if (AuthStorage.getToken()) {
    SmartMedAPI.settings.update({ theme: next }).catch(() => {});
  }
}

// Protected route guard
function checkAuthProtection() {
  const path = window.location.pathname;
  const isPublicPage = path.endsWith("index.html") || 
                       path === "/" || 
                       path.endsWith("login.html") || 
                       path.endsWith("register.html") ||
                       path.endsWith("about.html") ||
                       path.endsWith("contact.html") ||
                       path.endsWith("medicine-search.html") ||
                       path.endsWith("medicine-details.html");

  const token = AuthStorage.getToken();

  if (!token && !isPublicPage) {
    window.location.href = "login.html";
  }

  // If already logged in and on login/register page, show redirect hint or go to dashboard
  if (token && (path.endsWith("login.html") || path.endsWith("register.html"))) {
    window.location.href = "dashboard.html";
  }
}

// Render dynamic user details in sidebar/topbar
function renderUserNavbar() {
  const user = AuthStorage.getUser();
  const userNameEls = document.querySelectorAll(".current-user-name");
  const userEmailEls = document.querySelectorAll(".current-user-email");
  const userInitialsEls = document.querySelectorAll(".current-user-initials");

  if (user) {
    userNameEls.forEach(el => el.textContent = user.full_name || "Patient");
    userEmailEls.forEach(el => el.textContent = user.email || "");

    const initials = (user.full_name || "User")
      .split(" ")
      .map(n => n[0])
      .join("")
      .substring(0, 2)
      .toUpperCase();

    userInitialsEls.forEach(el => el.textContent = initials);
  }
}

// Highlight the active link in sidebar
function highlightActiveSidebar() {
  const currentPath = window.location.pathname.split("/").pop() || "index.html";
  const links = document.querySelectorAll(".sidebar-link");
  links.forEach(link => {
    const href = link.getAttribute("href");
    if (href && href === currentPath) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
}

// Mobile sidebar toggle
function initMobileSidebar() {
  const toggleBtn = document.querySelector(".mobile-nav-toggle");
  const sidebar = document.querySelector(".sidebar");
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });

    // Close when clicking outside
    document.addEventListener("click", (e) => {
      if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target) && sidebar.classList.contains("open")) {
        sidebar.classList.remove("open");
      }
    });
  }
}

// Live notification badge updater
function startNotificationPolling() {
  if (!AuthStorage.getToken()) return;

  function updateBadge() {
    SmartMedAPI.notifications.unreadCount()
      .then(res => {
        const badges = document.querySelectorAll(".notification-badge-count");
        badges.forEach(badge => {
          if (res.unread_count > 0) {
            badge.textContent = res.unread_count > 99 ? "99+" : res.unread_count;
            badge.style.display = "inline-flex";
          } else {
            badge.style.display = "none";
          }
        });
      })
      .catch(() => {});
  }

  updateBadge();
  setInterval(updateBadge, 30000); // Poll every 30 seconds
}

// Global logout function
function logoutUser() {
  if (confirm("Are you sure you want to log out of SmartMed?")) {
    SmartMedAPI.auth.logout();
  }
}
