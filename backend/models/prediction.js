import mongoose from "mongoose";

const predictionSchema = new mongoose.Schema({
  N: Number,
  P: Number,
  K: Number,
  temperature: Number,
  humidity: Number,
  ph: Number,
  rainfall: Number,
  predicted_crop: String,
  createdAt: { type: Date, default: Date.now },
});

export default mongoose.model("Prediction", predictionSchema);
