import { useEffect, useMemo, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import httpClient from "../httpClient";
import DonationCard from "./DonationCard";

export default function DonationsList() {
  const [email, setEmail] = useState("");
  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const [busyId, setBusyId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const me = await httpClient.get("/api/@me");
        setEmail(me.data.email);

        const resp = await httpClient.get("/api/my_donations");
        setDonations(resp.data.donations || []);
      } catch (e) {
        setErr(e?.response?.data?.message || "Not authenticated");
        navigate("/login");
        return;
      } finally {
        setLoading(false);
      }
    })();
  }, [navigate]);

  // Build filter option sets from data
  const statusOptions = useMemo(() => {
    const s = new Set();
    for (const d of donations) s.add(d.status || "Pending");
    return ["ALL", ...Array.from(s).sort()];
  }, [donations]);

  const categoryOptions = useMemo(() => {
    const s = new Set();
    for (const d of donations) if (d.donation_category) s.add(d.donation_category);
    return ["ALL", ...Array.from(s).sort()];
  }, [donations]);

  // Apply filters
  const filtered = useMemo(() => {
    return donations.filter((d) => {
      const st = d.status || "Pending";
      const okStatus = statusFilter === "ALL" || st === statusFilter;
      const okCat = categoryFilter === "ALL" || d.donation_category === categoryFilter;
      return okStatus && okCat;
    });
  }, [donations, statusFilter, categoryFilter]);

  const resetFilters = () => {
    setStatusFilter("ALL");
    setCategoryFilter("ALL");
  };

  const onDeleteDonation = async (d) => {
    if (!window.confirm("Delete this donation?")) return;
    try {
      setBusyId(d.id);
      await httpClient.delete(`/api/donations/${d.id}`);
      const resp = await httpClient.get("/api/my_donations");
      setDonations(resp.data.donations || []);
    } catch (e) {
      alert(e?.response?.data?.message || "Failed to delete donation");
    } finally {
      setBusyId(null);
    }
  };

  if (loading) {
    return <div style={{ padding: 16 }}>Loading your donations…</div>;
  }

  return (
    <div style={{ maxWidth: 1080, margin: "2rem auto", padding: 16 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
          gap: 12,
        }}
      >
        <div>
          <h1 style={{ margin: 0 }}>My Donations</h1>
          <div style={{ color: "#666" }}>{email}</div>
        </div>
      </div>

      {/* Error */}
      {err && (
        <div
          style={{
            background: "#fde2e2",
            border: "1px solid #f6bcbc",
            padding: 12,
            borderRadius: 8,
            marginBottom: 12,
            color: "#7a0b0b",
          }}
        >
          {err}
        </div>
      )}

      {/* Filters */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 12,
          alignItems: "end",
          marginBottom: 16,
        }}
      >
        <div>
          <label htmlFor="statusFilter" style={{ display: "block", marginBottom: 6, fontSize: 14 }}>
            Status
          </label>
          <select
            id="statusFilter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #ccc" }}
          >
            {statusOptions.map((s) => (
              <option key={s} value={s}>
                {s === "ALL" ? "All statuses" : s}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="categoryFilter" style={{ display: "block", marginBottom: 6, fontSize: 14 }}>
            Category
          </label>
          <select
            id="categoryFilter"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #ccc" }}
          >
            {categoryOptions.map((c) => (
              <option key={c} value={c}>
                {c === "ALL" ? "All categories" : c}
              </option>
            ))}
          </select>
        </div>

        <div>
          <button
            onClick={resetFilters}
            style={{
              marginTop: 28,
              padding: "10px 16px",
              borderRadius: 10,
              background: "#fff",
              border: "1px solid #ddd",
            }}
          >
            Reset Filters
          </button>
        </div>
      </div>

      {/* List */}
      {filtered.length === 0 ? (
        <div style={{ padding: 16, color: "#666" }}>
          No donations match your filters.
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
            gap: 16,
          }}
        >
          {filtered.map((d) => (
            <DonationCard
              key={d.id}
              donation={d}
              footer={
                <div style={{ marginTop: 8, display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "space-between", alignItems: "center" }}>
                  <span
                    style={{
                      display: "inline-block",
                      fontSize: 12,
                      padding: "4px 8px",
                      borderRadius: 999,
                      background:
                        (d.status || "Pending") === "Approved"
                          ? "#e6f7ed"
                          : (d.status || "Pending") === "Added"
                          ? "#e6f0ff"
                          : "#fff7e6",
                      border:
                        (d.status || "Pending") === "Approved"
                          ? "1px solid #bfe8cf"
                          : (d.status || "Pending") === "Added"
                          ? "1px solid #c7d4ff"
                          : "1px solid #ffe0b3",
                      color:
                        (d.status || "Pending") === "Approved"
                          ? "#0a5b2a"
                          : (d.status || "Pending") === "Added"
                          ? "#2848a5"
                          : "#8a5300",
                    }}
                  >
                    {d.status || "Pending"}
                  </span>

                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    {d.status === "Pending" && (
                      <Link
                        to={`/donations/${d.id}/edit`}
                        style={{ padding:"8px 12px", borderRadius:10, border:"1px solid #cbd5e1", background:"#f8fafc", textDecoration:"none", fontWeight:600 }}
                      >
                        Edit
                      </Link>
                    )}
                    {(d.status === "Pending" || d.status === "Approved") && (
                      <button
                        onClick={() => onDeleteDonation(d)}
                        disabled={busyId === d.id}
                        style={{ padding:"8px 12px", borderRadius:10, border:"1px solid #fecaca", background:"#fff5f5", color:"#7f1d1d", fontWeight:600 }}
                      >
                        {busyId === d.id ? "Deleting…" : "Delete"}
                      </button>
                    )}
                  </div>
                </div>
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}

