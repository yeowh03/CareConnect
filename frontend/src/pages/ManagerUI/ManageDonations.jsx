// import { useEffect, useState } from "react";
// import { Link, useNavigate } from "react-router-dom";
// import httpClient from "../httpClient";
// import DonationCard from "./DonationCard";

// function formatDate(iso) {
//   if (!iso) return "—";
//   try {
//     const d = new Date(iso);
//     return d.toLocaleDateString();
//   } catch {
//     return iso;
//   }
// }

// export default function ManageDonations() {
//   const [email, setEmail] = useState("");
//   const [cc, setCc] = useState("");
//   const [pending, setPending] = useState([]);
//   const [approved, setApproved] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [err, setErr] = useState("");
//   const [actionId, setActionId] = useState(null);
//   const navigate = useNavigate();

//   async function fetchData() {
//     setLoading(true);
//     setErr("");
//     try {
//       const resp = await httpClient.get("/api/@me");
//       const me = resp.data;
//       if (!me || me.role !== "M") {
//         alert("Not authenticated as Manager!!!!");
//         navigate("/login");
//         return;
//       }
//       setEmail(me.email);

//       const prof = await httpClient.get(`/api/get_ManagerProfile/${me.email}`);
//       setCc(prof.data.cc);

//       const res = await httpClient.get("/api/manager/donations");
//       setPending(res.data.pending || []);
//       setApproved(res.data.approved || []);
//     } catch (e) {
//       if (e?.response?.data?.message == "Not authenticated!"){
//         alert("Not authenticated as Manager!");
//         navigate("/login");
//         return;
//       }
//       setErr(e?.response?.data?.message || "Failed to load donations");
//     } finally {
//       setLoading(false);
//     }
//   }

//   useEffect(() => {
//     fetchData();
//     // eslint-disable-next-line react-hooks/exhaustive-deps
//   }, []);

//   const handleApprove = async (id) => {
//     setActionId(id);
//     setErr("");
//     try {
//       await httpClient.post(`/api/manager/donations/${id}/approve`);
//       await fetchData();
//     } catch (e) {
//       setErr(e?.response?.data?.message || "Failed to approve");
//     } finally {
//       setActionId(null);
//     }
//   };

//   const handleAdd = async (id) => {
//     setActionId(id);
//     setErr("");
//     try {
//       await httpClient.post(`/api/manager/donations/${id}/add`);
//       await fetchData();
//     } catch (e) {
//       setErr(e?.response?.data?.message || "Failed to add");
//     } finally {
//       setActionId(null);
//     }
//   };

//   const handleReject = async (id) => {
//     if (!window.confirm("Reject this donation? This will permanently remove it.")) return;
//     setActionId(id);
//     setErr("");
//     try {
//       await httpClient.delete(`/api/manager/donations/${id}/reject`);
//       await fetchData();
//     } catch (e) {
//       setErr(e?.response?.data?.message || "Failed to reject");
//     } finally {
//       setActionId(null);
//     }
//   };

//   if (loading) return <div style={{ padding: 16 }}>Loading manager donations…</div>;

//   return (
//     <div style={{ maxWidth: 1200, margin: "2rem auto", padding: 16 }}>
//       <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
//         <div>
//           <h1 style={{ margin: 0 }}>Manage Donations</h1>
//           <div style={{ color: "#666" }}>{email} — <strong>{cc}</strong></div>
//         </div>
//         <Link to="/managerhome">
//           <button style={{ padding: "10px 16px", borderRadius: 10, background: "#fff", border: "1px solid #ddd" }}>
//             Map
//           </button>
//         </Link>
//       </div>

//       {err && (
//         <div style={{ background: "#fde2e2", border: "1px solid #f6bcbc", padding: 12, borderRadius: 8, marginBottom: 12, color: "#7a0b0b" }}>
//           {err}
//         </div>
//       )}

