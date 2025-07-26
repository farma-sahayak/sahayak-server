from __future__ import annotations

from google import genai
from google.genai import types
from PIL import Image
from typing import TypedDict, Optional
import google.generativeai as genai
import google.auth
import os

# Initialize Gemini client
client = genai.Client(
    vertexai=True, project="sahayak-ai-466508", location="global",
)

# Define the expected structure of the response
class Disease(TypedDict):
    disease_name: str
    severity: str

class Remedy(TypedDict):
    remedy_steps: str
    recheck_days: int
    estimated_cost: int

class DiseaseAnalysis(TypedDict):
    disease: Disease
    remedy: Remedy

def detect_disease_from_image(image_path: str) -> Optional[Disease]:
    """
    Detects plant disease from an image using Gemini.
    Returns a dictionary with disease_name and severity.
    """
    # Check if image file exists
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return None

    # Load image using PIL
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return None

    # Construct prompt
    prompt = f"""
    Analyze the following image of a crop and identify any diseases or health issues.

    Respond in JSON with:
    - disease_name: The name of the disease or "Healthy" if no disease detected
    - severity: low, medium, high, or "none" if healthy
    """

    # Call Gemini model with structured response config
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[prompt, image],
            config={
                "response_mime_type": "application/json",
                "response_schema": Disease,
            },
        )
        return response.parsed  # Return the parsed dictionary
    except Exception as e:
        print(f"❌ Gemini API call failed: {e}")
        return None

def get_remedy_for_disease(disease_name: str, severity: str) -> Optional[Remedy]:
    """
    Given disease name and severity, return structured remedy guidance.
    """
    prompt = f"""
    The crop is infected with "{disease_name}" and severity is "{severity}".

    Please respond in JSON with:
    - remedy_steps: 1-3 actionable bullet points for treatment
    - recheck_days: number of days to recheck the crop
    - estimated_cost: estimated cost in Indian Rupees (₹)
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": Remedy,
            },
        )
        return response.parsed  # Return the parsed dictionary
    except Exception as e:
        print(f"❌ Gemini API call failed: {e}")
        return None

def analyze_crop_disease(image_path: str) -> Optional[DiseaseAnalysis]:
    """
    Complete crop disease analysis: detects disease and provides remedy.
    Returns a dictionary with both disease and remedy information.
    """
    try:
        # Detect disease from image
        disease_result = detect_disease_from_image(image_path)
        if not disease_result:
            return None
        
        # Get remedy for the detected disease
        remedy_result = get_remedy_for_disease(
            disease_result['disease_name'], 
            disease_result['severity']
        )
        
        if not remedy_result:
            return None
        
        # Combine results
        return {
            "disease": disease_result,
            "remedy": remedy_result
        }
        
    except Exception as e:
        print(f"❌ Error in crop disease analysis: {e}")
        return None

# Example usage (for testing)
if __name__ == "__main__":
    result = analyze_crop_disease("plant_disease.jpg")
    if result:
        print(f"🦠 Disease: {result['disease']['disease_name']}")
        print(f"📉 Severity: {result['disease']['severity']}")
        print(f"💊 Remedy: {result['remedy']['remedy_steps']}")
        print(f"📅 Recheck in: {result['remedy']['recheck_days']} days")
        print(f"💰 Estimated cost: ₹{result['remedy']['estimated_cost']}")
    else:
        print("❌ Failed to analyze crop disease")