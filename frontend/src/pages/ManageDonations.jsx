// import { useEffect, useState } from "react";
// import { Link, useNavigate } from "react-router-dom";
// import httpClient from "../httpClient";

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
//   const [lightboxUrl, setLightboxUrl] = useState("");
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

//   useEffect(() => {
//     const onKey = (e) => {
//       if (e.key === "Escape") setLightboxUrl("");
//     };
//     window.addEventListener("keydown", onKey);
//     return () => window.removeEventListener("keydown", onKey);
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

//   const Card = ({ d, footer }) => (
//     <article
//       style={{ border: "1px solid #eee", borderRadius: 12, overflow: "hidden", background: "#fff" }}
//     >
//       {d.image_link ? (
//         <button
//           onClick={() => setLightboxUrl(d.image_link)}
//           style={{ padding: 0, border: 0, background: "transparent", cursor: "zoom-in", width: "100%" }}
//           aria-label="View full-size image"
//         >
//           <img
//             src={d.image_link}
//             alt={d.donation_item}
//             style={{ width: "100%", height: 160, objectFit: "cover", display: "block" }}
//           />
//         </button>
//       ) : (
//         <div style={{ width: "100%", height: 160, background: "#f5f5f5" }} />
//       )}
//       <div style={{ padding: 12 }}>
//         <div style={{ fontSize: 12, color: "#666" }}>{d.donation_category}</div>
//         <h3 style={{ margin: "4px 0 8px" }}>{d.donation_item}</h3>

//         <div style={{ display: "grid", gap: 4, fontSize: 13, color: "#555", marginBottom: 8 }}>
//           <div>Qty: <strong>{d.donation_quantity}</strong></div>
//           <div>Location: {d.location}</div>
//           <div>Expiry: {formatDate(d.expiryDate)}</div>
//         </div>

//         {footer}
//       </div>
//     </article>
//   );

//   if (loading) return <div style={{ padding: 16 }}>Loading manager donations…</div>;

//   return (
//     <div style={{ maxWidth: 1200, margin: "2rem auto", padding: 16 }}>
//       <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
//         <div>
//           <h1 style={{ margin: 0 }}>Manage Donations</h1>
//           <div style={{ color: "#666" }}>{email} — <strong>{cc}</strong></div>
//         </div>
//         <Link to="/clienthome">
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
//               <Card
//                 key={d.id}
//                 d={d}
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
//               <Card
//                 key={d.id}
//                 d={d}
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

//       {/* Lightbox */}
//       {lightboxUrl && (
//         <div
//           onClick={() => setLightboxUrl("")}
//           style={{
//             position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)",
//             display: "flex", alignItems: "center", justifyContent: "center", zIndex: 9999,
//             padding: 16, cursor: "zoom-out"
//           }}
//           aria-modal="true"
//           role="dialog"
//         >
//           <img
//             src={lightboxUrl}
//             alt="Full size"
//             style={{ maxWidth: "95vw", maxHeight: "95vh", display: "block", borderRadius: 8 }}
//             onClick={(e) => e.stopPropagation()}
//           />
//         </div>
//       )}
//     </div>
//   );
// }

import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import httpClient from "../httpClient";
import DonationCard from "./DonationCard";

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
  const [email, setEmail] = useState("");
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
        alert("Not authenticated as Manager!!!!");
        navigate("/login");
        return;
      }
      setEmail(me.email);

      const prof = await httpClient.get(`/api/get_ManagerProfile/${me.email}`);
      setCc(prof.data.cc);

      const res = await httpClient.get("/api/manager/donations");
      setPending(res.data.pending || []);
      setApproved(res.data.approved || []);
    } catch (e) {
      if (e?.response?.data?.message == "Not authenticated!"){
        alert("Not authenticated as Manager!");
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  if (loading) return <div style={{ padding: 16 }}>Loading manager donations…</div>;

  return (
    <div style={{ maxWidth: 1200, margin: "2rem auto", padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div>
          <h1 style={{ margin: 0 }}>Manage Donations</h1>
          <div style={{ color: "#666" }}>{email} — <strong>{cc}</strong></div>
        </div>
        <Link to="/managerhome">
          <button style={{ padding: "10px 16px", borderRadius: 10, background: "#fff", border: "1px solid #ddd" }}>
            Map
          </button>
        </Link>
      </div>

      {err && (
        <div style={{ background: "#fde2e2", border: "1px solid #f6bcbc", padding: 12, borderRadius: 8, marginBottom: 12, color: "#7a0b0b" }}>
          {err}
        </div>
      )}

      {/* Pending */}
      <section style={{ marginBottom: 28 }}>
        <h2 style={{ marginBottom: 12 }}>Pending</h2>
        {pending.length === 0 ? (
          <div style={{ color: "#666" }}>No pending donations for {cc}.</div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
            {pending.map((d) => (
              <DonationCard
                key={d.id}
                donation={d}
                footer={
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 12, padding: "4px 8px", borderRadius: 999, background: "#fff7e6", border: "1px solid #ffe0b3", color: "#8a5300" }}>
                      Pending
                    </span>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button
                        onClick={() => handleReject(d.id)}
                        disabled={actionId === d.id}
                        style={{ padding: "8px 12px", borderRadius: 10, background: "#fff", color: "#b00020", border: "1px solid #f0c2c6" }}
                        title="Reject and delete donation"
                      >
                        {actionId === d.id ? "Rejecting…" : "Reject"}
                      </button>
                      <button
                        onClick={() => handleApprove(d.id)}
                        disabled={actionId === d.id}
                        style={{ padding: "8px 12px", borderRadius: 10, background: "#111", color: "#fff", border: 0 }}
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

      {/* Approved */}
      <section>
        <h2 style={{ marginBottom: 12 }}>Approved</h2>
        {approved.length === 0 ? (
          <div style={{ color: "#666" }}>No approved donations for {cc}.</div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
            {approved.map((d) => (
              <DonationCard
                key={d.id}
                donation={d}
                footer={
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 12, padding: "4px 8px", borderRadius: 999, background: "#e6f0ff", border: "1px solid #c7d4ff", color: "#2848a5" }}>
                      Approved
                    </span>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button
                        onClick={() => handleReject(d.id)}
                        disabled={actionId === d.id}
                        style={{ padding: "8px 12px", borderRadius: 10, background: "#fff", color: "#b00020", border: "1px solid #f0c2c6" }}
                        title="Reject and delete donation"
                      >
                        {actionId === d.id ? "Rejecting…" : "Reject"}
                      </button>
                      <button
                        onClick={() => handleAdd(d.id)}
                        disabled={actionId === d.id}
                        style={{ padding: "8px 12px", borderRadius: 10, background: "#111", color: "#fff", border: 0 }}
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

