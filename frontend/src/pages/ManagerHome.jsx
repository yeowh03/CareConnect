import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import TopNav from "./TopNav";
import httpClient from "../httpClient";
import CommunityClubsMap from "./CommunityClubsMap";

export default function ManagerHome() {
  const [email, setemail] = useState("");
  const [query, setQuery] = useState("");
  const [count, setCount] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resp = await httpClient.get("/api/@me");
        console.log(resp.data);
        setemail(resp.data.email);        
      } catch (error) {
        alert("Not authenticated");
        navigate("/login");
      }
    };
    fetchData();
  }, []);

  return (
    <>
      <TopNav role="Manager"/>
      <div>
        <h1 style={{ marginTop: 0 }}>Home</h1>
        <p>Email: {email}</p>

        {/* Search */}
        <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 8, marginBottom: 8, flexWrap: "wrap" }}>
          <input
            type="text"
            placeholder="Search Community Club by name…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Escape" && setQuery("")}
            style={{
              flex: 1,
              minWidth: 260,
              padding: "10px 12px",
              borderRadius: 10,
              border: "1px solid #ddd",
              fontSize: 16,
              outline: "none",
            }}
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              style={{
                padding: "10px 14px",
                borderRadius: 10,
                border: "1px solid #ddd",
                background: "#fafafa",
                cursor: "pointer",
              }}
              title="Clear"
            >
              Clear
            </button>
          )}
          <span style={{ fontSize: 13, color: "#666", marginLeft: "auto" }}>
            {count} result{count === 1 ? "" : "s"}
          </span>
        </div>
      </div>

      {/* Reusable map */}
        <div style={{ padding: "0 16px 16px" }}>
          <CommunityClubsMap
            query={query}
            height="65vh"
            onCountChange={setCount}
          />
        </div>
    </>
  );
}
