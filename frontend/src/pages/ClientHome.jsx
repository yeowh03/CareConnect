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

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaArrowLeft, FaFilter } from "react-icons/fa"; //  Icon imports
import httpClient from "../httpClient";
import TopNav from "./TopNav";
import "../styles/ClientDashboard.css";

export default function ClientDashboard() {
  const [ccList, setCcList] = useState([]);
  const [selectedCC, setSelectedCC] = useState("");
  const [showFilter, setShowFilter] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAllCCSummary();
  }, []);

  const fetchAllCCSummary = async () => {
    setLoading(true);
    try {
      const res = await httpClient.get("/api/client/cc_summary");
      console.log(res)
      const sortedData = [...res.data].sort((a, b) =>
        a.location.toLowerCase().localeCompare(b.location.toLowerCase())
      );
      console.log(sortedData);
      setCcList(sortedData);
    } catch (err) {
      console.error("Error fetching client summary:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    const location = e.target.value;
    setSelectedCC(location);
    setShowFilter(false);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading community data...</p>
      </div>
    );
  }

  const filteredList = selectedCC
    ? ccList.filter((cc) => cc.location === selectedCC)
    : ccList;

  return (
    <>
    <TopNav role = "Client"/>
    <div className="client-dashboard-container">
      {/*  Filter icon (top-right) */}
      <div className="filter-icon-container">
        <button
          className="icon-btn filter-btn"
          onClick={() => setShowFilter((prev) => !prev)}
        >
          <FaFilter size={18} />
        </button>

        {showFilter && (
          <div className="filter-dropdown">
            <label htmlFor="ccFilter"><strong>Filter by CC:</strong></label>
            <select id="ccFilter" value={selectedCC} onChange={handleFilterChange}>
              <option value="">All CCs</option>
              {ccList.map((cc, i) => (
                <option key={i} value={cc.location}>
                  {cc.location}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <h1 className="page-title">Community Club Inventory</h1>
      <p className="page-description">
        View donation and request statistics for each CC. Items in shortage are highlighted.
      </p>

      <div className="cc-grid">
        {filteredList.map((cc) => (
          <div key={cc.location} className="cc-card">
            <div className="cc-card-header">
              <h2>{cc.location}</h2>
            </div>
            <div className="cc-card-content">
              <p><strong>Total Donations:</strong> {cc.total_donations}</p>
              <p><strong>Total Requests:</strong> {cc.total_requests}</p>
              <p><strong>Fulfilled Requests:</strong> {cc.fulfilled_requests}</p>

              {cc.severe_shortage_items && cc.severe_shortage_items.length > 0 ? (
                <div className="shortage-warning">
                  <p>⚠️ Severe Shortage Items:</p>
                  <ul>
                    {cc.severe_shortage_items.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p className="no-shortage">✅ No severe shortages</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
    </>
  );
}