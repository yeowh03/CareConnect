// // src/pages/ClientHome.jsx
// import { useEffect, useState } from "react";
// import { useNavigate } from "react-router-dom";
// import TopNav from "./TopNav";
// import httpClient from "../httpClient";
// import CommunityClubsMap from "./CommunityClubsMap";

// export default function ClientHome() {
//   const [query, setQuery] = useState("");
//   const [count, setCount] = useState(0);
//   const [profile, setProfile] = useState(null);
//   const navigate = useNavigate();

//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         const resp = await httpClient.get("/api/@me");
//         console.log(resp.data);
//         const pf = await httpClient.get(`/api/get_ClientProfile/${resp.data.email}`)
//         console.log(pf.data);
//         setProfile(pf.data);

//       } catch (error) {
//         alert("Not authenticated");
//         navigate("/login");
//       }
//     };
//     fetchData();
//   }, []);

//   const handleEdit = async() => {
//     navigate("/register", {state:{profile:profile}} )
//   }

//   return (
//     <>
//       <TopNav role="Client" />

//       <div style={{ padding: "16px" }}>
//         <h1 style={{ marginTop: 0 }}>Home</h1>
//         <p>Email: {profile?.email}</p>

//         {!profile?.profile_complete && (
//           <div style={{ background: "#fff8e1", padding: 12, borderRadius: 10, marginBottom: 12 }}>
//             Your profile is incomplete. Please fill it in on the <button onClick={handleEdit}>registration</button> page.
//           </div>
//         )}

//         {/* Search */}
//         <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 8, marginBottom: 8, flexWrap: "wrap" }}>
//           <input
//             type="text"
//             placeholder="Search Community Club by name…"
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             onKeyDown={(e) => e.key === "Escape" && setQuery("")}
//             style={{
//               flex: 1,
//               minWidth: 260,
//               padding: "10px 12px",
//               borderRadius: 10,
//               border: "1px solid #ddd",
//               fontSize: 16,
//               outline: "none",
//             }}
//           />
//           {query && (
//             <button
//               onClick={() => setQuery("")}
//               style={{
//                 padding: "10px 14px",
//                 borderRadius: 10,
//                 border: "1px solid #ddd",
//                 background: "#fafafa",
//                 cursor: "pointer",
//               }}
//               title="Clear"
//             >
//               Clear
//             </button>
//           )}
//           <span style={{ fontSize: 13, color: "#666", marginLeft: "auto" }}>
//             {count} result{count === 1 ? "" : "s"}
//           </span>
//         </div>
//       </div>

//       {/* Reusable map */}
//       <div style={{ padding: "0 16px 16px" }}>
//         <CommunityClubsMap
//           query={query}
//           height="65vh"
//           onCountChange={setCount}
//           role = {profile?.role}
//           monthlyIncome = {profile?.monthly_income}
//           accountStatus = {profile?.account_status}
//         />
//       </div>
//     </>
//   );
// }

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