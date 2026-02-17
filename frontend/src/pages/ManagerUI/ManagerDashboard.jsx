import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import httpClient from "../../httpClient";
import "../../styles/ManagerDashboard.css";
import { FaArrowLeft, FaFilter } from "react-icons/fa";
import TopNav from "../../Components/TopNav";

export default function ManagerDashboard() {
  const [ccList, setCcList] = useState([]);
  const [selectedCC, setSelectedCC] = useState(null);
  const [filteredCC, setFilteredCC] = useState(null);
  const [ccInventory, setCcInventory] = useState([]);
  const [fulfillmentRate, setFulfillmentRate] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showFilter, setShowFilter] = useState(false);
  const navigate = useNavigate();

  // authenticate
  useEffect(() => {
    (async () => {
      try {
        const resp = await httpClient.get("/api/@me");
        const user = resp.data;
        if (!user || user.role !== "M") {
          alert("Managers only");
          navigate("/login");
          return;
        }
      } catch (error) {
        alert("Not authenticated");
        navigate("/login");
      }
    })();
  }, []);

  // Fetch all CC summaries initially
  useEffect(() => {
    fetchAllCCSummary();
  }, []);

  const fetchAllCCSummary = async () => {
    setLoading(true);
    try {
      const res = await httpClient.get(`/api/manager/cc_summary`);
      const sorted = [...res.data].sort((a, b) => a.location.localeCompare(b.location));
      setCcList(sorted);
      setSelectedCC(null);
      setCcInventory([]);
    } catch (err) {
      console.error("Error fetching CC summary:", err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch complete inventory (not only shortages)
  const fetchCCInventory = async (location) => {
    setLoading(true);
    try {
      // Get all items (not just severe)
      const res = await httpClient.get(`/api/manager/inventory/${location}`);
      setCcInventory(res.data);

      // Extract fulfillment rate from summary
      const ccInfo = ccList.find((c) => c.location === location);
      setFulfillmentRate(ccInfo ? ccInfo.fulfillment_rate : 0);
      setSelectedCC(location);
    } catch (err) {
      console.error("Error fetching CC inventory:", err);
    } finally {
      setLoading(false);
    }
  };

    const handleFilterChange = (e) => {
        const location = e.target.value;
        setFilteredCC(location); // <-- was setSelectedCC
        setShowFilter(false);
    };

  const filteredList = filteredCC
    ? ccList.filter((cc) => cc.location === filteredCC)
    : ccList;

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading manager data...</p>
      </div>
    );
  }

  // Detailed CC inventory view
  if (selectedCC) {
    return (
      <div className="manager-dashboard-container">
        <button className="icon-btn back-btn" onClick={() => setSelectedCC(null)}>
          <FaArrowLeft />
        </button>

        <h1 className="page-title">{selectedCC}</h1>
        <p className="fulfillment-rate">
          Overall Fulfillment Rate:{" "}
          <span className={fulfillmentRate < 50 ? "text-red" : "text-green"}>
            {fulfillmentRate}%
          </span>
        </p>

        <div className="table-container">
          <h2 className="section-title">Inventory Overview</h2>
          <table className="data-table">
            <thead>
              <tr>
                <th>Item Name</th>
                <th>Total Requested</th>
                <th>Total Donated</th>
                <th>Fulfillment %</th>
              </tr>
            </thead>
            <tbody>
              {ccInventory.map((item, i) => (
                <tr
                  key={i}
                  className={item.fulfillment_pct < 50 ? "shortage-row" : ""}
                >
                  <td>{item.item_name}</td>
                  <td>{item.total_requested}</td>
                  <td>{item.total_donated}</td>
                  <td>{item.fulfillment_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Legend */}
          <div className="legend">
            <span className="legend-box shortage"></span>
            <span>Items highlighted in red are in severe shortage (fulfillment &lt; 50%)</span>
          </div>
        </div>
      </div>
    );
  }

  // Overview with all CC cards
  return (
    <>
        <TopNav role = "Manager" />
        <div className="manager-dashboard-container">
        <button className="icon-btn back-btn" onClick={() => navigate("/managerHome")}>
          <FaArrowLeft />
        </button>

        {/* Filter icon and dropdown */}
        <div className="filter-icon-container">
            <button className="icon-btn" onClick={() => setShowFilter(!showFilter)}>
                <FaFilter />
            </button>
            {showFilter && (
                <div className="filter-dropdown">
                    <label htmlFor="ccFilter"><strong>Filter by CC:</strong></label>
                    <select
                    id="ccFilter"
                    value={filteredCC}          // <-- was selectedCC
                    onChange={handleFilterChange}
                    >
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

        <h1 className="page-title">Community Club Dashboard</h1>
        <p className="page-description">
          Click on a Community Club to view its full inventory and shortage insights.
        </p>

        <div className="cc-grid">
            {filteredList.map((cc) => (   // <-- was filteredCC.map
                <div
                key={cc.location}
                className="cc-card clickable"
                onClick={() => fetchCCInventory(cc.location)}
                >
                    <div className="cc-card-header">
                        <h2>{cc.location}</h2>
                    </div>
                    <div className="cc-card-content">
                        <p><strong>Total Donations:</strong> {cc.total_donations}</p>
                        <p><strong>Total Requests:</strong> {cc.total_requests}</p>
                        <p><strong>Fulfilled Requests:</strong> {cc.fulfilled_requests}</p>
                        <p>
                        <strong>Fulfillment Rate:</strong>{" "}
                        <span className={cc.fulfillment_rate < 50 ? "text-red" : "text-green"}>
                            {cc.fulfillment_rate}%
                        </span>
                        </p>
                    </div>
                </div>
                ))}
            </div>
        </div>
    </>
  );
}