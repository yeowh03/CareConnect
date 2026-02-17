import { useEffect, useMemo, useState } from "react";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import httpClient from "../../httpClient";

const CATEGORY_ITEMS = {
  Food: ["Rice","Noodles","Bread","Canned goods","Biscuits & crackers","Cereals & oats","Cooking oil","Flour","Sugar","Soy sauce","Chili sauce","Salt","Pepper"],
  Drinks: ["Bottled water","Packet drinks","Instant coffee / Tea sachets","Milk powder","UHT milk cartons","Canned drinks"],
  Furnitures: ["Chairs","Tables","Shelves","Cabinets","Beds","Baby cots","Sofas"],
  Electronics: ["Mobile phones","Tablets","Laptops","Kettles","Rice cookers","Blenders","Toasters","Fans","Irons","Light bulbs","Extension cords","TVs","Radios"],
  Essentials: ["Soap","Shampoo","Toothpaste","Toothbrushes","Sanitary pads","Detergent","Toilet paper","Masks","Hand sanitizers","First aid basics"],
};

export default function RequestForm() {
  const navigate = useNavigate();
  const { state } = useLocation();
  const { id } = useParams();                 // if present, we are editing
  const editMode = Boolean(id);

  const ccFromState = state?.cc || "";

  const [email, setEmail] = useState("");     // shows who’s logged in
  const [authChecking, setAuthChecking] = useState(true);
  const [loading, setLoading] = useState(editMode);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  // single form state for create + edit
  const [form, setForm] = useState({
    request_category: editMode ? "" : "Food",
    request_item: "",
    request_quantity: 1,
    location: ccFromState,   // will be overwritten by API when editing
    status: "Pending",       // only meaningful on edit
    allocation: 0,           // only meaningful on edit
  });

  // 1) Check auth
  useEffect(() => {
    (async () => {
      try {
        const me = await httpClient.get("/api/@me");
        if (!me?.data?.authenticated) throw new Error("Not authenticated");
        setEmail(me.data.email || "");
      } catch {
        alert("Not authenticated");
        navigate("/login", { replace: true });
        return;
      } finally {
        setAuthChecking(false);
      }
    })();
  }, [navigate]);

  // 2) If editing, load existing request to prefill
  useEffect(() => {
    if (!editMode) return;
    (async () => {
      try {
        const r = await httpClient.get(`/api/requests/${id}`);
        setForm({
          request_category: r.data.request_category,
          request_item: r.data.request_item,
          request_quantity: r.data.request_quantity,
          location: r.data.location,
          status: r.data.status,
          allocation: Number(r.data.allocation || 0),
        });
      } catch (e) {
        setError(e?.response?.data?.message || "Failed to load request.");
      } finally {
        setLoading(false);
      }
    })();
  }, [editMode, id]);

  // dependent item dropdown
  const itemOptions = useMemo(
    () => (form.request_category ? CATEGORY_ITEMS[form.request_category] || [] : []),
    [form.request_category]
  );

  // reset item when category changes
  useEffect(() => {
    setForm((f) => ({ ...f, request_item: "" }));
  }, [form.request_category]);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((f) => ({
      ...f,
      [name]: name === "request_quantity" ? Number(value) : value,
    }));
  }

  const canSave =
    !saving &&
    (!editMode || (form.status === "Pending" && Number(form.allocation || 0) === 0));

  async function onSubmit(e) {
    e.preventDefault();
    setError("");

    // Validate location source:
    const locationToUse = editMode ? form.location : ccFromState;
    if (!locationToUse) return setError("Missing location (CC). Please select a Community Club first.");

    if (!form.request_category) return setError("Select a request category.");
    if (!form.request_item) return setError("Select a request item.");
    if (!form.request_quantity || form.request_quantity < 1)
      return setError("Quantity must be at least 1.");

    try {
      setSaving(true);
      const payload = {
        request_category: form.request_category,
        request_item: form.request_item,
        request_quantity: Number(form.request_quantity),
        location: locationToUse,
      };

      if (editMode) {
        await httpClient.patch(`/api/requests/${id}`, payload);
        alert("Request updated!");
      } else {
        await httpClient.post("/api/requests", payload);
        alert("Request created!");
      }
      navigate("/myRequests");
    } catch (e) {
      setError(
        e?.response?.data?.message ||
          (editMode ? "Failed to update request." : "Failed to create request.")
      );
    } finally {
      setSaving(false);
    }
  }

  if (authChecking) return <div style={{ padding: 16 }}>Checking authentication…</div>;
  if (loading) return <div style={{ padding: 16 }}>Loading…</div>;

  return (
    <div style={{ maxWidth: 640, margin: "2rem auto", padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
        <div>
          <h1 style={{ margin: 0 }}>{editMode ? "Edit Request" : "New Request"}</h1>
          <div style={{ color: "#666" }}>{email}</div>
        </div>
      </div>

      {editMode && form.status !== "Pending" && (
        <div style={{ background:"#fff7e6", border:"1px solid #ffe0b3", color:"#8a5300", padding:12, borderRadius:8, marginBottom:12 }}>
          Only <strong>Pending</strong> requests can be edited. Current status: <strong>{form.status}</strong>.
        </div>
      )}
      {editMode && Number(form.allocation || 0) > 0 && (
        <div style={{ background:"#fee2e2", border:"1px solid #fecaca", padding:12, borderRadius:8, marginBottom:12 }}>
          This request has allocated items. You can’t edit it—delete instead.
        </div>
      )}

      {error && (
        <div style={{ background:"#fde2e2", border:"1px solid #f6bcbc", padding:12, borderRadius:8, marginBottom:12, color:"#7a0b0b" }}>
          {error}
        </div>
      )}

      <form onSubmit={onSubmit}>
        {/* Category */}
        <div style={{ marginBottom: 12 }}>
          <label htmlFor="request_category" style={{ display: "block", marginBottom: 6 }}>
            Request Category *
          </label>
          <select
            id="request_category"
            name="request_category"
            value={form.request_category}
            onChange={handleChange}
            style={{ width:"100%", padding:10, borderRadius:8, border:"1px solid #ccc" }}
            required
          >
            <option value="" disabled>Select a category</option>
            {Object.keys(CATEGORY_ITEMS).map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        {/* Item (depends on category) */}
        <div style={{ marginBottom: 12 }}>
          <label htmlFor="request_item" style={{ display: "block", marginBottom: 6 }}>
            Request Item *
          </label>
          <select
            id="request_item"
            name="request_item"
            value={form.request_item}
            onChange={handleChange}
            disabled={!form.request_category}
            style={{
              width:"100%", padding:10, borderRadius:8, border:"1px solid #ccc",
              background: form.request_category ? "white" : "#f5f5f5",
            }}
            required
          >
            <option value="" disabled>
              {form.request_category ? "Select an item" : "Choose a category first"}
            </option>
            {itemOptions.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </div>

        {/* Quantity */}
        <div style={{ marginBottom: 12 }}>
          <label htmlFor="request_quantity" style={{ display: "block", marginBottom: 6 }}>
            Quantity *
          </label>
          <input
            id="request_quantity"
            name="request_quantity"
            type="number"
            min={1}
            step={1}
            value={form.request_quantity}
            onChange={handleChange}
            style={{ width:"100%", padding:10, borderRadius:8, border:"1px solid #ccc" }}
            required
          />
        </div>

        {/* Location (when creating, read-only from state.cc; when editing, show existing) */}
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: "block", marginBottom: 6 }}>Location (Community Club)</label>
          <input
            type="text"
            value={editMode ? form.location : ccFromState}
            readOnly={true}
            onChange={(e) => editMode && setForm((f) => ({ ...f, location: e.target.value }))}
            style={{ width:"100%", padding:10, borderRadius:8, border:"1px solid #ccc", background: editMode ? "white" : "#f8f8f8" }}
          />
        </div>

        <button
          type="submit"
          disabled={!canSave}
          style={{
            padding:"10px 16px",
            borderRadius:10,
            background: saving ? "#666" : "#111",
            color:"#fff",
            border:0,
            cursor: saving ? "not-allowed" : "pointer",
          }}
        >
          {saving ? (editMode ? "Saving…" : "Submitting…") : (editMode ? "Save" : "Submit Request")}
        </button>
      </form>
    </div>
  );
}
