import httpClient from "../httpClient";
import { useNavigate } from "react-router-dom";
import "../styles/TopNav.css";

function TopNav({ role }) {
  const navigate = useNavigate();

  const handleProfile = async () => {
    try {
      const resp = await httpClient.get("/api/@me");
      navigate("/profile", { state: { user_email: resp.data.email } });
    } catch (error) {
      if (error.response?.status === 401) {
        alert("Invalid credentials");
      } else {
        alert(error.message);
      }
    }
  };

  const handleLogout = async () => {
    try {
      await httpClient.post("/api/logout");
      navigate("/");
    } catch (error) {
      if (error.response?.status === 401) {
        alert("Invalid credentials");
      } else {
        alert(error.message);
      }
    }
  };

  return (
    <nav className="topnav">
      <div className="nav-container">
        <h2 className="nav-logo" onClick={() => navigate("/")}>
          CareConnect
        </h2>

        <div className="nav-buttons">
          {role === "Manager" ? (
            <>
              <button
                className="nav-btn"
                onClick={() => navigate("/managerHome")}
              >
                Home
              </button>
              <button className="nav-btn" onClick={handleProfile}>
                Profile
              </button>
              <button
                className="nav-btn"
                onClick={() => navigate("/notification")}
              >
                Notification
              </button>
              <button
                className="nav-btn"
                onClick={() => navigate("/managerAction")}
              >
                Action
              </button>
              <button
                className="nav-btn"
                onClick={() => navigate("/managerDashboard")}
              >
                Dashboard
              </button>
              <button className="logout-btn" onClick={handleLogout}>
                Log Out
              </button>
            </>
          ) : (
            <>
              <button
                className="nav-btn"
                onClick={() => navigate("/clientHome")}
              >
                Home
              </button>
              <button className="nav-btn" onClick={handleProfile}>
                Profile
              </button>
              <button
                className="nav-btn"
                onClick={() => navigate("/notification")}
              >
                Notification
              </button>
              <button
                className="nav-btn"
                onClick={() => navigate("/myRequests")}
              >
                Requests
              </button>
              <button
                className="nav-btn"
                onClick={() => navigate("/myDonations")}
              >
                Donations
              </button>
              <button
                className="nav-btn"
                onClick={() => navigate("/clientDashboard")}
              >
                Inventory
              </button>
              <button className="nav-btn" onClick={handleLogout}>
                Log Out
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

export default TopNav;