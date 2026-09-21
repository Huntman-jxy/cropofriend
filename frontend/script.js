let userLocation = null;

const form = document.getElementById("cropForm");
const imageInput = document.getElementById("image");
const uploadText = document.getElementById("uploadText");
const locationStatus = document.getElementById("locationStatus");
const analyzeBtn = document.getElementById("analyzeBtn");
const statusText = document.getElementById("status");
const results = document.getElementById("results");

imageInput.addEventListener("change", () => {
    uploadText.textContent =
        imageInput.files.length
            ? imageInput.files[0].name
            : "Choose crop image";
});


function getLocation() {
    if (!navigator.geolocation) {
        locationStatus.textContent =
            "Location is not supported by this browser.";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            userLocation = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            };

            locationStatus.textContent =
                `Location detected (${userLocation.latitude.toFixed(4)}, ${userLocation.longitude.toFixed(4)})`;
        },
        () => {
            locationStatus.textContent =
                "Location permission was not granted. Allow location to analyze the crop.";
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 300000
        }
    );
}


getLocation();


form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!userLocation) {
        statusText.textContent =
            "Please allow location access first.";
        getLocation();
        return;
    }

    const file = imageInput.files[0];

    if (!file) {
        statusText.textContent =
            "Please choose a crop image first.";
        return;
    }


    const formData = new FormData();

    // Only send the image and location.
    formData.append("image", file);
    formData.append("latitude", userLocation.latitude);
    formData.append("longitude", userLocation.longitude);


    analyzeBtn.disabled = true;

    statusText.textContent =
        "Analyzing image, weather and risk...";

    results.classList.add("hidden");


    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            body: formData
        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.detail || "Analysis failed."
            );
        }


        renderResults(data);

        statusText.textContent =
            `Analysis saved as report #${data.analysis_id}.`;

        results.classList.remove("hidden");


    } catch (error) {

        statusText.textContent =
            error.message || "Something went wrong.";

    } finally {

        analyzeBtn.disabled = false;

    }
});


function renderResults(data) {

    const disease = data.disease;
    const pest = data.pest;


    // -----------------------------
    // Disease result
    // -----------------------------

    document.getElementById("disease").textContent =
        disease?.label || "No disease detected";

    document.getElementById("diseaseConfidence").textContent =
        disease
            ? `Confidence: ${Math.round(disease.confidence * 100)}%`
            : "";


    // -----------------------------
    // Pest result
    // -----------------------------

    document.getElementById("pest").textContent =
        pest?.label || "No pest detected";

    document.getElementById("pestConfidence").textContent =
        pest
            ? `Confidence: ${Math.round(pest.confidence * 100)}%`
            : "";


    // -----------------------------
    // Severity
    // -----------------------------

    document.getElementById("severity").textContent =
        data.severity || "—";


    // -----------------------------
    // Risk
    // -----------------------------

    document.getElementById("risk").textContent =
        `${data.risk.percentage}%`;

    document.getElementById("riskLevel").textContent =
        data.risk.level;


    // -----------------------------
    // Weather
    // -----------------------------

    const weather = data.weather || {};

    document.getElementById("temperature").textContent =
        weather.temperature != null
            ? `${weather.temperature} °C`
            : "Unavailable";

    document.getElementById("humidity").textContent =
        weather.humidity != null
            ? `${weather.humidity}%`
            : "Unavailable";

    document.getElementById("precipitation").textContent =
        weather.precipitation != null
            ? `${weather.precipitation} mm`
            : "Unavailable";


    // -----------------------------
    // Disease annotated image
    // -----------------------------

    const diseaseImage = document.getElementById("diseaseImage");

    if (diseaseImage && data.disease_image) {
        diseaseImage.src =
            `${data.disease_image}?t=${Date.now()}`;

        diseaseImage.classList.remove("hidden");
    }


    // -----------------------------
    // Pest annotated image
    // -----------------------------

    const pestImage = document.getElementById("pestImage");

    if (pestImage && data.pest_image) {
        pestImage.src =
            `${data.pest_image}?t=${Date.now()}`;

        pestImage.classList.remove("hidden");
    }


    // -----------------------------
    // Demo badge
    // -----------------------------

    document.getElementById("demoBadge")
        .classList.toggle("hidden", !data.demo);
}