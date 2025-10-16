// main.js — EngageSight frontend logic

const chooseBtn = document.getElementById('chooseBtn');
const input = document.getElementById('fileID');
const form = document.getElementById('uploadForm');
const loadingScreen = document.getElementById('loading-screen');
const resultsDiv = document.getElementById('results');

if (chooseBtn && input) {
  chooseBtn.addEventListener('click', () => input.click());
  input.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) chooseBtn.innerText = "✅ " + file.name;
  });
}

if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    loadingScreen.style.display = "block";
    resultsDiv.style.display = "none";

    const formData = new FormData(form);
    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();

      loadingScreen.style.display = "none";

      if (data.success) {
        resultsDiv.style.display = "block";
        document.getElementById('images-link').href = data.images_url;
        document.getElementById('csv-link').href = data.csv_url;
      } else {
        alert("Processing failed. Please try again.");
      }
    } catch (err) {
      loadingScreen.style.display = "none";
      alert("Error uploading file. Please check your connection.");
      console.error(err);
    }
  });
}

async function loadAnnotatedImages() {
  try {
    const res = await fetch("/download_images");
    const data = await res.json();

    if (data.success && data.annotated_images.length > 0) {
      const gallery = document.getElementById("gallery");
      const grid = document.getElementById("imageGrid");

      grid.innerHTML = ""; // clear old content
      data.annotated_images.forEach(url => {
        const img = document.createElement("img");
        img.src = url;
        img.alt = "Annotated frame";
        grid.appendChild(img);
      });

      gallery.style.display = "block";
      gallery.scrollIntoView({ behavior: "smooth" });
    } else {
      alert("No annotated images found.");
    }
  } catch (err) {
    console.error(err);
    alert("Failed to load annotated images.");
  }
}