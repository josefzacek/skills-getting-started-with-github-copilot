document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      
      // Clear activity select dropdown (keep the default option)
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Generate participants list HTML
        let participantsSection;
        if (details.participants.length > 0) {
          participantsSection = document.createElement("div");
          participantsSection.className = "participants-section";

          const h5 = document.createElement("h5");
          h5.textContent = "Current Participants:";
          participantsSection.appendChild(h5);

          const ul = document.createElement("ul");
          ul.className = "participants-list";

          details.participants.forEach(email => {
            const li = document.createElement("li");

            const span = document.createElement("span");
            span.className = "participant-email";
            span.textContent = email;
            li.appendChild(span);

            const button = document.createElement("button");
            button.className = "delete-icon";
            button.title = "Remove participant";
            button.textContent = "×";
            button.addEventListener("click", () => {
              unregisterParticipant(name, email);
            });
            li.appendChild(button);

            ul.appendChild(li);
          });

          participantsSection.appendChild(ul);
        } else {
          participantsSection = document.createElement("div");
          participantsSection.className = "participants-section";

          const h5 = document.createElement("h5");
          h5.textContent = "Current Participants:";
          participantsSection.appendChild(h5);

          const p = document.createElement("p");
          p.className = "no-participants";
          p.textContent = "No participants yet - be the first to sign up!";
          participantsSection.appendChild(p);
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;
        activityCard.appendChild(participantsSection);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities list to show updated participant count
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Function to unregister a participant
  window.unregisterParticipant = async function(activityName, email) {
    if (!confirm(`Are you sure you want to remove ${email} from ${activityName}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        // Refresh activities list to show updated participant count
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering:", error);
    }
  };

  // Initialize app
  fetchActivities();
});
