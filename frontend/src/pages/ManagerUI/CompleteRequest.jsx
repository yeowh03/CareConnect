// // src/pages/CompleteRequest.jsx
// import { useEffect, useState } from "react";
// import { useNavigate } from "react-router-dom";
// import httpClient from "../httpClient";

// export default function CompleteRequest() {
//   const navigate = useNavigate();
//   const [me, setMe] = useState(null);
//   const [cc, setCc] = useState("");
//   const [loading, setLoading] = useState(true);
//   const [requests, setRequests] = useState([]);
//   const [error, setError] = useState("");

//   // 1) Ensure user is logged in and is a Manager
//   useEffect(() => {
//     (async () => {
//       try {
//         const resp = await httpClient.get("/api/@me", { withCredentials: true });
//         const user = resp.data;
//         if (!user || user.role !== "M") {
//           alert("Managers only");
//           navigate("/login");
//           return;
//         }
//         setMe(user);
//       } catch {
//         alert("Not authenticated");
//         navigate("/login");
//       }
//     })();
//   }, [navigate]);

//   // 2) Load manager's matched requests
//   async function loadMatched() {
//     setLoading(true);
//     setError("");
//     try {
//       const resp = await httpClient.get("/api/manager/matched_requests", { withCredentials: true });
//       setRequests(resp.data.requests || []);
//       setCc(resp.data.cc || "");
//     } catch (e) {
//       setError("Failed to load matched requests");
//     } finally {
//       setLoading(false);
//     }
//   }

//   useEffect(() => {
//     if (me) loadMatched();
//   }, [me]);

//   // 3) Complete a request
//   async function markComplete(id) {
//     if (!window.confirm("Mark this request as Completed?")) return;
//     try {
//       await httpClient.post(`/api/manager/requests/${id}/complete`);
//       // Refresh list after completing
//       await loadMatched();
//     } catch (e) {
//       alert("Failed to complete the request");
//     }
//   }

//   if (!me) return null;

//   return (
//     <div style={{ maxWidth: 880, margin: "24px auto", padding: 16 }}>
//       <h2>Matched Requests at {cc || "your CC"}</h2>

//       {loading && <p>Loading…</p>}
//       {error && <p style={{ color: "red" }}>{error}</p>}

//       {!loading && requests.length === 0 && (
//         <div style={{ background: "#f7f7f7", padding: 16, borderRadius: 8 }}>
//           No matched requests found for your CC.
//         </div>
//       )}

//       {!loading && requests.length > 0 && (
//         <table style={{ width: "100%", borderCollapse: "collapse" }}>
//           <thead>
//             <tr style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>
//               <th style={{ padding: 8 }}>ID</th>
//               <th style={{ padding: 8 }}>Requester</th>
//               <th style={{ padding: 8 }}>Category</th>
//               <th style={{ padding: 8 }}>Item</th>
//               <th style={{ padding: 8 }}>Qty</th>
//               <th style={{ padding: 8 }}>Allocated</th>
//               <th style={{ padding: 8 }}>Status</th>
//               <th style={{ padding: 8 }}>Matched At</th>
//               <th style={{ padding: 8 }}>Action</th>
//             </tr>
//           </thead>
//           <tbody>
//             {requests.map(r => (
//               <tr key={r.id} style={{ borderBottom: "1px solid #eee" }}>
//                 <td style={{ padding: 8 }}>{r.id}</td>
//                 <td style={{ padding: 8 }}>{r.requester_email}</td>
//                 <td style={{ padding: 8 }}>{r.request_category}</td>
//                 <td style={{ padding: 8 }}>{r.request_item}</td>
//                 <td style={{ padding: 8 }}>{r.request_quantity}</td>
//                 <td style={{ padding: 8 }}>{r.allocation}</td>
//                 <td style={{ padding: 8 }}>{r.status}</td>
//                 <td style={{ padding: 8 }}>{r.matched_at ? new Date(r.matched_at).toLocaleString() : "-"}</td>
//                 <td style={{ padding: 8 }}>
//                   <button
//                     onClick={() => markComplete(r.id)}
//                     style={{
//                       padding: "6px 10px",
//                       borderRadius: 6,
//                       border: "1px solid #ddd",
//                       background: "#e7f7ee",
//                       cursor: "pointer"
//                     }}
//                     title="Mark as Completed"
//                   >
//                     Mark Complete
//                   </button>
//                 </td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       )}
//     </div>
//   );
// }

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import httpClient from "../../httpClient";
import { FaArrowLeft } from "react-icons/fa";
import "../../styles/CompleteRequest.css";

export default function CompleteRequest() {
  const navigate = useNavigate();
  const [me, setMe] = useState(null);
  const [cc, setCc] = useState("");
  const [loading, setLoading] = useState(true);
  const [requests, setRequests] = useState([]);
  const [error, setError] = useState("");

  // 1) Ensure user is logged in and is a Manager
  useEffect(() => {
    (async () => {
      try {
        const resp = await httpClient.get("/api/@me", { withCredentials: true });
        const user = resp.data;
        if (!user || user.role !== "M") {
          alert("Managers only");
          navigate("/login");
          return;
        }
        setMe(user);
      } catch {
        alert("Not authenticated");
        navigate("/login");
      }
    })();
  }, [navigate]);

  // 2) Load matched requests
  async function loadMatched() {
    setLoading(true);
    setError("");
    try {
      const resp = await httpClient.get("/api/manager/matched_requests", { withCredentials: true });
      setRequests(resp.data.requests || []);
      setCc(resp.data.cc || "");
    } catch (e) {
      setError("Failed to load matched requests");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (me) loadMatched();
  }, [me]);

  // 3) Mark request as completed
  async function markComplete(id) {
    if (!window.confirm("Mark this request as Completed?")) return;
    try {
      await httpClient.post(`/api/manager/requests/${id}/complete`);
      await loadMatched();
    } catch {
      alert("Failed to complete the request");
    }
  }

  if (!me) return null;

  return (
    <div className="complete-requests-container">
      {/* Back Button */}
      <button className="icon-btn back-btn" onClick={() => navigate(-1)}>
        <FaArrowLeft />
      </button>

      {/* Page Header */}
      <div className="complete-header">
        <h2 className="page-title">Matched Requests</h2>
        <div className="manager-info">
            <strong>{cc}</strong>
        </div>
      </div>

      {/* Loading / Error States */}
      {loading && <p className="loading-text">Loading matched requests…</p>}
      {error && <p className="error-box">{error}</p>}

      {/* Empty State */}
      {!loading && requests.length === 0 && (
        <div className="empty-box">
          No matched requests found for your CC.
        </div>
      )}

      {/* Requests Table */}
      {!loading && requests.length > 0 && (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Requester</th>
                <th>Category</th>
                <th>Item</th>
                <th>Qty</th>
                <th>Allocated</th>
                <th>Status</th>
                <th>Matched At</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.requester_email}</td>
                  <td>{r.request_category}</td>
                  <td>{r.request_item}</td>
                  <td>{r.request_quantity}</td>
                  <td>{r.allocation}</td>
                  <td>{r.status}</td>
                  <td>
                    {r.matched_at ? new Date(r.matched_at).toLocaleString() : "-"}
                  </td>
                  <td>
                    <button
                      onClick={() => markComplete(r.id)}
                      className="complete-btn"
                      title="Mark as Completed"
                    >
                      Mark Complete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}