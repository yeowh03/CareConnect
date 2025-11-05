import { useEffect, useState } from "react";
import httpClient from "../../httpClient";
import { useNavigate } from "react-router-dom";
import { FaTrash } from "react-icons/fa";
import TopNav from "../../Components/TopNav";
import "../../styles/Notifications.css";

export default function Notifications() {
  const navigate = useNavigate();
  const [notes, setNotes] = useState([]);
  const [role, setRole] = useState("");

  async function load() {
    try {
      const n = await httpClient.get("/api/notifications");
      setNotes(n.data.notifications || []);
    } catch (e) {
      console.error(e);
      alert("Please log in to see notifications");
    }
  }

  useEffect(() => {
    const run = async () => {
      try {
        const resp = await httpClient.get("/api/@me");
        setRole(resp.data.role);
      } catch {
        alert("Not authenticated");
        navigate("/login");
        return;
      }
      load();
    };
    run();
    const t = setInterval(load, 10000);
    return () => clearInterval(t);
  }, [navigate]);

  async function deleteNote(id) {
    try {
      await httpClient.delete(`/api/notifications/${id}`);
      setNotes((curr) => curr.filter((n) => n.id !== id));
    } catch (e) {
      console.error(e);
      alert("Failed to delete notification");
    }
  }

  return (
    <>
      {role && <TopNav role={role === "M" ? "Manager" : "Client"} />}
      <div className="notifications-page">
        <h2 className="page-title">Notifications</h2>
        {notes.length === 0 && <p className="section-empty">No notifications yet.</p>}
        <ul className="section-list">
          {notes.map((n) => (
            <li key={n.id} className="notification-card">
              <button
                onClick={() => deleteNote(n.id)}
                className="delete-btn"
                title="Delete Notification"
              >
                <FaTrash />
              </button>
              <div className="notification-time">
                {new Date(n.created_at).toLocaleString()}
              </div>
              <div className="notification-message">{n.message}</div>
            </li>
          ))}
        </ul>
      </div>
    </>
  );
}