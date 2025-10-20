import { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import httpClient from "../httpClient";

export default function ManagerRegistrations() {
  const [email, setEmail] = useState("");
  const [registrations, setRegistrations] = useState("");
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
        console.log(resp.data);
        setEmail(resp.data.email);
        
        const r = await httpClient.get(`/api/pending_registrations`);
        setRegistrations(r.data);

      } catch (error) {
          if (e?.response?.data?.message == "Not authenticated!"){
          alert("Not authenticated as Manager!");
          navigate("/login");
          return;
        }
        setErr(error.response?.data?.message);
      }
    };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAccept = async (email) => {
    try {
        const resp = await httpClient.post("/api/process_registrations", {email:email, outcome:true});
        alert("Accepted Succesfully!");
        fetchData()
    } catch (error) {
        alert("error");
        fetchData()
    }
  }

  const handleReject = async (email) => {
    try {
        const resp = await httpClient.post("/api/process_registrations", {email:email, outcome:false});
        alert("Rejected Succesfully!");
        fetchData()
    } catch (error) {
        alert("error");
        fetchData()
    }
  }

  if (registrations.length == 0) {
    return (
        <p>No Pending Registrations.</p>
    )
  } else {
    return (
        <div>
            {err && (
              <div style={{ background: "#fde2e2", border: "1px solid #f6bcbc", padding: 12, borderRadius: 8, marginBottom: 12, color: "#7a0b0b" }}>
                {err}
              </div>
            )}

            {registrations.map((r) => (
                <div key={r.client.email}>
                    <p>Name: {r.user.name}</p>
                    <p>Email: {r.client.email}</p>
                    <p>Monthy Income: {r.client.monthly_income}</p>
                    <p>Contact Number: {r.user.contact_number}</p>
                    <button onClick={()=>handleAccept(r.client.email)}>Accept</button>
                    <button onClick={()=>handleReject(r.client.email)}>Reject</button>
                    <hr/>
                </div>
            ))}
        </div>
    )
    }
}