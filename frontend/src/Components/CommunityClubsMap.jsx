import { useEffect, useRef, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import httpClient from "../httpClient";
import "../styles/CommunityClubsMap.css";

export default function CommunityClubsMap({
  query = "",
  height = "65vh",
  onCountChange,
  role,
  monthlyIncome,
  accountStatus,
}) {
  const mapRef = useRef(null);
  const markersLayerRef = useRef(null);
  const navigate = useNavigate();

  // modal
  const [selected, setSelected] = useState(null); // { name, address?, link?, fulfilmentRate?, lowFulfilment?}

  // data + geo errors
  const [dataError, setDataError] = useState("");
  const [geoError, setGeoError] = useState("");
  const [locating, setLocating] = useState(false);

  // user location refs
  const userMarkerRef = useRef(null);
  const userAccCircleRef = useRef(null);

  // Default (blue) icon
  const markerIcon = new L.Icon({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
  });

  // Red icon (for low fulfilment < 50%)
  const redIcon = new L.Icon({
    iconUrl: "https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-red.png",
    iconRetinaUrl: "https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-red.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
  });


  // init map once
  useEffect(() => {
    if (mapRef.current) return;

    const map = L.map("cc-map", { zoomControl: true });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    map.setView([1.3521, 103.8198], 11);
    markersLayerRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;

    // first load
    fetchAndRender("");

    return () => {
      map.remove();
      mapRef.current = null;
      markersLayerRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // refetch when query changes (debounced)
  useEffect(() => {
    if (!mapRef.current) return;
    const t = setTimeout(() => fetchAndRender(query.trim()), 300);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query]);

  async function fetchAndRender(q) {
    try {
      const res = await httpClient.get("/api/community-clubs", {
        withCredentials: true,
        params: q ? { q } : {},
      });
      const markers = res.data?.markers || [];
      renderMarkers(markers);
      setDataError("");
      onCountChange?.(markers.length);
    } catch (e) {
      console.error(e);
      setDataError("Could not load community clubs. Please check the backend route.");
      onCountChange?.(0);
    }
  }

  function formatPercent(rate) {
    if (rate == null) return "No data";
    return `${Math.round(rate * 100)}%`;
  }

  function renderMarkers(markers) {
    const map = mapRef.current;
    if (!map) return;

    markersLayerRef.current.clearLayers();
    const bounds = L.latLngBounds([]);

    markers.forEach((m) => {
      if (typeof m.lat !== "number" || typeof m.lng !== "number") return;
      const latlng = L.latLng(m.lat, m.lng);

      const iconToUse = m.lowFulfilment ? redIcon : markerIcon;

      const marker = L.marker(latlng, { icon: iconToUse });
      marker.on("click", () =>
        setSelected({
          name: m.name,
          address: m.address,
          link: m.link,
          fulfilmentRate: m.fulfilmentRate,
          lowFulfilment: m.lowFulfilment,
        })
      );

      // Optional: quick tooltip with the rate
      const rateText = m.fulfilmentRate == null ? "No data" : `${Math.round(m.fulfilmentRate * 100)}%`;
      marker.bindTooltip(`Fulfilment: ${rateText}`, { direction: "top", offset: [0, -10] });

      marker.addTo(markersLayerRef.current);
      bounds.extend(latlng);
    });

    if (bounds.isValid()) map.fitBounds(bounds.pad(0.1));
  }

  // --- Geolocation helpers---
  function drawOrUpdateUserLocation(lat, lng, accuracy) {
    const map = mapRef.current;
    if (!map) return;

    if (!userMarkerRef.current) {
      userMarkerRef.current = L.marker([lat, lng], {
        icon: L.divIcon({
          className: "user-loc-dot",
          html: `<div style="
            width:14px;height:14px;border-radius:50%;
            background:#2b6cb0;border:2px solid white;box-shadow:0 0 0 2px rgba(43,108,176,0.35);
          "></div>`,
          iconSize: [14, 14],
          iconAnchor: [7, 7],
        }),
        title: "Your location",
      }).addTo(map);
    } else {
      userMarkerRef.current.setLatLng([lat, lng]);
    }

    const radius = Number.isFinite(accuracy) ? Math.max(accuracy, 10) : 30;
    if (!userAccCircleRef.current) {
      userAccCircleRef.current = L.circle([lat, lng], {
        radius,
        color: "#2b6cb0",
        weight: 1,
        fillOpacity: 0.12,
      }).addTo(map);
    } else {
      userAccCircleRef.current.setLatLng([lat, lng]);
      userAccCircleRef.current.setRadius(radius);
    }
  }

  function handleLocateMe() {
    setGeoError("");
    if (!("geolocation" in navigator)) {
      setGeoError("Geolocation is not supported in this browser.");
      return;
    }
    if (locating) return;

    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude, accuracy } = pos.coords || {};
        drawOrUpdateUserLocation(latitude, longitude, accuracy);
        mapRef.current?.flyTo(
          [latitude, longitude],
          Math.max(mapRef.current?.getZoom?.() || 11, 15),
          { duration: 0.8 }
        );
        setLocating(false);
      },
      (err) => {
        setLocating(false);
        if (err.code === err.PERMISSION_DENIED) setGeoError("Location permission denied.");
        else if (err.code === err.POSITION_UNAVAILABLE) setGeoError("Location unavailable.");
        else if (err.code === err.TIMEOUT) setGeoError("Getting location timed out.");
        else setGeoError("Failed to get your location.");
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
    );
  }

  return (
    <div style={{ position: "relative" }}>
      {/* Map container */}
      <div
        id="cc-map"
        style={{
          height: typeof height === "number" ? `${height}px` : height,
          width: "100%",
          borderRadius: 12,
          overflow: "hidden",
          position: "relative",
        }}
      />

      {/* Locate button (bottom-right) */}
      <div
        style={{
          position: "absolute",
          right: 12,
          bottom: 12,
          zIndex: 1000,
          pointerEvents: "auto",
        }}
      >
        <button
          onClick={handleLocateMe}
          disabled={locating}
          style={{
            padding: "10px 14px",
            borderRadius: 10,
            border: "1px solid #2b6cb0",
            background: locating ? "#e6f0ff" : "#f0f6ff",
            color: "#2b6cb0",
            cursor: locating ? "default" : "pointer",
            fontSize: 14,
            boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
          }}
          title="Show my current location"
        >
          {locating ? "Locating..." : "Locate me"}
        </button>
      </div>

      {/* Errors */}
      {(dataError || geoError) && (
        <div
          style={{
            position: "absolute",
            left: 12,
            bottom: 64,
            background: "rgba(255,255,255,0.95)",
            border: "1px solid #eee",
            padding: "8px 12px",
            borderRadius: 10,
            fontSize: 13,
            color: "#b00020",
            maxWidth: "80%",
            zIndex: 1000,
          }}
        >
          {dataError || geoError}
        </div>
      )}

      {/* Modal */}
      {selected && (
        <div
          className="cc-modal-overlay"
          onClick={() => setSelected(null)}
        >
          <div
            className="cc-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="cc-modal-title"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="cc-modal-header">
              <h2 id="cc-modal-title" className="cc-modal-title">Community Club</h2>
              <button
                className="cc-modal-close"
                aria-label="Close"
                onClick={() => setSelected(null)}
              >
                ✕
              </button>
            </div>

            <p><strong>Name:</strong> {selected.name}</p>
            {selected.address && (
              <p><strong>Address:</strong> {selected.address}</p>
            )}

            <p>
              <strong>Fulfilment rate:</strong> {formatPercent(selected.fulfilmentRate)}
              {selected.lowFulfilment && (
                <>
                  <span className="cc-modal-low">(Below 50%)</span>
                  <span>
                    {" "}
                    Click{" "}
                    <Link to={role == "C" ? "/clientDashboard" : "/managerDashboard"}>
                      here
                    </Link>{" "}
                    to view shortages.
                  </span>
                </>
              )}
            </p>

            {(role == "C" && accountStatus == "Confirmed") && (
              <div className="cc-modal-actions">
                <button
                  className="cc-btn"
                  onClick={() => navigate("/donationForm", { state: { cc: selected.name } })}
                >
                  Donate
                </button>

                {monthlyIncome < 800 && (
                  <button
                    className="cc-btn"
                    onClick={() => navigate("/requestForm", { state: { cc: selected.name } })}
                  >
                    Request
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
