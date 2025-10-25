#!/bin/bash

SECRET="cb910f55ccc473356ed5eec6b3c77d7e3e70ec6fbe263e3ed767c4130"

curl -X POST "https://innovation-web-rho.vercel.app/api/pipeline/run-1761419288183-501/complete" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: $SECRET" \
  -d '{
    "status": "COMPLETED",
    "completedAt": "2025-10-25T19:11:11Z",
    "duration": 183000,
    "opportunities": [
      {"title": "Black Diamond Protein Cheese Bites", "markdown": "# Black Diamond\n\nHigh-protein cheese snacks"},
      {"title": "Lactalis Loop QR Recycling", "markdown": "# Lactalis Loop\n\nQR-based recycling program"},
      {"title": "Astro Local Farm-Fresh", "markdown": "# Astro Local\n\nLocal farm yogurt"},
      {"title": "Enjoy Plant-Based Smoothies", "markdown": "# Enjoy Smoothies\n\nPlant-based RTD beverages"},
      {"title": "Cheestrings Lactose-Free", "markdown": "# Cheestrings\n\nLactose-free kids snacks"}
    ],
    "stageOutputs": {}
  }'