//       {/* Pending */}
//       <section style={{ marginBottom: 28 }}>
//         <h2 style={{ marginBottom: 12 }}>Pending</h2>
//         {pending.length === 0 ? (
//           <div style={{ color: "#666" }}>No pending donations for {cc}.</div>
//         ) : (
//           <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
//             {pending.map((d) => (
//               <DonationCard
//                 key={d.id}
//                 donation={d}
//                 footer={
//                   <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
//                     <span style={{ fontSize: 12, padding: "4px 8px", borderRadius: 999, background: "#fff7e6", border: "1px solid #ffe0b3", color: "#8a5300" }}>
//                       Pending
//                     </span>
//                     <div style={{ display: "flex", gap: 8 }}>
//                       <button
//                         onClick={() => handleReject(d.id)}
//                         disabled={actionId === d.id}
//                         style={{ padding: "8px 12px", borderRadius: 10, background: "#fff", color: "#b00020", border: "1px solid #f0c2c6" }}
//                         title="Reject and delete donation"
//                       >
//                         {actionId === d.id ? "Rejecting…" : "Reject"}
//                       </button>
//                       <button
//                         onClick={() => handleApprove(d.id)}
//                         disabled={actionId === d.id}
//                         style={{ padding: "8px 12px", borderRadius: 10, background: "#111", color: "#fff", border: 0 }}
//                       >
//                         {actionId === d.id ? "Approving…" : "Approve"}
//                       </button>
//                     </div>
//                   </div>
//                 }
//               />
//             ))}
//           </div>
//         )}
//       </section>

//       {/* Approved */}
//       <section>
//         <h2 style={{ marginBottom: 12 }}>Approved</h2>
//         {approved.length === 0 ? (
//           <div style={{ color: "#666" }}>No approved donations for {cc}.</div>
//         ) : (
//           <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
//             {approved.map((d) => (
//               <DonationCard
//                 key={d.id}
//                 donation={d}
//                 footer={
//                   <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
//                     <span style={{ fontSize: 12, padding: "4px 8px", borderRadius: 999, background: "#e6f0ff", border: "1px solid #c7d4ff", color: "#2848a5" }}>
//                       Approved
//                     </span>
//                     <div style={{ display: "flex", gap: 8 }}>
//                       <button
//                         onClick={() => handleReject(d.id)}
//                         disabled={actionId === d.id}
//                         style={{ padding: "8px 12px", borderRadius: 10, background: "#fff", color: "#b00020", border: "1px solid #f0c2c6" }}
//                         title="Reject and delete donation"
//                       >
//                         {actionId === d.id ? "Rejecting…" : "Reject"}
//                       </button>
//                       <button
//                         onClick={() => handleAdd(d.id)}
//                         disabled={actionId === d.id}
//                         style={{ padding: "8px 12px", borderRadius: 10, background: "#111", color: "#fff", border: 0 }}
//                       >
//                         {actionId === d.id ? "Adding…" : "Add"}
//                       </button>
//                     </div>
//                   </div>
//                 }
//               />
//             ))}
//           </div>
//         )}
//       </section>
//     </div>
//   );
// }

import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import httpClient from "../../httpClient";
import DonationCard from "../../Components/DonationCard";
import { FaArrowLeft } from "react-icons/fa";
import "../../styles/ManageDonations.css";

function formatDate(iso) {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleDateString();
  } catch {
    return iso;
  }
}

