import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import mongoose from "mongoose";
import path from "path";
import { fileURLToPath } from "url";
import predictRoute from "./routes/predict.js";
import advisoryRoutes from "./routes/advisoryRoutes.mjs";


dotenv.config();
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// API Routes
app.use("/api/predict", predictRoute);
app.use("/api/advisory", advisoryRoutes);

// MongoDB connection
mongoose
  .connect(process.env.MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log("✅ MongoDB connected"))
  .catch((err) => console.error("MongoDB connection error:", err));

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
