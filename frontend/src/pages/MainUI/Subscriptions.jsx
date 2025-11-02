import { useEffect, useState } from "react";
import httpClient from "../../httpClient";
import { useNavigate } from "react-router-dom";
import TopNav from "../../Components/TopNav";
import "../../styles/Notifications.css"; // reuse styles

export default function Subscriptions() {
  const navigate = useNavigate();
  const [cc, setCc] = useState("");
  const [subs, setSubs] = useState([]);
  const [names, setNames] = useState([]);
  const [role, setRole] = useState("");

  async function load() {
    try {
      const s = await httpClient.get("/api/broadcast/subscriptions");
      setSubs(s.data.subscriptions || []);

      const c = await httpClient.get("/api/community-clubs");
      const markers = c.data?.markers || [];

      const collected = Array.from(
        new Set(
          markers.map((m) => m?.name).filter(Boolean)
        )
      ).sort((a, b) => a.localeCompare(b));
      setNames(collected);
    } catch (e) {
      console.error(e);
      alert("Please log in to view subscriptions");
    }
  }

  useEffect(() => {
    const run = async () => {
      try {
        const resp = await httpClient.get("/api/@me");
        setRole(resp.data.role);
      } catch {
        alert("Not authenticated");
        navigate("/login");
        return;
      }
      load();
    };
    run();
  }, [navigate]);

  async function subscribe() {
    if (!cc) {
      alert("Choose a Community Club first");
      return;
    }
    try {
      await httpClient.post("/api/broadcast/subscribe", { cc });
      setCc("");
      load();
    } catch (e) {
      console.error("Failed to subscribe:", e);
      alert("Failed to subscribe. Please try again.");
    }
  }

  async function unsubscribe(name) {
    try {
      await httpClient.post("/api/broadcast/unsubscribe", { cc: name });
      load();
    } catch (e) {
      console.error("Failed to unsubscribe:", e);
      alert("Failed to unsubscribe. Please try again.");
    }
  }

  return (
    <>
      {role && <TopNav role={role === "M" ? "Manager" : "Client"} />}
      <div className="notifications-page">
        <h2 className="page-title">Community Club Subscriptions</h2>
        <p>Subscribe for severe shortage announcements from your selected CCs</p>

        <div className="cc-select-row">
          <select
            className="cc-select"
            value={cc}
            onChange={(e) => setCc(e.target.value)}
          >
            <option value="">
              {names.length
                ? "Select a Community Club…"
                : "Loading CC names…"}
            </option>
            {names.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>

          <button
            className="btn-subscribe"
            onClick={subscribe}
            disabled={!cc}
          >
            Subscribe
          </button>
        </div>

        <div className="subscriptions-container">
          {subs.length === 0 ? (
            <p className="section-empty">No active subscriptions.</p>
          ) : (
            <div className="subscriptions-grid">
              {subs.map((s) => (
                <div key={s.id} className="subscription-item">
                    <span className="subscription-name">{s.cc}</span>
                    <button
                        className="unsubscribe-btn"
                        onClick={() => unsubscribe(s.cc)}
                    >
                        Unsubscribe
                    </button>
                    </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}