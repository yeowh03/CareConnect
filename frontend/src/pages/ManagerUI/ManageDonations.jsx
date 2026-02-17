import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import httpClient from "../../httpClient";
import DonationCard from "../../Components/DonationCard";
import { FaArrowLeft } from "react-icons/fa";
import "../../styles/ManageDonations.css";

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
        alert("Managers only");
        navigate("/login");
        return;
      }

      const prof = await httpClient.get(`/api/get_ManagerProfile/${me.email}`);
      setCc(prof.data.cc);

      const res = await httpClient.get("/api/manager/donations");
      setPending(res.data.pending || []);
      setApproved(res.data.approved || []);
    } catch (e) {
      if (e?.response?.data?.message === "Not authenticated!") {
        alert("Not authenticated");
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

  if (loading) return <div className="loading-text">Loading manager donations…</div>;

  return (
    <div className="manager-donations-container">
      {/* Back button */}
      <button className="icon-btn back-btn" onClick={() => navigate(-1)}>
        <FaArrowLeft />
      </button>

      {/* Header */}
      <div className="manager-donations-header">
        <div>
          <h1 className="page-title">Manage Donations</h1>
          <div className="manager-info">
            <strong>{cc}</strong>
          </div>
        </div>
      </div>

      {/* Error message */}
      {err && <div className="error-box">{err}</div>}

      {/* Pending Section */}
      <section className="donations-section">
        <h2 className="section-title">Pending</h2>
        {pending.length === 0 ? (
          <div className="empty-text">No pending donations for {cc}.</div>
        ) : (
          <div className="donations-grid">
            {pending.map((d) => (
              <DonationCard
                key={d.id}
                donation={d}
                footer={
                  <div className="donation-footer">
                    <span className="status-pill pending">Pending</span>
                    <div className="donation-actions">
                      <button
                        onClick={() => handleReject(d.id)}
                        disabled={actionId === d.id}
                        className="reject-btn"
                      >
                        {actionId === d.id ? "Rejecting…" : "Reject"}
                      </button>
                      <button
                        onClick={() => handleApprove(d.id)}
                        disabled={actionId === d.id}
                        className="approve-btn"
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

      {/* Approved Section */}
      <section className="donations-section">
        <h2 className="section-title">Approved</h2>
        {approved.length === 0 ? (
          <div className="empty-text">No approved donations for {cc}.</div>
        ) : (
          <div className="donations-grid">
            {approved.map((d) => (
              <DonationCard
                key={d.id}
                donation={d}
                footer={
                  <div className="donation-footer">
                    <span className="status-pill approved">Approved</span>
                    <div className="donation-actions">
                      <button
                        onClick={() => handleReject(d.id)}
                        disabled={actionId === d.id}
                        className="reject-btn"
                      >
                        {actionId === d.id ? "Rejecting…" : "Reject"}
                      </button>
                      <button
                        onClick={() => handleAdd(d.id)}
                        disabled={actionId === d.id}
                        className="approve-btn"
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