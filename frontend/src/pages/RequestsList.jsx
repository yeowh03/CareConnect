// /src/pages/RequestsList.jsx

import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import httpClient from "../httpClient";

const fmtDateTime = (iso) => {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
};

const statusPill = (status) => {
  const base = {
    padding: "2px 8px",
    borderRadius: 999,
    fontSize: 12,
    fontWeight: 600,
    display: "inline-block",
  };
  switch (status) {
    case "Matched":
      return { ...base, color: "#065f46", background: "#d1fae5", border: "1px solid #a7f3d0" };
    case "Pending":
      return { ...base, color: "#1e3a8a", background: "#dbeafe", border: "1px solid #bfdbfe" };
    case "Expired": // NEW
      return { ...base, color: "#991b1b", background: "#fee2e2", border: "1px solid #fecaca" };
    default:
      return { ...base, color: "#334155", background: "#e2e8f0", border: "1px solid #cbd5e1" };
  }
};

export default function RequestsList() {
  const navigate = useNavigate();

  const [me, setMe] = useState(null);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState("");

  // Filters
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [categoryFilter, setCategoryFilter] = useState("ALL");

  const statusOptions = ["ALL", "Pending", "Matched", "Expired", "Completed"];
  const categoryOptions = useMemo(() => {
    const set = new Set(requests.map((r) => r.request_item).filter(Boolean));
    return ["ALL", ...Array.from(set).sort((a, b) => a.localeCompare(b))];
  }, [requests]);

  const fetchRequests = async () => {
    const resp = await httpClient.get("/api/my_requests");
    setRequests(resp.data?.requests || []);
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
    if (!window.confirm("Reject this matched request? Items will be reallocated where possible.")) {
      return;
    }
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
      <div style={{ padding: 24 }}>
        <h2 style={{ marginBottom: 16 }}>My Requests</h2>
        <div>Loading…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 24 }}>
        <h2 style={{ marginBottom: 16 }}>My Requests</h2>
        <div
          style={{
            color: "#b91c1c",
            background: "#fee2e2",
            padding: 12,
            borderRadius: 8,
            border: "1px solid #fecaca",
          }}
        >
          {error}
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: 24, maxWidth: 980, margin: "0 auto" }}>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          justifyContent: "space-between",
          gap: 12,
          flexWrap: "wrap",
        }}
      >
        <h2 style={{ margin: 0 }}>My Requests</h2>
        <div style={{ fontSize: 14, color: "#475569" }}>
          Signed in as <strong>{me?.email}</strong>
        </div>
      </div>

      {/* Filters */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr auto",
          gap: 12,
          marginTop: 16,
          alignItems: "center",
        }}
      >
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{
            padding: 8,
            borderRadius: 8,
            border: "1px solid #cbd5e1",
            background: "white",
          }}
        >
          {statusOptions.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          style={{
            padding: 8,
            borderRadius: 8,
            border: "1px solid #cbd5e1",
            background: "white",
          }}
        >
          {categoryOptions.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        <div style={{ display: "flex", gap: 8 }}>
          <button
            onClick={resetFilters}
            title="Reset filters"
            style={{
              padding: "8px 12px",
              borderRadius: 8,
              border: "1px solid #e2e8f0",
              background: "#f8fafc",
              cursor: "pointer",
            }}
          >
            Reset
          </button>
          <button
            onClick={fetchRequests}
            title="Refresh list"
            style={{
              padding: "8px 12px",
              borderRadius: 8,
              border: "1px solid #e2e8f0",
              background: "#f1f5f9",
              cursor: "pointer",
            }}
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Empty state */}
      {filtered.length === 0 ? (
        <div
          style={{
            marginTop: 24,
            padding: 24,
            borderRadius: 12,
            border: "1px dashed #cbd5e1",
            background: "#f8fafc",
            color: "#475569",
          }}
        >
          No requests found.
        </div>
      ) : (
        <div style={{ marginTop: 20, display: "grid", gap: 12 }}>
          {filtered.map((r) => (
            <div
              key={r.id}
              style={{
                border: "1px solid #e2e8f0",
                borderRadius: 12,
                background: "white",
                padding: 16,
                display: "grid",
                gap: 10,
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  gap: 12,
                  flexWrap: "wrap",
                }}
              >
                <div style={{ display: "grid" }}>
                  <div style={{ fontSize: 16, fontWeight: 700 }}>
                    {r.request_item ?? "—"}{" "}
                    <span style={{ fontWeight: 500, color: "#64748b" }}>
                      × {r.request_quantity ?? 0}
                    </span>
                  </div>
                  <div style={{ fontSize: 13, color: "#475569" }}>
                    Location: <strong>{r.location ?? "—"}</strong>
                  </div>
                </div>
                <div style={{ alignSelf: "flex-start" }}>
                  <span style={statusPill(r.status)}>{r.status ?? "—"}</span>
                </div>
              </div>

              {r.notes && (
                <div style={{ fontSize: 14, color: "#334155", whiteSpace: "pre-wrap" }}>
                  {r.notes}
                </div>
              )}

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 12,
                  flexWrap: "wrap",
                }}
              >
                <div style={{ fontSize: 13, color: "#64748b" }}>
                  Created: {fmtDateTime(r.created_at)} • Allocation:{" "}
                  <strong>
                    {r.allocation ?? 0}/{r.request_quantity ?? 0}
                  </strong>
                </div>

                <div style={{ display: "flex", gap: 8 }}>
                  {r.status === "Pending" && r.allocation === 0 && (
                    <Link
                      to={`/requests/${r.id}/edit`}
                      style={{
                        padding: "8px 12px",
                        borderRadius: 10,
                        border: "1px solid #cbd5e1",
                        background: "#f8fafc",
                        textDecoration: "none",
                        fontWeight: 600,
                      }}
                    >
                      Edit
                    </Link>
                  )}

                  {r.status === "Pending" && (
                    <button
                      onClick={() => onDelete(r)}
                      disabled={busyId === r.id}
                      style={{
                        padding: "8px 12px",
                        borderRadius: 10,
                        border: "1px solid #fecaca",
                        background: busyId === r.id ? "#fff1f2" : "#fff5f5",
                        color: "#7f1d1d",
                        cursor: busyId === r.id ? "not-allowed" : "pointer",
                        fontWeight: 600,
                      }}
                      title="Delete this pending request"
                    >
                      {busyId === r.id ? "Deleting…" : "Delete"}
                    </button>
                  )}
                  
                  {r.status === "Matched" && (
                    <button
                      onClick={() => onReject(r)}
                      disabled={busyId === r.id}
                      style={{
                        padding: "8px 12px",
                        borderRadius: 10,
                        border: "1px solid #fecaca",
                        background: busyId === r.id ? "#fff1f2" : "#fff5f5",
                        color: "#7f1d1d",
                        cursor: busyId === r.id ? "not-allowed" : "pointer",
                        fontWeight: 600,
                      }}
                      title="Reject this matched request"
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
  );
}
