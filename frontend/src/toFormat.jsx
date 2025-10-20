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
        console.log(resp.data);
        setEmail(resp.data.email);        
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
    </>
  )
}