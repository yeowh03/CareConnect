import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import TopNav from "../../Components/TopNav";
import httpClient from "../../httpClient";
import CommunityClubsMap from "../../Components/CommunityClubsMap";
import "../../styles/ManagerHome.css";

export default function ManagerHome() {
  const [email, setEmail] = useState("");
  const [query, setQuery] = useState("");
  const [count, setCount] = useState(0);
  const navigate = useNavigate();

  // Fetch logged-in manager info
  useEffect(() => {
    const fetchData = async () => {
      try {
        const resp = await httpClient.get("/api/@me");
        setEmail(resp.data.email);
      } catch (error) {
        alert("Not authenticated");
        navigate("/login");
      }
    };
    fetchData();
  }, [navigate]);

  return (
    <>
      <TopNav role="Manager" />
      <div className="manager-home">
        <h2 className="manager-home-title">
          Home
        </h2>

        {/* === Search Bar === */}
        <div className="manager-filter-bar">
          <input
            type="text"
            placeholder="Search Community Club by name…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Escape" && setQuery("")}
            className="manager-filter-input"
          />

          {query && (
            <button
              onClick={() => setQuery("")}
              className="manager-filter-btn"
              title="Clear search"
            >
              Clear
            </button>
          )}

          <span className="manager-result-count">
            {count} result{count === 1 ? "" : "s"}
          </span>
        </div>

        {/* === Interactive Map === */}
        <div className="manager-map-container">
          <CommunityClubsMap
            query={query}
            height="65vh"
            onCountChange={setCount}
          />
        </div>
      </div>
    </>
  );
}