
const InfoFile = {
  meta: {
    title: "",
    lastSaved: null
  },

  area: {
    sw: { lat: null, lng: null },
    ne: { lat: null, lng: null },
    area_m2: null
  },

  origin: {
    lat: null,
    lng: null
  },

  import: {
    terrain: true,
    buildings: true,
    trees: true,
    replaceExistingFiles: false,
    cleanBlender: true
  },

  status: {
    lastBlenderRun: null,
    blenderFile: null,
    mitsubaFile: null
  }
};


function loadFile(file) {
  if (!file) return;

  const reader = new FileReader();
  reader.onload = () => {
    const json = JSON.parse(reader.result);

    Object.assign(InfoFile, json);
    console.log("Loaded InfoFile:");
    updateUIFromInfoFile();
  };

  reader.readAsText(file);
}

function saveFile() {
  InfoFile.meta.lastSaved = new Date().toISOString();

  const blob = new Blob(
    [JSON.stringify(InfoFile, null, 2)],
    { type: "application/json" }
  );

  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = (InfoFile.meta.title || "scene_info") + ".json";
  a.click();

  URL.revokeObjectURL(a.href);
}





const map = L.map("map", {
  zoomControl: false // disable default top-left zoom
}).setView([51.505, -0.09], 13);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors"
}).addTo(map);

// Add zoom control manually at bottom-right
L.control.zoom({ position: 'bottomright' }).addTo(map);



// Create drawer instance
const area_selection = createRectangleDrawer(map);
const origin_marker = createMarkerPlacer(map);


// Get references to inputs
const file_Input = document.getElementById("fileInput");
const title_Input = document.getElementById("fileTitle");
const save_Btn = document.getElementById("saveBtn");

const drawarea_Btn = document.getElementById("drawareaBtn");
const swLat_Input = document.getElementById("swLat");
const swLng_Input = document.getElementById("swLng");
const neLat_Input = document.getElementById("neLat");
const neLng_Input = document.getElementById("neLng");
const area_Output = document.getElementById("areaOutput");

const selorigin_Btn = document.getElementById("originBtn");
const originLat_Input = document.getElementById("originLat");
const originLng_Input = document.getElementById("originLng");

const terrain_Input = document.getElementById("checkbTerrain");
const buildings_Input = document.getElementById("checkbBuildings");
const trees_Input = document.getElementById("checkbTrees");
const replaceFiles_Input = document.getElementById("checkbReplaceFiles");
const cleanBlender_Input = document.getElementById("checkbCleanBlender");

const gen_time_Output = document.getElementById("blenderOutputTime");
const blenderPath_Output = document.getElementById("blenderPath");
const mitsubaPath_Output = document.getElementById("mitsubaPath");


function logInfoFile() {
  console.log(JSON.stringify(InfoFile, null, 2));
}


// Function to update UI from InfoFile
function updateUIFromInfoFile() {
  title_Input.value = InfoFile.meta.title || "";
  
  const area = InfoFile.area;
  swLat_Input.value = area.sw.lat !== null ? area.sw.lat.toFixed(6) : "";
  swLng_Input.value = area.sw.lng !== null ? area.sw.lng.toFixed(6) : "";
  neLat_Input.value = area.ne.lat !== null ? area.ne.lat.toFixed(6) : "";
  neLng_Input.value = area.ne.lng !== null ? area.ne.lng.toFixed(6) : "";
  area_Output.value = area.area_m2 !== null ? (area.area_m2 / 1000000).toFixed(2) + " km²" : "";

  originLat_Input.value = InfoFile.origin.lat !== null ? InfoFile.origin.lat.toFixed(6) : "";
  originLng_Input.value = InfoFile.origin.lng !== null ? InfoFile.origin.lng.toFixed(6) : "";

  terrain_Input.checked = InfoFile.import.terrain;
  buildings_Input.checked = InfoFile.import.buildings;
  trees_Input.checked = InfoFile.import.trees;
  replaceFiles_Input.checked = InfoFile.import.replaceExistingFiles;
  cleanBlender_Input.checked = InfoFile.import.cleanBlender;

  const status = InfoFile.status;
  gen_time_Output.value = status.lastBlenderRun ? new Date(status.lastBlenderRun).toLocaleString() : "N/A";
  blenderPath_Output.value = status.blenderFile || "N/A";
  mitsubaPath_Output.value = status.mitsubaFile || "N/A";

  const markerPos = MarkerFromInfoFile();
  if (markerPos) {
    origin_marker.placeMarker(markerPos);
  }

  const bounds = BoundsFromInfoFile();
  if (bounds) {
    area_selection.drawRectangle(bounds);
  }
}


