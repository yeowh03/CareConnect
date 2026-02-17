// src/pages/ClientHome.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import TopNav from "../../Components/TopNav";
import httpClient from "../../httpClient";
import CommunityClubsMap from "../../Components/CommunityClubsMap";
import "../../styles/ClientHome.css";

export default function ClientHome() {
  const [query, setQuery] = useState("");
  const [count, setCount] = useState(0);
  const [profile, setProfile] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resp = await httpClient.get("/api/@me");
        const pf = await httpClient.get(`/api/get_ClientProfile/${resp.data.email}`);
        setProfile(pf.data);
      } catch (error) {
        alert("Not authenticated");
        navigate("/login");
      }
    };
    fetchData();
  }, []);

  const handleEdit = () => {
    navigate("/register", { state: { profile: profile } });
  };

  return (
    <>
      <TopNav role="Client" />

      <div className="client-home">
        <h2 className="client-home-title">
          Home
        </h2>
        {!profile?.profile_complete && (
          <div className="client-warning-box">
            Your profile is incomplete. Please fill it in on the{" "}
            <button className="link-button" onClick={handleEdit}>
              registration
            </button>{" "}
            page.
          </div>
        )}

        {/* Search Bar */}
        <div className="client-search">
          <input
            type="text"
            placeholder="Search Community Club by name…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Escape" && setQuery("")}
            className="client-search-input"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="client-clear-btn"
              title="Clear"
            >
              Clear
            </button>
          )}
          <span className="client-result-count">
            {count} result{count === 1 ? "" : "s"}
          </span>
        </div>
      </div>

      {/* Reusable Map */}
      <div className="client-map-container">
        <CommunityClubsMap
          query={query}
          height="65vh"
          onCountChange={setCount}
          role={profile?.role}
          monthlyIncome={profile?.monthly_income}
          accountStatus={profile?.account_status}
        />
      </div>
    </>
  );
}