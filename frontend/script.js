const API_URL = "https://croprecomendation-backend.onrender.com";

const form = document.getElementById("cropForm");
const resultCard = document.getElementById("resultCard");
const cropResult = document.getElementById("cropResult");
const confidenceScore = document.getElementById("confidenceScore");

const cityInput = document.getElementById("cityInput");
const fetchWeatherBtn = document.getElementById("fetchWeatherBtn");

// 1. Auto-Fetch Weather & Fill Climate Fields
fetchWeatherBtn.addEventListener("click", async () => {
  const city = cityInput.value.trim();
  if (!city) {
    alert("Please enter a city name first.");
    return;
  }

  try {
    fetchWeatherBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Fetching...';
    
    const geoRes = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&format=json`);
    const geoData = await geoRes.json();
    
    if (!geoData.results || geoData.results.length === 0) {
      alert("City not found.");
      return;
    }

    const { latitude, longitude } = geoData.results[0];

    const weatherRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,precipitation&timezone=auto`);
    const weatherData = await weatherRes.json();

    document.getElementById("temperature").value = Math.round(weatherData.current.temperature_2m * 10) / 10;
    document.getElementById("humidity").value = Math.round(weatherData.current.relative_humidity_2m);
    
    const rain = weatherData.current.precipitation || 120.0;
    document.getElementById("rainfall").value = rain;

  } catch (err) {
    alert("Failed to retrieve weather data.");
  } finally {
    fetchWeatherBtn.innerHTML = '<i class="fa-solid fa-cloud-sun"></i> Auto-Fill Weather';
  }
});

// 2. Submit Crop Prediction Form
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    nitrogen: parseFloat(document.getElementById("nitrogen").value),
    phosphorus: parseFloat(document.getElementById("phosphorus").value),
    potassium: parseFloat(document.getElementById("potassium").value),
    temperature: parseFloat(document.getElementById("temperature").value),
    humidity: parseFloat(document.getElementById("humidity").value),
    ph: parseFloat(document.getElementById("ph").value),
    rainfall: parseFloat(document.getElementById("rainfall").value)
  };

  try {
    const res = await fetch(`${API_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (data.status === "success") {
      cropResult.textContent = data.crop;
      confidenceScore.textContent = `Confidence: ${data.confidence}%`;
      resultCard.classList.remove("hidden");
    } else {
      alert("Prediction error: " + (data.detail || "Invalid input values"));
    }
  } catch (err) {
    alert("Could not connect to the Backend API. Make sure FastAPI is running on port 8000.");
  }
});