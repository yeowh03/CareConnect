import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import httpClient from "../../httpClient";
import TopNav from "../../Components/TopNav";
import "../../styles/ManagerAction.css";

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
        setEmail(user.email);
      } catch (error) {
        alert("Not authenticated");
        navigate("/login");
      }
    };
    fetchData();
  }, [navigate]);

  return (
    <>
      <TopNav role="Manager" />
      <div className="manager-action">
        <h2 className="manager-action-title">
          Manager Actions
        </h2>

        <div className="manager-info-box">
          Manage pending requests, donations and registrations.
        </div>

        <div className="manager-action-btns">
          <button
            className="manager-btn"
            onClick={() => navigate("/manageRegistrations")}
          >
            Manage Registrations
          </button>
          <button
            className="manager-btn"
            onClick={() => navigate("/manageDonations")}
          >
            Manage Donations
          </button>
          <button
            className="manager-btn"
            onClick={() => navigate("/completeRequests")}
          >
            Complete Requests
          </button>
        </div>
      </div>
    </>
  );
}