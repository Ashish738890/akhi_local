import React, { useState } from "react";
import axios from "axios";

export default function Advisory() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const onFile = (e) => {
    const f = e.target.files?.[0];
    setImage(f || null);
    setResult(null);
    setError("");
    if (f) setPreview(URL.createObjectURL(f));
  };

  const detect = async () => {
    if (!image) return setError("Please select an image first.");
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const form = new FormData();
      form.append("image", image);
      const { data } = await axios.post("http://localhost:5000/api/advisory/pest-detect", form);
      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || "Detection failed. Please try again.");
      }
    } catch (e) {
      console.error("Detection error:", e);
      const errorMsg = e.response?.data?.error || e.response?.data?.details || e.message;
      setError(`Detection failed: ${errorMsg || "Please ensure backend and ML service are running."}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-6 space-y-4">
      <h1 className="text-3xl font-bold">🪲 Pest Detection (Advisory)</h1>

      <input type="file" accept="image/*" onChange={onFile} className="border p-2 w-full" />
      {preview && <img src={preview} alt="preview" className="rounded-lg shadow w-full" />}

      <button
        onClick={detect}
        disabled={loading}
        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-60"
      >
        {loading ? "Detecting..." : "Detect Pest"}
      </button>

      {error && <p className="text-red-600">{error}</p>}

      {result?.success && (
        <div className="p-4 border rounded-lg shadow">
          <p className="text-lg">
            Predicted Pest: <b>{result.pest}</b>
          </p>
          <p>Confidence: {result.confidence}%</p>
        </div>
      )}
    </div>
  );
}
