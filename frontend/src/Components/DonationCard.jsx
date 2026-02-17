import { useEffect, useState } from "react";

function formatDate(iso) {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleDateString();
  } catch {
    return iso;
  }
}

/**
 * Reusable donation card that mirrors ManageDonations' design and behavior.
 * - Shows image with click-to-zoom (lightbox)
 * - Displays category, title, qty, location, expiry
 * - Lets parent inject custom footer actions/status via `footer`
 */
export default function DonationCard({ donation, footer }) {
  const d = donation || {};
  const [lightboxOpen, setLightboxOpen] = useState(false);

  // Close lightbox when pressing Escape
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") setLightboxOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <article
      style={{ border: "1px solid #eee", borderRadius: 12, overflow: "hidden", background: "#fff" }}
    >
      {d.image_link ? (
        <button
          onClick={() => setLightboxOpen(true)}
          style={{ padding: 0, border: 0, background: "transparent", cursor: "zoom-in", width: "100%" }}
          aria-label="View full-size image"
        >
          <img
            src={d.image_link}
            alt={d.donation_item}
            style={{ width: "100%", height: 160, objectFit: "cover", display: "block" }}
          />
        </button>
      ) : (
        <div style={{ width: "100%", height: 160, background: "#f5f5f5" }} />
      )}

      <div style={{ padding: 12 }}>
        <div style={{ fontSize: 12, color: "#666" }}>{d.donation_category}</div>
        <h3 style={{ margin: "4px 0 8px" }}>{d.donation_item}</h3>

        <div style={{ display: "grid", gap: 4, fontSize: 13, color: "#555", marginBottom: 8 }}>
          <div>Qty: <strong>{d.donation_quantity}</strong></div>
          <div>Location: {d.location}</div>
          <div>Expiry: {formatDate(d.expiryDate)}</div>
        </div>

        {footer}
      </div>

      {/* Lightbox */}
      {lightboxOpen && d.image_link && (
        <div
          onClick={() => setLightboxOpen(false)}
          style={{
            position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)",
            display: "flex", alignItems: "center", justifyContent: "center", zIndex: 9999,
            padding: 16, cursor: "zoom-out"
          }}
          aria-modal="true"
          role="dialog"
        >
          <img
            src={d.image_link}
            alt="Full size"
            style={{ maxWidth: "95vw", maxHeight: "95vh", display: "block", borderRadius: 8 }}
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </article>
  );
}
