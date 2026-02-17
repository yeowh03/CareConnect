import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import httpClient from "../../httpClient";
import TopNav from "../../Components/TopNav";
import "../../styles/RequestsList.css";

const fmtDateTime = (iso) => {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
};

export default function RequestsList() {
  const navigate = useNavigate();

  const [me, setMe] = useState(null);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState("");

  const [statusFilter, setStatusFilter] = useState("ALL");
  const [categoryFilter, setCategoryFilter] = useState("ALL");

  const statusOptions = ["ALL", "Pending", "Matched", "Expired", "Completed"];
  const categoryOptions = useMemo(() => {
    const set = new Set(requests.map((r) => r.request_item).filter(Boolean));
    return ["ALL", ...Array.from(set).sort((a, b) => a.localeCompare(b))];
  }, [requests]);

  const fetchRequests = async () => {
    try {
      const resp = await httpClient.get("/api/my_requests");
      setRequests(resp.data?.requests || []);
    } catch (e) {
      console.error("Failed to fetch requests:", e);
      setError("Failed to load requests. Please try again.");
    }
  };

  useEffect(() => {
    (async () => {
      try {
        const u = await httpClient.get("/api/@me");
        if (!u?.data?.authenticated) throw new Error("Not authenticated");
        setMe(u.data);
        await fetchRequests();
      } catch (e) {
        setError(e?.response?.data?.message || "Please log in to view your requests.");
        navigate("/login");
        return;
      } finally {
        setLoading(false);
      }
    })();
  }, [navigate]);

  const filtered = useMemo(() => {
    return requests
      .filter((r) => (statusFilter === "ALL" ? true : r.status === statusFilter))
      .filter((r) => (categoryFilter === "ALL" ? true : r.request_item === categoryFilter))
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  }, [requests, statusFilter, categoryFilter]);

  const resetFilters = () => {
    setStatusFilter("ALL");
    setCategoryFilter("ALL");
  };

  const onReject = async (r) => {
    if (!window.confirm("Reject this matched request? Items will be reallocated where possible.")) return;
    try {
      setBusyId(r.id);
      await httpClient.post("/api/requests/reject", {
        i: r.request_item,
        location: r.location,
        r: r.id,
      });
      await fetchRequests();
    } catch (e) {
      const msg = e?.response?.data?.message || "Failed to reject request";
      alert(msg);
    } finally {
      setBusyId(null);
    }
  };

  const onDelete = async (r) => {
    if (!window.confirm("Delete this pending request? Any reserved items will be released.")) return;
    try {
      setBusyId(r.id);
      await httpClient.delete(`/api/requests/${r.id}`);
      await fetchRequests();
    } catch (e) {
      alert(e?.response?.data?.message || "Failed to delete request");
    } finally {
      setBusyId(null);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <h2>My Requests</h2>
        <div>Loading…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <h2>My Requests</h2>
        <div className="error-box">{error}</div>
      </div>
    );
  }

  return (
    <>
      <TopNav role="Client" />
      <div className="page-container">
        <div className="page-header">
          <h2>My Requests</h2>
        </div>

        {/* === Filters === */}
        <div className="filters-bar">
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            {statusOptions.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>

          <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
            {categoryOptions.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>

          <div className="filter-buttons">
            <button onClick={resetFilters} title="Reset filters">
              Reset
            </button>
            <button onClick={fetchRequests} title="Refresh list">
              Refresh
            </button>
          </div>
        </div>

        {/* === List === */}
        {filtered.length === 0 ? (
          <div className="empty-box">No requests found.</div>
        ) : (
          <div className="requests-grid">
            {filtered.map((r) => (
              <div key={r.id} className="request-card">
                <div className="request-top">
                  <div>
                    <div className="request-title">
                      {r.request_item ?? "—"}{" "}
                      <span className="request-qty">× {r.request_quantity ?? 0}</span>
                    </div>
                    <div className="request-location">
                      Location: <strong>{r.location ?? "—"}</strong>
                    </div>
                  </div>
                  <span className={`status-pill ${r.status?.toLowerCase() || "default"}`}>
                    {r.status ?? "—"}
                  </span>
                </div>

                {r.notes && <div className="request-notes">{r.notes}</div>}

                <div className="request-bottom">
                  <div className="request-meta">
                    Created: {fmtDateTime(r.created_at)} • Allocation:{" "}
                    <strong>
                      {r.allocation ?? 0}/{r.request_quantity ?? 0}
                    </strong>
                  </div>

                  <div className="request-actions">
                    {r.status === "Pending" && r.allocation === 0 && (
                      <Link to={`/requests/${r.id}/edit`} className="btn btn-secondary">
                        Edit
                      </Link>
                    )}

                    {r.status === "Pending" && (
                      <button
                        onClick={() => onDelete(r)}
                        disabled={busyId === r.id}
                        className="btn btn-danger"
                      >
                        {busyId === r.id ? "Deleting…" : "Delete"}
                      </button>
                    )}

                    {r.status === "Matched" && (
                      <button
                        onClick={() => onReject(r)}
                        disabled={busyId === r.id}
                        className="btn btn-danger"
                      >
                        {busyId === r.id ? "Rejecting…" : "Reject"}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}