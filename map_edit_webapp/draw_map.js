// draw_map.js
// Encapsulates rectangle drawing logic for a Leaflet map

function createRectangleDrawer(map) {
  let drawMode = false;
  let startLatLng = null;
  let rectangle = null;
  let onComplete = null;

  function enableDraw(callback) {
    drawMode = true;
    startLatLng = null;
    onComplete = callback;

    map.dragging.disable();
    map.getContainer().classList.add("draw-active");
  }

  function disableDraw() {
    drawMode = false;
    startLatLng = null;

    map.dragging.enable();
    map.getContainer().classList.remove("draw-active");
  }

  function clearRectangle() {
    if (rectangle) {
      map.removeLayer(rectangle);
      rectangle = null;
    }
  }

  function drawRectangle(bounds) {
    clearRectangle();
    rectangle = L.rectangle(bounds, {
      color: "blue",
      weight: 2,
      fillOpacity: 0.1
    }).addTo(map);
  }

  map.on("mouseup", (e) => {
    if (!drawMode) return;

    if (!startLatLng) {
      startLatLng = e.latlng;
      clearRectangle();
    } else {
      const bounds = rectangle.getBounds();

      disableDraw();

      if (onComplete) {
        onComplete(bounds);
      }
    }
  });

  map.on("mousemove", (e) => {
    if (!drawMode || !startLatLng) return;

    const bounds = L.latLngBounds(startLatLng, e.latlng);

    if (!rectangle) {
      rectangle = L.rectangle(bounds, {
        color: "blue",
        weight: 2,
        fillOpacity: 0.1
      }).addTo(map);
    } else {
      rectangle.setBounds(bounds);
    }
  });

  return {
    enableDraw,
    drawRectangle,
    clearRectangle
  };
}