// Function to update InfoFile from UI
function updateInfoFileFromUI() {
  InfoFile.meta.title = title_Input.value;

  InfoFile.import.terrain = terrain_Input.checked;
  InfoFile.import.buildings = buildings_Input.checked;
  InfoFile.import.trees = trees_Input.checked;
  InfoFile.import.replaceExistingFiles = replaceFiles_Input.checked;
  InfoFile.import.cleanBlender = cleanBlender_Input.checked;

  InfoFile.area.sw.lat = parseFloat(swLat_Input.value) || null;
  InfoFile.area.sw.lng = parseFloat(swLng_Input.value) || null;
  InfoFile.area.ne.lat = parseFloat(neLat_Input.value) || null;
  InfoFile.area.ne.lng = parseFloat(neLng_Input.value) || null;

  InfoFile.origin.lat = parseFloat(originLat_Input.value) || null;
  InfoFile.origin.lng = parseFloat(originLng_Input.value) || null;

  const bounds = BoundsFromInfoFile();
  const area_m2 = bounds.getNorthEast().distanceTo(bounds.getSouthWest()) *
                bounds.getNorthEast().distanceTo(
                  L.latLng(bounds.getSouthWest().lat, bounds.getNorthEast().lng)
                );
  InfoFile.area.area_m2 = area_m2;

  updateUIFromInfoFile();
  logInfoFile();
}

function updateInfoFileAreaFromBounds(bounds) {
  const sw = bounds.getSouthWest();
  const ne = bounds.getNorthEast();

  InfoFile.area.sw.lat = sw.lat;
  InfoFile.area.sw.lng = sw.lng;
  InfoFile.area.ne.lat = ne.lat;
  InfoFile.area.ne.lng = ne.lng;

  const area_m2 = bounds.getNorthEast().distanceTo(bounds.getSouthWest()) *
                  bounds.getNorthEast().distanceTo(
                    L.latLng(bounds.getSouthWest().lat, bounds.getNorthEast().lng)
                  );
  InfoFile.area.area_m2 = area_m2;

  logInfoFile();
  updateUIFromInfoFile();
}

function updateInfoFileOriginFromMarker(latlng) {
  InfoFile.origin.lat = latlng.lat;
  InfoFile.origin.lng = latlng.lng;

  logInfoFile();
  updateUIFromInfoFile();
}



function BoundsFromInfoFile() {
  const area = InfoFile.area;
  if (
    area.sw.lat !== null && area.sw.lng !== null &&
    area.ne.lat !== null && area.ne.lng !== null
  ) {
    return L.latLngBounds(
      [area.sw.lat, area.sw.lng],
      [area.ne.lat, area.ne.lng]
    );
  }
  return null;
}

function MarkerFromInfoFile() {
  const origin = InfoFile.origin;
  if (origin.lat !== null && origin.lng !== null) {
    return L.latLng(origin.lat, origin.lng);
  }
  return null;
}



// Button to enter draw mode
drawarea_Btn.addEventListener("click", () => {
  area_selection.enableDraw((bounds) => {
    updateInfoFileAreaFromBounds(bounds);
  });
});

// Button to place origin point
selorigin_Btn.addEventListener("click", () => {
  origin_marker.enableDraw((latlng) => {
    updateInfoFileOriginFromMarker(latlng);
  });
});

// Update rectangle if inputs change
[swLat_Input, swLng_Input, neLat_Input, neLng_Input].forEach(input => {
  input.addEventListener("change", () => {
    updateInfoFileFromUI();

  });
});

[originLat_Input, originLng_Input].forEach(input => {
  input.addEventListener("change", () => {
    updateInfoFileFromUI();
  });
});

[title_Input, terrain_Input, buildings_Input, trees_Input, replaceFiles_Input, cleanBlender_Input].forEach(input => {
  input.addEventListener("change", () => {
    updateInfoFileFromUI();
  });
});

file_Input.addEventListener("change", (e) => {
  const file = e.target.files[0];
  console.log("Loading file:", file.name);
  loadFile(file);
  updateUIFromInfoFile();
});

save_Btn.addEventListener("click", () => {
  updateInfoFileFromUI();
  saveFile();
});



// Optional: draw a default rectangle on load
const defaultBounds = L.latLngBounds([51.50, -0.12], [51.52, -0.06]);
const defaultOrigin = L.latLng(51.505, -0.09);
area_selection.drawRectangle(defaultBounds);
origin_marker.placeMarker(defaultOrigin);
updateInfoFileAreaFromBounds(defaultBounds);
updateInfoFileOriginFromMarker(defaultOrigin);