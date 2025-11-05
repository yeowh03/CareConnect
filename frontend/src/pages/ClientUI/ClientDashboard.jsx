import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaArrowLeft, FaFilter } from "react-icons/fa"; //  Icon imports
import httpClient from "../../httpClient";
import TopNav from "../../Components/TopNav";
import "../../styles/ClientDashboard.css";

export default function ClientDashboard() {
  const [ccList, setCcList] = useState([]);
  const [selectedCC, setSelectedCC] = useState("");
  const [showFilter, setShowFilter] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // authenticate
  useEffect(() => {
    (async () => {
      try {
        const resp = await httpClient.get("/api/@me");
      } catch (error) {
        alert("Not authenticated");
        navigate("/login");
      }
    })();
  }, []);

  useEffect(() => {
    fetchAllCCSummary();
  }, []);

  const fetchAllCCSummary = async () => {
    setLoading(true);
    try {
      const res = await httpClient.get("/api/client/cc_summary");
      console.log(res)
      const sortedData = [...res.data].sort((a, b) =>
        a.location.toLowerCase().localeCompare(b.location.toLowerCase())
      );
      console.log(sortedData);
      setCcList(sortedData);
    } catch (err) {
      console.error("Error fetching client summary:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    const location = e.target.value;
    setSelectedCC(location);
    setShowFilter(false);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading community data...</p>
      </div>
    );
  }

  const filteredList = selectedCC
    ? ccList.filter((cc) => cc.location === selectedCC)
    : ccList;

  return (
    <>
    <TopNav role = "Client"/>
    <div className="client-dashboard-container">
      {/*  Filter icon (top-right) */}
      <div className="filter-icon-container">
        <button
          className="icon-btn filter-btn"
          onClick={() => setShowFilter((prev) => !prev)}
        >
          <FaFilter size={18} />
        </button>

        {showFilter && (
          <div className="filter-dropdown">
            <label htmlFor="ccFilter"><strong>Filter by CC:</strong></label>
            <select id="ccFilter" value={selectedCC} onChange={handleFilterChange}>
              <option value="">All CCs</option>
              {ccList.map((cc, i) => (
                <option key={i} value={cc.location}>
                  {cc.location}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <h1 className="page-title">Community Club Inventory</h1>
      <p className="page-description">
        View donation and request statistics for each CC. Items in shortage are highlighted.
      </p>

      <div className="cc-grid">
        {filteredList.map((cc) => (
          <div key={cc.location} className="cc-card">
            <div className="cc-card-header">
              <h2>{cc.location}</h2>
            </div>
            <div className="cc-card-content">
              <p><strong>Total Donations:</strong> {cc.total_donations}</p>
              <p><strong>Total Requests:</strong> {cc.total_requests}</p>
              <p><strong>Fulfilled Requests:</strong> {cc.fulfilled_requests}</p>

              {cc.severe_shortage_items && cc.severe_shortage_items.length > 0 ? (
                <div className="shortage-warning">
                  <p>⚠️ Severe Shortage Items:</p>
                  <ul>
                    {cc.severe_shortage_items.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p className="no-shortage">✅ No severe shortages</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
    </>
  );
}