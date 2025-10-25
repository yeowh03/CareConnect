// import { useEffect, useState } from "react";
// import { Link, useNavigate, useLocation } from "react-router-dom";
// import httpClient from "../httpClient";

// export default function ManagerRegistrations() {
//   const [email, setEmail] = useState("");
//   const [registrations, setRegistrations] = useState("");
//   const [err, setErr] = useState("");
//   const navigate = useNavigate();

//   const fetchData = async () => {
//       try {
//         const me = await httpClient.get("/api/@me");
//         if (!me || me.data.role !== "M") {
//           alert("Not authenticated as Manager!");
//           navigate("/login");
//           return;
//         }
//         setEmail(me.data.email);
        
//         const r = await httpClient.get(`/api/pending_registrations`);
//         setRegistrations(r.data);

//       } catch (error) {
//           if (error.response?.data?.message == "Not authenticated!"){
//           alert("Not authenticated!");
//           navigate("/login");
//           return;
//         }
//         setErr(error.response?.data?.message);
//       }
//     };

//   useEffect(() => {
//     fetchData();
//   }, []);

//   const handleAccept = async (email) => {
//     try {
//         const resp = await httpClient.post("/api/process_registrations", {email:email, outcome:true});
//         alert("Accepted Succesfully!");
//         fetchData()
//     } catch (error) {
//         alert("error");
//         fetchData()
//     }
//   }

//   const handleReject = async (email) => {
//     try {
//         const resp = await httpClient.post("/api/process_registrations", {email:email, outcome:false});
//         alert("Rejected Succesfully!");
//         fetchData()
//     } catch (error) {
//         alert("error");
//         fetchData()
//     }
//   }

//   if (registrations.length == 0) {
//     return (
//         <p>No Pending Registrations.</p>
//     )
//   } else {
//     return (
//         <div>
//             {err && (
//               <div style={{ background: "#fde2e2", border: "1px solid #f6bcbc", padding: 12, borderRadius: 8, marginBottom: 12, color: "#7a0b0b" }}>
//                 {err}
//               </div>
//             )}

//             {registrations.map((r) => (
//                 <div key={r.client.email}>
//                     <p>Name: {r.user.name}</p>
//                     <p>Email: {r.client.email}</p>
//                     <p>Monthy Income: {r.client.monthly_income}</p>
//                     <p>Contact Number: {r.user.contact_number}</p>
//                     <button onClick={()=>handleAccept(r.client.email)}>Accept</button>
//                     <button onClick={()=>handleReject(r.client.email)}>Reject</button>
//                     <hr/>
//                 </div>
//             ))}
//         </div>
//     )
//     }
// }

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import httpClient from "../httpClient";
import { FaArrowLeft } from "react-icons/fa";
import "../styles/ManageRegistrations.css";

export default function ManagerRegistrations() {
  const [email, setEmail] = useState("");
  const [registrations, setRegistrations] = useState([]);
  const [err, setErr] = useState("");
  const navigate = useNavigate();

  const fetchData = async () => {
    try {
      const me = await httpClient.get("/api/@me");
      if (!me || me.data.role !== "M") {
        alert("Not authenticated as Manager!");
        navigate("/login");
        return;
      }
      setEmail(me.data.email);

      const r = await httpClient.get(`/api/pending_registrations`);
      setRegistrations(r.data || []);
    } catch (error) {
      if (error.response?.data?.message === "Not authenticated!") {
        alert("Not authenticated!");
        navigate("/login");
        return;
      }
      setErr(error.response?.data?.message || "Failed to load registrations");
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAccept = async (email) => {
    try {
      await httpClient.post("/api/process_registrations", { email, outcome: true });
      alert("Accepted successfully!");
      fetchData();
    } catch {
      alert("Error processing request");
      fetchData();
    }
  };

  const handleReject = async (email) => {
    try {
      await httpClient.post("/api/process_registrations", { email, outcome: false });
      alert("Rejected successfully!");
      fetchData();
    } catch {
      alert("Error processing request");
      fetchData();
    }
  };

  if (registrations.length === 0) {
    return (
      <div className="manager-registrations-container">
        <button className="icon-btn back-btn" onClick={() => navigate(-1)}>
          <FaArrowLeft />
        </button>
        <h2 className="page-title">Pending Registrations</h2>
        <p className="empty-text">No pending registrations.</p>
      </div>
    );
  }

  return (
    <div className="manager-registrations-container">
      {/* Back button */}
      <button className="icon-btn back-btn" onClick={() => navigate(-1)}>
        <FaArrowLeft />
      </button>

      <h2 className="page-title">Pending Registrations</h2>

      {err && <div className="error-box">{err}</div>}

      <div className="registrations-list">
        {registrations.map((r) => (
          <div key={r.client.email} className="registration-card">
            <p><strong>Name:</strong> {r.user.name}</p>
            <p><strong>Email:</strong> {r.client.email}</p>
            <p><strong>Monthly Income:</strong> {r.client.monthly_income}</p>
            <p><strong>Contact Number:</strong> {r.user.contact_number}</p>
            <div className="registration-actions">
              <button
                className="accept-btn"
                onClick={() => handleAccept(r.client.email)}
              >
                Accept
              </button>
              <button
                className="reject-btn"
                onClick={() => handleReject(r.client.email)}
              >
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}