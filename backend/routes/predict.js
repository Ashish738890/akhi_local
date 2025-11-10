import express from "express";
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";
import Prediction from "../models/Prediction.js";

const router = express.Router();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

router.post("/", async (req, res) => {
  const pythonScriptPath = path.join(__dirname, "..", "..", "ml-model", "predict.py");
  const python = spawn("python", [pythonScriptPath]);

  let output = "", error = "";

  python.stdout.on("data", (data) => (output += data.toString()));
  python.stderr.on("data", (data) => (error += data.toString()));

  python.on("close", async (code) => {
    if (error) console.error("Python error:", error);

    try {
      const result = JSON.parse(output);
      if (result.error) return res.status(500).json(result);

      // 💾 Save to MongoDB
      const saved = new Prediction({ ...req.body, predicted_crop: result.predicted_crop });
      await saved.save();

      res.json(result);
    } catch (e) {
      console.error("JSON parse error:", output);
      res.status(500).json({ error: "Invalid JSON from Python script" });
    }
  });

  python.stdin.write(JSON.stringify(req.body));
  python.stdin.end();
});

export default router;
