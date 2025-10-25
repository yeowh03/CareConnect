import { useState, useEffect } from "react";
import httpClient from "../httpClient";
import { useNavigate, useLocation } from "react-router-dom";
import "../styles/TopNav.css";
import logo from "../assets/logo.png";

function TopNav({ role }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [unreadCount, setUnreadCount] = useState(0);

  // Poll unread count (every 10 seconds)
  useEffect(() => {
    const fetchUnreadCount = async () => {
      try {
        const resp = await httpClient.get("/api/notifications/unread-count");
        setUnreadCount(resp.data?.unread ?? 0);
      } catch (err) {
        console.error("Failed to fetch unread count:", err);
      }
    };

    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 10000);
    return () => clearInterval(interval);
  }, []);

  // When user visits /notification, mark them read
  useEffect(() => {
    const markRead = async () => {
      try {
        await httpClient.post("/api/notifications/mark-read");
        setUnreadCount(0);
      } catch (err) {
        console.error("Failed to mark notifications read:", err);
      }
    };

    if (location.pathname === "/notification") {
      markRead();
    }
  }, [location.pathname]);

  const handleProfile = async () => {
    try {
      const resp = await httpClient.get("/api/@me");
      navigate("/profile", { state: { user_email: resp.data.email } });
    } catch (error) {
      alert(error.response?.status === 401 ? "Invalid credentials" : error.message);
    }
  };

  const handleLogout = async () => {
    try {
      await httpClient.post("/api/logout");
      navigate("/");
    } catch (error) {
      alert(error.response?.status === 401 ? "Invalid credentials" : error.message);
    }
  };

  return (
    <nav className="topnav">
      <div className="nav-container">
        <div
          className="nav-logo"
          onClick={() =>
            navigate(role === "Manager" ? "/managerHome" : "/clientHome")
          }
        >
          <img src={logo} alt="CareConnect Logo" className="logo-img" />
          <span className="logo-text">CareConnect</span>
        </div>

        <div className="nav-buttons">
          {role === "Manager" ? (
            <>
              <button className="nav-btn" onClick={() => navigate("/managerHome")}>
                Home
              </button>
              <button className="nav-btn" onClick={handleProfile}>
                Profile
              </button>

              {/* Notification button with badge */}
              <div className="nav-btn-badge-wrapper">
                <button className="nav-btn" onClick={() => navigate("/notification")}>
                  Notification
                </button>
                {unreadCount > 0 && (
                  <span className="notif-badge-count">{unreadCount}</span>
                )}
              </div>

              <button className="nav-btn" onClick={() => navigate("/subscriptions")}>
                Subscriptions
              </button>
              <button className="nav-btn" onClick={() => navigate("/managerAction")}>
                Action
              </button>
              <button className="nav-btn" onClick={() => navigate("/managerDashboard")}>
                Dashboard
              </button>
              <button className="nav-btn" onClick={handleLogout}>
                Log Out
              </button>
            </>
          ) : (
            <>
              <button className="nav-btn" onClick={() => navigate("/clientHome")}>
                Home
              </button>
              <button className="nav-btn" onClick={handleProfile}>
                Profile
              </button>

              <div className="nav-btn-badge-wrapper">
                <button className="nav-btn" onClick={() => navigate("/notification")}>
                  Notification
                </button>
                {unreadCount > 0 && (
                  <span className="notif-badge-count">{unreadCount}</span>
                )}
              </div>

              <button className="nav-btn" onClick={() => navigate("/subscriptions")}>
                Subscriptions
              </button>
              <button className="nav-btn" onClick={() => navigate("/myRequests")}>
                Requests
              </button>
              <button className="nav-btn" onClick={() => navigate("/myDonations")}>
                Donations
              </button>
              <button className="nav-btn" onClick={() => navigate("/clientDashboard")}>
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
