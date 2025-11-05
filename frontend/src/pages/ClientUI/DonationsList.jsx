import { useEffect, useMemo, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import httpClient from "../../httpClient";
import DonationCard from "../../Components/DonationCard";
import TopNav from "../../Components/TopNav";
import "../../styles/DonationsList.css";

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
    return (
      <div className="page-container">
        <h2>My Donations</h2>
        <div>Loading your donations…</div>
      </div>
    );
  }

  return (
    <>
      <TopNav role="Client" />
      <div className="page-container">
        <div className="page-header">
          <div>
            <h2>My Donations</h2>
          </div>
        </div>

        {err && <div className="error-box">{err}</div>}

        {/* === Filters === */}
        <div className="filters-bar">
          <div>
            <label htmlFor="statusFilter">Status</label>
            <select
              id="statusFilter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              {statusOptions.map((s) => (
                <option key={s} value={s}>
                  {s === "ALL" ? "All statuses" : s}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="categoryFilter">Category</label>
            <select
              id="categoryFilter"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              {categoryOptions.map((c) => (
                <option key={c} value={c}>
                  {c === "ALL" ? "All categories" : c}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-buttons">
            <button onClick={resetFilters}>Reset</button>
            <button onClick={() => window.location.reload()}>Refresh</button>
          </div>
        </div>

        {/* === List === */}
        {filtered.length === 0 ? (
          <div className="empty-box">No donations match your filters.</div>
        ) : (
          <div className="donations-grid">
            {filtered.map((d) => (
              <DonationCard
                key={d.id}
                donation={d}
                footer={
                  <div className="donation-footer">
                    <span className={`status-pill ${d.status?.toLowerCase() || "pending"}`}>
                      {d.status || "Pending"}
                    </span>

                    <div className="donation-actions">
                      {d.status === "Pending" && (
                        <Link to={`/donations/${d.id}/edit`} className="btn btn-secondary">
                          Edit
                        </Link>
                      )}
                      {(d.status === "Pending" || d.status === "Approved") && (
                        <button
                          onClick={() => onDeleteDonation(d)}
                          disabled={busyId === d.id}
                          className="btn btn-danger"
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
    </>
  );
}