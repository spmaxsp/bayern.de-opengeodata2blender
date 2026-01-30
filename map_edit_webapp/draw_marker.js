// draw_marker.js
// Encapsulates single marker placement logic for a Leaflet map

function createMarkerPlacer(map) {
  let drawMode = false;
  let marker = null;
  let onComplete = null;

  function enableDraw(callback) {
    drawMode = true;
    onComplete = callback;

    map.dragging.disable();
    map.getContainer().classList.add("draw-active");
  }

  function disableDraw() {
    drawMode = false;

    map.dragging.enable();
    map.getContainer().classList.remove("draw-active");
  }

  function clearMarker() {
    if (marker) {
      map.removeLayer(marker);
      marker = null;
    }
  }

  function placeMarker(latlng) {
    clearMarker();

    marker = L.marker(latlng, {
      draggable: false
    }).addTo(map);
  }

  map.on("mouseup", (e) => {
    if (!drawMode) return;

    placeMarker(e.latlng);
    disableDraw();

    if (onComplete) {
      onComplete(e.latlng);
    }
  });

  return {
    enableDraw,
    placeMarker,
    clearMarker
  };
}