export default function ManageDonations() {
  const [cc, setCc] = useState("");
  const [pending, setPending] = useState([]);
  const [approved, setApproved] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [actionId, setActionId] = useState(null);
  const navigate = useNavigate();

  async function fetchData() {
    setLoading(true);
    setErr("");
    try {
      const resp = await httpClient.get("/api/@me");
      const me = resp.data;
      if (!me || me.role !== "M") {
        alert("Managers only");
        navigate("/login");
        return;
      }

      const prof = await httpClient.get(`/api/get_ManagerProfile/${me.email}`);
      setCc(prof.data.cc);

      const res = await httpClient.get("/api/manager/donations");
      setPending(res.data.pending || []);
      setApproved(res.data.approved || []);
    } catch (e) {
      if (e?.response?.data?.message === "Not authenticated!") {
        alert("Not authenticated");
        navigate("/login");
        return;
      }
      setErr(e?.response?.data?.message || "Failed to load donations");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
  }, []);

  const handleApprove = async (id) => {
    setActionId(id);
    setErr("");
    try {
      await httpClient.post(`/api/manager/donations/${id}/approve`);
      await fetchData();
    } catch (e) {
      setErr(e?.response?.data?.message || "Failed to approve");
    } finally {
      setActionId(null);
    }
  };

  const handleAdd = async (id) => {
    setActionId(id);
    setErr("");
    try {
      await httpClient.post(`/api/manager/donations/${id}/add`);
      await fetchData();
    } catch (e) {
      setErr(e?.response?.data?.message || "Failed to add");
    } finally {
      setActionId(null);
    }
  };

  const handleReject = async (id) => {
    if (!window.confirm("Reject this donation? This will permanently remove it.")) return;
    setActionId(id);
    setErr("");
    try {
      await httpClient.delete(`/api/manager/donations/${id}/reject`);
      await fetchData();
    } catch (e) {
      setErr(e?.response?.data?.message || "Failed to reject");
    } finally {
      setActionId(null);
    }
  };

  if (loading) return <div className="loading-text">Loading manager donations…</div>;

  return (
    <div className="manager-donations-container">
      {/* Back button */}
      <button className="icon-btn back-btn" onClick={() => navigate(-1)}>
        <FaArrowLeft />
      </button>

      {/* Header */}
      <div className="manager-donations-header">
        <div>
          <h1 className="page-title">Manage Donations</h1>
          <div className="manager-info">
            <strong>{cc}</strong>
          </div>
        </div>
      </div>

      {/* Error message */}
      {err && <div className="error-box">{err}</div>}

      {/* Pending Section */}
      <section className="donations-section">
        <h2 className="section-title">Pending</h2>
        {pending.length === 0 ? (
          <div className="empty-text">No pending donations for {cc}.</div>
        ) : (
          <div className="donations-grid">
            {pending.map((d) => (
              <DonationCard
                key={d.id}
                donation={d}
                footer={
                  <div className="donation-footer">
                    <span className="status-pill pending">Pending</span>
                    <div className="donation-actions">
                      <button
                        onClick={() => handleReject(d.id)}
                        disabled={actionId === d.id}
                        className="reject-btn"
                      >
                        {actionId === d.id ? "Rejecting…" : "Reject"}
                      </button>
                      <button
                        onClick={() => handleApprove(d.id)}
                        disabled={actionId === d.id}
                        className="approve-btn"
                      >
                        {actionId === d.id ? "Approving…" : "Approve"}
                      </button>
                    </div>
                  </div>
                }
              />
            ))}
          </div>
        )}
      </section>

      {/* Approved Section */}
      <section className="donations-section">
        <h2 className="section-title">Approved</h2>
        {approved.length === 0 ? (
          <div className="empty-text">No approved donations for {cc}.</div>
        ) : (
          <div className="donations-grid">
            {approved.map((d) => (
              <DonationCard
                key={d.id}
                donation={d}
                footer={
                  <div className="donation-footer">
                    <span className="status-pill approved">Approved</span>
                    <div className="donation-actions">
                      <button
                        onClick={() => handleReject(d.id)}
                        disabled={actionId === d.id}
                        className="reject-btn"
                      >
                        {actionId === d.id ? "Rejecting…" : "Reject"}
                      </button>
                      <button
                        onClick={() => handleAdd(d.id)}
                        disabled={actionId === d.id}
                        className="approve-btn"
                      >
                        {actionId === d.id ? "Adding…" : "Add"}
                      </button>
                    </div>
                  </div>
                }
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}