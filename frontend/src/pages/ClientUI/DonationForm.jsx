import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import httpClient from "../../httpClient";

const CATEGORY_ITEMS = {
  Food:["Rice","Noodles","Bread","Canned goods","Biscuits & crackers","Cereals & oats","Cooking oil","Flour","Sugar","Soy sauce","Chili sauce","Salt","Pepper"],
  Drinks:["Bottled water","Packet drinks","Instant coffee / Tea sachets","Milk powder","UHT milk cartons","Canned drinks"],
  Furnitures:["Chairs","Tables","Shelves","Cabinets","Beds","Baby cots","Sofas"],
  Electronics:["Mobile phones","Tablets","Laptops","Kettles","Rice cookers","Blenders","Toasters","Fans","Irons","Light bulbs","Extension cords","TVs","Radios"],
  Essentials:["Soap","Shampoo","Toothpaste","Toothbrushes","Sanitary pads","Detergent","Toilet paper","Masks","Hand sanitizers","First aid basics"],
};

export default function DonationForm() {
  const { id } = useParams();                 // if present, we are editing
  const editMode = Boolean(id);
  const navigate = useNavigate();
  const locationHook = useLocation();
  const ccFromState = locationHook?.state?.cc || "";   // used on create

  const [email, setEmail] = useState("");
  const [authChecking, setAuthChecking] = useState(true);
  const [loading, setLoading] = useState(editMode);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [previewUrl, setPreviewUrl] = useState("");

  const [form, setForm] = useState({
    donation_category: "",
    donation_item: "",
    donation_quantity: 1,
    expiryDate: "",          // required when Food/Drinks
    image_file: null,        // required on create, optional on edit
    image_link: "",          // for showing existing image when editing
    status: "Pending",       // only meaningful on edit
    location: ccFromState,   // will be overwritten by API when editing
  });

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

  // 2) If editing, fetch donation details
  useEffect(() => {
    if (!editMode) return;
    (async () => {
      try {
        const resp = await httpClient.get(`/api/donations/${id}`);
        setForm({
          donation_category: resp.data.donation_category,
          donation_item: resp.data.donation_item,
          donation_quantity: resp.data.donation_quantity,
          expiryDate: resp.data.expiryDate || "",
          image_file: null,
          image_link: resp.data.image_link || "",
          status: resp.data.status,
          location: resp.data.location || ccFromState,
        });
      } catch (e) {
        setError(e?.response?.data?.message || "Failed to load donation.");
      } finally {
        setLoading(false);
      }
    })();
  }, [editMode, id, ccFromState]);

  const needsExpiry = form.donation_category === "Food" || form.donation_category === "Drinks";
  const itemOptions = useMemo(
    () => (form.donation_category ? CATEGORY_ITEMS[form.donation_category] || [] : []),
    [form.donation_category]
  );

  // reset item when category changes
  useEffect(() => {
    setForm((f) => ({ ...f, donation_item: "" }));
  }, [form.donation_category]);

  // cleanup preview URL
  useEffect(() => {
    return () => { if (previewUrl) URL.revokeObjectURL(previewUrl); };
  }, [previewUrl]);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((f) => ({
      ...f,
      [name]: name === "donation_quantity" ? Number(value) : value,
    }));
  }

  function handleImageChange(e) {
    const file = e.target.files?.[0] || null;
    setForm((f) => ({ ...f, image_file: file }));
    setError("");

    if (file) {
      if (!file.type.startsWith("image/")) {
        setError("Please select a valid image file.");
        setPreviewUrl("");
        return;
      }
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl("");
    }
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError("");

    // Validate fields
    const locationToUse = editMode ? form.location : ccFromState;
    if (!locationToUse) return setError("Missing location (CC). Please select a Community Club first.");
    if (!form.donation_category) return setError("Choose a donation category.");
    if (!form.donation_item) return setError("Choose a donation item.");
    if (!form.donation_quantity || form.donation_quantity < 1) return setError("Quantity must be at least 1.");
    if (needsExpiry && !form.expiryDate) return setError("Please provide an expiry date.");
    if (!editMode && !form.image_file) return setError("Please upload an image.");

    try {
      setSubmitting(true);

      // Use FormData so we can include an image for both create + edit
      const fd = new FormData();
      fd.append("donation_category", form.donation_category);
      fd.append("donation_item", form.donation_item);
      fd.append("donation_quantity", String(form.donation_quantity));
      fd.append("location", locationToUse);
      if (needsExpiry) fd.append("expiryDate", form.expiryDate);
      if (form.image_file) fd.append("image", form.image_file); // optional on edit

      if (editMode) {
        await httpClient.patch(`/api/donations/${id}`, fd, { headers: { "Content-Type": "multipart/form-data" }});
        alert("Donation updated!");
      } else {
        await httpClient.post("/api/donations", fd, { headers: { "Content-Type": "multipart/form-data" }});
        alert("Donation created!");
      }

      // reset & go back
      setForm({
        donation_category: "",
        donation_item: "",
        donation_quantity: 1,
        expiryDate: "",
        image_file: null,
        image_link: "",
        status: "Pending",
        location: locationToUse,
      });
      setPreviewUrl("");
      navigate("/myDonations");
    } catch (e) {
      setError(
        e?.response?.data?.message ||
          (editMode ? "Failed to update donation." : "Failed to create donation.")
      );
    } finally {
      setSubmitting(false);
    }
  }

  const todayStr = new Date().toISOString().slice(0, 10);

  if (authChecking) return <div style={{ padding: 16 }}>Checking authentication…</div>;
  if (loading) return <div style={{ padding: 16 }}>Loading…</div>;

  return (
    <div style={{ maxWidth: 720, margin: "2rem auto", padding: 16 }}>
      <h1 style={{ marginBottom: 8 }}>{editMode ? "Edit Donation" : "Donate an Item"}</h1>
      <p style={{ color: "#555", marginBottom: 16 }}>
        {editMode ? "Update your donation." : "Fill out the form to list your donation."}
      </p>

      <div style={{ color: "#666", marginBottom: 12 }}>{email}</div>

      {editMode && form.status !== "Pending" && (
        <div style={{ background:"#fff7e6", border:"1px solid #ffe0b3", color:"#8a5300", padding:12, borderRadius:8, marginBottom:12 }}>
          Only <strong>Pending</strong> donations can be edited. Current status: <strong>{form.status}</strong>.
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
          <label htmlFor="donation_category" style={{ display:"block", marginBottom:6 }}>Donation Category *</label>
          <select
            id="donation_category"
            name="donation_category"
            value={form.donation_category}
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
          <label htmlFor="donation_item" style={{ display:"block", marginBottom:6 }}>Donation Item *</label>
          <select
            id="donation_item"
            name="donation_item"
            value={form.donation_item}
            onChange={handleChange}
            disabled={!form.donation_category}
            style={{
              width:"100%", padding:10, borderRadius:8, border:"1px solid #ccc",
              background: form.donation_category ? "white" : "#f5f5f5",
            }}
            required
          >
            <option value="" disabled>
              {form.donation_category ? "Select an item" : "Choose a category first"}
            </option>
            {itemOptions.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </div>

        {/* Quantity */}
        <div style={{ marginBottom: 12 }}>
          <label htmlFor="donation_quantity" style={{ display:"block", marginBottom:6 }}>Quantity *</label>
          <input
            id="donation_quantity"
            name="donation_quantity"
            type="number"
            min={1}
            step={1}
            value={form.donation_quantity}
            onChange={handleChange}
            style={{ width:"100%", padding:10, borderRadius:8, border:"1px solid #ccc" }}
            required
          />
        </div>

        {/* Location */}
        <div style={{ marginBottom: 16 }}>
          <label style={{ display:"block", marginBottom:6 }}>Location (Community Club)</label>
          <input
            type="text"
            value={editMode ? form.location : ccFromState}
            readOnly={true}
            onChange={(e) => editMode && setForm((f) => ({ ...f, location: e.target.value }))}
            style={{ width:"100%", padding:10, borderRadius:8, border:"1px solid #ccc", background: editMode ? "white" : "#f8f8f8" }}
          />
        </div>
        
        {/* Expiry (Food/Drinks only) */}
        {(form.donation_category === "Food" || form.donation_category === "Drinks") && (
          <div style={{ marginBottom: 16 }}>
            <label htmlFor="expiryDate" style={{ display:"block", marginBottom:6 }}>Expiry Date *</label>
            <input
              id="expiryDate"
              name="expiryDate"
              type="date"
              min={todayStr}
              value={form.expiryDate}
              onChange={handleChange}
              style={{ width:"100%", padding:10, borderRadius:8, border:"1px solid #ccc" }}
              required
            />
            <div style={{ fontSize: 12, color: "#666", marginTop: 4 }}>
              Required for Food and Drinks.
            </div>
          </div>
        )}

        {/* Image (required on create, optional on edit) */}
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="image" style={{ display:"block", marginBottom:6 }}>
            {editMode ? "Replace Image (optional)" : "Image *"}
          </label>
          <input id="image" name="image" type="file" accept="image/*" onChange={handleImageChange} />
          {(previewUrl || form.image_link) && (
            <div style={{ marginTop: 8 }}>
              <div style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>Preview</div>
              <img
                src={previewUrl || form.image_link}
                alt="Preview"
                style={{ maxHeight: 220, borderRadius: 8, border: "1px solid #eee", objectFit: "contain" }}
              />
            </div>
          )}
        </div>

        <div style={{ display:"flex", gap:8 }}>
          <button
            type="submit"
            disabled={submitting || (editMode && form.status !== "Pending")}
            style={{
              padding:"10px 16px",
              borderRadius:10,
              background: submitting ? "#666" : "#111",
              color:"white",
              border:0,
              cursor: submitting ? "not-allowed" : "pointer",
            }}
          >
            {submitting ? (editMode ? "Saving…" : "Submitting…") : (editMode ? "Save" : "Submit Donation")}
          </button>

          <button
            type="button"
            onClick={() => {
              setForm((f) => ({
                ...f,
                donation_item: "",
                donation_quantity: 1,
                expiryDate: "",
                image_file: null,
              }));
              setPreviewUrl("");
              setError("");
            }}
            style={{ padding:"10px 16px", borderRadius:10, border:"1px solid #ccc", background:"white" }}
          >
            Reset
          </button>
        </div>
      </form>
    </div>
  );
}
