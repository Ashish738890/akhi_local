import axios from "axios";

export const getCropRecommendation = async (req, res) => {
  try {
    const { N, P, K, temperature, humidity, ph, rainfall } = req.body;

    const response = await axios.post("http://127.0.0.1:5001/predict", {
      N, P, K, temperature, humidity, ph, rainfall
    });

    res.json({
      success: true,
      crop: response.data.recommended_crop
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
};
