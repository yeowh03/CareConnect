import { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import httpClient from "../httpClient";

export default function ManagerAction() {
  const [email, setEmail] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resp = await httpClient.get("/api/@me");
        const user = resp.data;
        if (!user || user.role !== "M") {
          alert("Managers only");
          navigate("/login");
          return;
        }
        console.log(user.email);
        setEmail(user.email);

      } catch (error) {
        alert("Not authenticated");
        navigate("/login");
      }
    };
    fetchData();
  }, []);

  return (
    <>
      <button onClick={() => navigate('/manageRegistrations')}>Manage Registrations</button>
      <button onClick={() => navigate('/manageDonations')}>Manage Donations</button>
      <button onClick={() => navigate('/completeRequests')}>Complete Requests</button>
    </>
  )
}