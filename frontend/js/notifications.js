/**
 * SmartMed Notification & Reminder Engine
 * Integrates Web Notifications API, Web Audio API chime, and background checking.
 */

const SmartMedNotifier = {
  // Synthesized Web Audio API medical chime
  playReminderSound: () => {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();

      // Gentle two-tone chime (E5 -> B5)
      const now = ctx.currentTime;
      
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.type = "sine";
      osc1.frequency.setValueAtTime(659.25, now); // E5
      gain1.gain.setValueAtTime(0.15, now);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.start(now);
      osc1.stop(now + 0.4);

      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.type = "sine";
      osc2.frequency.setValueAtTime(987.77, now + 0.2); // B5
      gain2.gain.setValueAtTime(0.2, now + 0.2);
      gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
      osc2.connect(gain2);
      gain2.connect(ctx.destination);
      osc2.start(now + 0.2);
      osc2.stop(now + 0.7);
    } catch (e) {
      console.warn("Audio Context playback unavailable:", e);
    }
  },

  // Request browser notification permission
  requestPermission: async () => {
    if (!("Notification" in window)) {
      showToast("Browser notifications are not supported in this browser.", "warning");
      return false;
    }

    if (Notification.permission === "granted") {
      showToast("Browser notifications are already enabled!", "success");
      return true;
    }

    if (Notification.permission !== "denied") {
      const permission = await Notification.requestPermission();
      if (permission === "granted") {
        showToast("Notification permission granted! You will now receive medicine reminders.", "success");
        SmartMedNotifier.playReminderSound();
        new Notification("SmartMed Reminders Active", {
          body: "You will receive timely alerts when your medicines are due.",
          icon: "assets/icons/pill.png"
        });
        return true;
      } else {
        showToast("Notification permission was denied. You will still receive in-app alerts.", "info");
        return false;
      }
    }
    showToast("Notifications are blocked in your browser settings. Please enable them to get alerts.", "warning");
    return false;
  },

  // Send Browser Notification
  notify: (title, body, tag = null) => {
    SmartMedNotifier.playReminderSound();

    if ("Notification" in window && Notification.permission === "granted") {
      try {
        const notif = new Notification(title, {
          body: body,
          tag: tag || "smartmed-reminder",
          icon: "assets/icons/pill.png"
        });
        notif.onclick = () => {
          window.focus();
          window.location.href = "today.html";
        };
      } catch (e) {
        console.error("Error creating browser notification:", e);
      }
    }

    // Always show in-app toast
    showToast(`<strong>${title}</strong><br>${body}`, "info", 8000);
  },

  // Background checker for due medicines
  startScheduler: () => {
    if (!AuthStorage.getToken()) return;

    let alertedDoses = new Set();

    const checkDueMedicines = async () => {
      try {
        const todayLogs = await SmartMedAPI.schedules.today();
        const now = new Date();
        const currentHours = now.getHours();
        const currentMinutes = now.getMinutes();

        todayLogs.forEach(dose => {
          if (dose.status === "pending") {
            const schedDate = new Date(dose.scheduled_time);
            const schedHours = schedDate.getHours();
            const schedMinutes = schedDate.getMinutes();

            // Match current minute window and not already alerted this minute
            if (schedHours === currentHours && schedMinutes === currentMinutes && !alertedDoses.has(dose.id)) {
              alertedDoses.add(dose.id);
              SmartMedNotifier.notify(
                `Medicine Reminder: ${dose.medicine_name}`,
                `Time to take ${dose.medicine_dosage || ""} (${dose.medicine_form || "dose"}). ${dose.instructions || ""}`,
                `dose-${dose.id}`
              );
            }
          }
        });
      } catch (e) {
        // Silently skip if network error during background poll
      }
    };

    // Run immediately and every 30 seconds
    checkDueMedicines();
    setInterval(checkDueMedicines, 30000);
  }
};

// Start background notification scheduler on load
document.addEventListener("DOMContentLoaded", () => {
  SmartMedNotifier.startScheduler();
});
