/* ============================================================================
   dashboard.js
   ------------
   Powers dashboard.html: fetches jobs/resumes from the Django API, lets a
   recruiter post a job (CREATE), lets a candidate add a resume (CREATE) and
   trigger the AI match (custom endpoint), and renders results (READ).
   ========================================================================== */

// --- Guard: bounce anyone without a valid token back to login ---------------
if (!Auth.isLoggedIn()) {
  window.location.href = "login.html";
}

const user = Auth.getUser();
document.getElementById("welcome-name").textContent = user?.full_name || user?.username || "there";
document.getElementById("role-pill").textContent = user.role;

// Recruiters get a "post a job" form; candidates get a "add resume" form.
if (user.role === "recruiter") {
  document.getElementById("recruiter-panel").style.display = "block";
} else {
  document.getElementById("candidate-panel").style.display = "block";
}

// ----------------------------------------------------------------------------
// JOBS: list (READ) + create (CREATE, recruiter only)
// ----------------------------------------------------------------------------
async function loadJobs() {
  const list = document.getElementById("jobs-list");
  list.innerHTML = "<p class='empty-state'>Loading jobs...</p>";
  try {
    const data = await apiRequest("/jobs/");
    const jobs = data.results || data; // handles paginated or plain list response
    if (!jobs.length) {
      list.innerHTML = "<p class='empty-state'>No jobs posted yet.</p>";
      return;
    }
    list.innerHTML = jobs
      .map(
        (job) => `
        <div class="job-item">
          <div>
            <h4>${escapeHtml(job.title)} - ${escapeHtml(job.company)}</h4>
            <p>${escapeHtml(job.location || "Remote")} · Skills: ${escapeHtml(job.required_skills)}</p>
          </div>
          ${
            user.role === "candidate"
              ? `<button class="btn btn-ghost" onclick="runMatch(${job.id})">Check my match</button>`
              : ""
          }
        </div>`
      )
      .join("");
  } catch (err) {
    list.innerHTML = `<p class='empty-state'>Error loading jobs: ${escapeHtml(err.message)}</p>`;
  }
}

const jobForm = document.getElementById("job-form");
if (jobForm) {
  jobForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      title: jobForm.title.value,
      company: jobForm.company.value,
      description: jobForm.description.value,
      required_skills: jobForm.required_skills.value,
      location: jobForm.location.value,
    };
    try {
      await apiRequest("/jobs/", { method: "POST", body: payload }); // CREATE
      jobForm.reset();
      loadJobs(); // refresh the list -> READ again
    } catch (err) {
      alert("Could not post job: " + err.message);
    }
  });
}

// ----------------------------------------------------------------------------
// RESUMES: list (READ) + create (CREATE, candidate only)
// ----------------------------------------------------------------------------
let myResumes = [];

async function loadResumes() {
  const select = document.getElementById("resume-select");
  try {
    const data = await apiRequest("/resumes/");
    myResumes = data.results || data;
    select.innerHTML = myResumes
      .map((r) => `<option value="${r.id}">${escapeHtml(r.title)}</option>`)
      .join("");
  } catch (err) {
    console.error(err);
  }
}

const resumeForm = document.getElementById("resume-form");
if (resumeForm) {
  resumeForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      title: resumeForm.title.value,
      raw_text: resumeForm.raw_text.value,
    };
    try {
      await apiRequest("/resumes/", { method: "POST", body: payload }); // CREATE
      resumeForm.reset();
      loadResumes();
      alert("Resume saved! Pick a job below and click 'Check my match'.");
    } catch (err) {
      alert("Could not save resume: " + err.message);
    }
  });
}

// ----------------------------------------------------------------------------
// AI MATCH: candidate picks a saved resume, we call Django's custom
// /resumes/{id}/match/{job_id}/ endpoint, which itself calls FastAPI.
// ----------------------------------------------------------------------------
async function runMatch(jobId) {
  const select = document.getElementById("resume-select");
  const resumeId = select.value;
  if (!resumeId) {
    alert("Add a resume first (see the panel above).");
    return;
  }
  const resultsBox = document.getElementById("match-results");
  resultsBox.innerHTML = "<p class='empty-state'>Scoring your resume with AI...</p>";

  try {
    const result = await apiRequest(`/resumes/${resumeId}/match/${jobId}/`, { method: "POST" });
    renderMatchResult(result);
  } catch (err) {
    resultsBox.innerHTML = `<p class='empty-state'>${escapeHtml(err.message)}</p>`;
  }
}

function renderMatchResult(result) {
  const resultsBox = document.getElementById("match-results");
  const scoreClass = result.score >= 70 ? "score-high" : result.score >= 40 ? "score-mid" : "score-low";
  resultsBox.innerHTML = `
    <div class="job-item">
      <div>
        <h4>${escapeHtml(result.job_title)}</h4>
        <p>Matched skills: ${escapeHtml(result.matched_skills) || "none"}</p>
        <p>Missing skills: ${escapeHtml(result.missing_skills) || "none"}</p>
      </div>
      <span class="score-badge ${scoreClass}">${result.score}%</span>
    </div>`;
}

// --- tiny helper to prevent XSS when injecting API text into innerHTML -----
function escapeHtml(str = "") {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

// --- initial load -------------------------------------------------------
loadJobs();
loadResumes();
