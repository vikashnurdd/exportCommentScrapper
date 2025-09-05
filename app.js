// server.js
const express = require("express");
const bodyParser = require("body-parser");
const { spawn } = require("child_process");

const app = express();
app.use(bodyParser.json());

// POST endpoint
app.post("/api/scrape", (req, res) => {
    console.log("Received request:", req.body);
  const { url } = req.body;
  if (!url) return res.status(400).json({ error: "URL is required" });

  const py = spawn("python", ["scraper.py", url]);
  let data = "";
  py.stdout.on("data", (chunk) => {
    data += chunk.toString();
  });
  let errorData = "";
  py.stderr.on("data", (chunk) => {
    errorData += chunk.toString();
  });

  py.on("close", (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: "Python script failed", details: errorData });
    }
    try {
      const result = JSON.parse(data);
      res.json(result);
    } catch (err) {
      res.status(500).json({ error: "Invalid JSON from Python", raw: data });
    }
  });
});

app.listen(5000, () => {
  console.log("🚀 Server running on http://localhost:5000");
});
