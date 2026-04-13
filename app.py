# app.py — ECO Track AI Backend (GET approach)
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os, json, base64, requests

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.environ.get("AIzaSyAfd0cNJYz-uyNH7Y7olyILALYZ40ILwGU"))
model = genai.GenerativeModel("gemini-1.5-flash")

WASTE_DB = {
  "plastic":   {"type":"PLASTIC",   "icon":"🧴", "bin":"Blue Recycling Bin",        "method":"Rinse and crush before disposal.",         "impact":"Saves fossil fuels and energy!",          "fact":"Plastic takes 350 years to decompose!"},
  "paper":    {"type":"PAPER",    "icon":"📄", "bin":"Blue Bin / Paper Bank",        "method":"Keep dry. Remove staples and tape.",          "impact":"Recycling paper saves trees!",              "fact":"1 ton of paper saves 17 trees!"},
  "glass":    {"type":"GLASS",    "icon":"🍶", "bin":"Green Glass Bin",             "method":"Rinse clean. Handle with care.",              "impact":"Glass is 100% recyclable forever!",           "fact":"Glass never wears out when recycled."},
  "metal":    {"type":"METAL",    "icon":"🥫", "bin":"Blue Recycling Bin",          "method":"Rinse cans. Flatten if possible.",            "impact":"Saves 95% energy vs new metal!",             "fact":"Aluminium recycles in just 60 days!"},
  "organic":  {"type":"ORGANIC",  "icon":"🍃", "bin":"Green Compost Bin",           "method":"Compost at home or use organic bin.",         "impact":"Creates fertiliser for plants!",              "fact":"Composting reduces methane emissions!"},
  "hazardous":{"type":"HAZARDOUS","icon":"☠️", "bin":"Hazardous Drop-off Point",     "method":"NEVER put in regular bin!",                  "impact":"Prevents toxic contamination!",               "fact":"Batteries poison 600k litres of water!"},
  "ewaste":   {"type":"E-WASTE",  "icon":"💻", "bin":"E-Waste Collection Point",     "method":"Take to certified e-waste centre.",          "impact":"Recovers precious metals safely!",            "fact":"E-waste has gold, silver and copper!"},
  "general":  {"type":"GENERAL",  "icon":"❓", "bin":"General Waste / Black Bin",    "method":"Check local disposal guidelines.",           "impact":"Aim to reduce general waste!",               "fact":"30% of bin waste could be composted!"},
}

PROMPT = """Look at this image and classify the waste into EXACTLY ONE category:
plastic, paper, glass, metal, organic, hazardous, ewaste, general

Definitions:
- plastic = bottles, bags, wrappers, straws, containers, packaging
- paper = newspaper, cardboard, books, receipts, magazines
- glass = bottles, jars, mirrors, broken glass
- metal = cans, aluminium foil, steel items, scrap metal
- organic = food scraps, fruit peels, vegetables, garden waste, leaves
- hazardous = batteries, chemicals, paint, syringes, medicines, pesticides
- ewaste = phones, laptops, chargers, cables, electronics, circuit boards
- general = mixed or unclear waste, anything that doesn't fit above

Reply with ONLY this JSON format. Nothing else:
{"category":"plastic","confidence":0.94}"""

@app.route("/classify", methods=["GET", "POST"])
def classify():
    # Try to get image data
    img_bytes = None
    
    # Method 1: Image file uploaded via POST
    if request.method == "POST" and "image" in request.files:
        img_bytes = request.files["image"].read()
    
    # Method 2: Base64 image in POST body
    elif request.method == "POST" and request.json and "image_base64" in request.json:
        img_bytes = base64.b64decode(request.json["image_base64"])
    
    # Method 3: GET request — use a test image to demo Gemini
    elif request.method == "GET":
        # For GET requests, we return a simulated result
        # This lets you test the full flow without image upload
        import random
        categories = list(WASTE_DB.keys())
        category = random.choice(categories)
        info = WASTE_DB[category].copy()
        info["confidence"] = f"{random.randint(82, 97)}%"
        info["note"] = "Demo mode - deploy with POST for real AI"
        return jsonify(info)
    
    if img_bytes is None:
        return jsonify({"error": "No image data received"}), 400

    try:
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        resp = model.generate_content([
            {"mime_type": "image/jpeg", "data": b64},
            PROMPT
        ])
        result = json.loads(resp.text.strip())
        category = result.get("category", "general").lower()
        confidence = result.get("confidence", 0.85)
        info = WASTE_DB.get(category, WASTE_DB["general"]).copy()
        info["confidence"] = f"{int(confidence * 100)}%"
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def health():
    return "ECO Track AI Backend is running! ♻️"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
