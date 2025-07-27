from fastapi import APIRouter, Query, UploadFile, File, HTTPException
from app.services.crop_disease import analyze_crop_disease
from app.db.firestore import firestore_service
import os
import uuid
from datetime import datetime
import base64

router = APIRouter()

@router.post("/upload-image")
async def upload_crop_image(image: UploadFile = File(...)):
    """
    Upload a crop image to Firestore and return the path for disease detection.
    
    Args:
        image: Image file uploaded from frontend
    
    Returns:
        JSON with the image path and metadata
    """
    try:
        # Validate file type
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        file_ext = os.path.splitext(image.filename)[1].lower()
        if file_ext not in valid_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid image format. Supported formats: {', '.join(valid_extensions)}"
            )
        
        # Read image data
        image_data = await image.read()
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"crop_image_{timestamp}_{unique_id}{file_ext}"
        
        # Create image metadata
        image_metadata = {
            "filename": filename,
            "original_filename": image.filename,
            "content_type": image.content_type,
            "file_size": len(image_data),
            "upload_timestamp": datetime.now().isoformat(),
            "image_data": base64.b64encode(image_data).decode('utf-8')  # Store as base64
        }
        
        # Store in Firestore
        doc_id = f"crop_images/{filename}"
        doc_ref = firestore_service.db.document(doc_id)
        doc_ref.set(image_metadata)
        
        # Create local file path for temporary storage (for crop disease detection)
        local_path = f"/tmp/{filename}"
        
        # Save image to local temp directory
        with open(local_path, "wb") as f:
            f.write(image_data)
        
        return {
            "status": "ok",
            "message": "Image uploaded successfully",
            "data": {
                "image_path": local_path,
                "firestore_path": doc_id,
                "filename": filename,
                "file_size": len(image_data),
                "content_type": image.content_type
            }
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Error uploading image: {str(e)}"
        }

@router.post("/analyze")
async def upload_and_analyze_crop_image(image: UploadFile = File(...)):
    """
    Upload a crop image and immediately perform disease detection analysis.
    
    Args:
        image: Image file uploaded from frontend
    
    Returns:
        JSON with both upload info and disease analysis results
    """
    try:
        # Validate file type
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        file_ext = os.path.splitext(image.filename)[1].lower()
        if file_ext not in valid_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid image format. Supported formats: {', '.join(valid_extensions)}"
            )
        
        # Read image data
        image_data = await image.read()
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"crop_image_{timestamp}_{unique_id}{file_ext}"
        
        # Create image metadata
        image_metadata = {
            "filename": filename,
            "original_filename": image.filename,
            "content_type": image.content_type,
            "file_size": len(image_data),
            "upload_timestamp": datetime.now().isoformat(),
            "image_data": base64.b64encode(image_data).decode('utf-8')  # Store as base64
        }
        
        # Store in Firestore
        doc_id = f"crop_images/{filename}"
        doc_ref = firestore_service.db.document(doc_id)
        doc_ref.set(image_metadata)
        
        # Create local file path for temporary storage
        local_path = f"/tmp/{filename}"
        
        # Save image to local temp directory
        with open(local_path, "wb") as f:
            f.write(image_data)
        
        # Perform disease detection
        disease_result = analyze_crop_disease(local_path)
        
        # Clean up temporary file
        try:
            os.remove(local_path)
        except:
            pass  # Ignore cleanup errors
        
        if disease_result:
            return {
                "status": "ok",
                "message": "Image uploaded and disease analysis completed successfully",
                "data": {
                    "upload_info": {
                        "image_path": local_path,
                        "firestore_path": doc_id,
                        "filename": filename,
                        "file_size": len(image_data),
                        "content_type": image.content_type
                    },
                    "analysis": {
                        "disease": {
                            "name": disease_result["disease"]["disease_name"],
                            "severity": disease_result["disease"]["severity"]
                        },
                        "remedy": {
                            "steps": disease_result["remedy"]["remedy_steps"],
                            "recheck_days": disease_result["remedy"]["recheck_days"],
                            "estimated_cost": disease_result["remedy"]["estimated_cost"]
                        }
                    }
                }
            }
        else:
            return {
                "status": "partial_success",
                "message": "Image uploaded successfully but disease analysis failed",
                "data": {
                    "upload_info": {
                        "image_path": local_path,
                        "firestore_path": doc_id,
                        "filename": filename,
                        "file_size": len(image_data),
                        "content_type": image.content_type
                    },
                    "analysis": None,
                    "error": "Failed to analyze crop disease. Please try again."
                }
            }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Error processing image: {str(e)}"
        }

@router.get("/detect")
async def detect_crop_disease(image_path: str = Query(..., description="Path to the crop image file")):
    """
    Detect crop disease from an image and provide remedy information.
    
    Args:
        image_path: Path to the image file (e.g., "/path/to/crop_image.jpg")
    
    Returns:
        JSON with disease detection and remedy information
    """
    try:
        # Validate image path
        if not image_path:
            return {
                "status": "failed",
                "error": "Image path is required"
            }
        
        # Check if file exists
        if not os.path.exists(image_path):
            return {
                "status": "failed",
                "error": f"Image file not found: {image_path}"
            }
        
        # Check if it's a valid image file
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in valid_extensions:
            return {
                "status": "failed",
                "error": f"Invalid image format. Supported formats: {', '.join(valid_extensions)}"
            }
        
        # Analyze crop disease
        result = analyze_crop_disease(image_path)
        
        if result:
            return {
                "status": "ok",
                "message": "Crop disease analysis completed successfully",
                "data": {
                    "disease": {
                        "name": result["disease"]["disease_name"],
                        "severity": result["disease"]["severity"]
                    },
                    "remedy": {
                        "steps": result["remedy"]["remedy_steps"],
                        "recheck_days": result["remedy"]["recheck_days"],
                        "estimated_cost": result["remedy"]["estimated_cost"]
                    }
                }
            }
        else:
            return {
                "status": "failed",
                "error": "Failed to analyze crop disease. Please check the image and try again."
            }
            
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Error processing crop disease analysis: {str(e)}"
        }

@router.get("/health")
async def health_check():
    """
    Health check endpoint for crop disease service
    """
    return {
        "status": "ok",
        "service": "crop-disease",
        "message": "Crop disease detection service is running"
    } 