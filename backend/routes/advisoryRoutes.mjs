import express from "express";
import multer from "multer";
import fs from "fs";
import axios from "axios";
import FormData from "form-data";

const router = express.Router();
const upload = multer({ dest: "uploads/" });

router.post("/pest-detect", upload.single("image"), async (req, res) => {
  try {
    if (!req.file) {
      console.error("❌ No file received from frontend");
      return res.status(400).json({ success: false, error: "Image file missing" });
    }

    const form = new FormData();
    form.append("file", fs.createReadStream(req.file.path));

    console.log("📤 Sending file to Flask API...");
    const { data } = await axios.post("http://127.0.0.1:5001/predict-pest", form, {
      headers: form.getHeaders(),
      maxBodyLength: Infinity,
    });

    console.log("✅ Flask response:", data);

    fs.unlink(req.file.path, () => {});
    return res.json(data);
  } catch (err) {
    console.error("🔥 Pest detect error:", err.response?.data || err.message);
    return res.status(500).json({
      success: false,
      error: "Backend failed",
      details: err.response?.data || err.message,
    });
  }
});

export default router;
