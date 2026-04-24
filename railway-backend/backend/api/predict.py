import io, os, uuid
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import get_db
from backend.db.models import Prediction
from backend.core.security import get_current_user
from backend.schemas.schemas import PredictRequest, PredictResponse
from backend.core.config import get_settings
from ml.predict import predict_single, predict_batch

router = APIRouter(tags=["predict"])

@router.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest,
                  user_id: str = Depends(get_current_user),
                  db: AsyncSession = Depends(get_db)):
    result = predict_single(req.model_dump())
    record = Prediction(user_id=int(user_id), input_data=req.model_dump(),
                        churn=result["churn"], probability=result["probability"])
    db.add(record)
    await db.commit()
    return result

@router.post("/batch_predict")
async def batch_predict(file: UploadFile = File(...),
                        user_id: str = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files accepted")
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(400, f"Invalid CSV: {e}")

    result_df = predict_batch(df)

    # Save output file
    s = get_settings()
    os.makedirs(s.STORAGE_DIR, exist_ok=True)
    fname = f"{uuid.uuid4().hex}_results.csv"
    fpath = os.path.join(s.STORAGE_DIR, fname)
    result_df.to_csv(fpath, index=False)

    record = Prediction(user_id=int(user_id), batch_file=fname,
                        churn=None, probability=None)
    db.add(record)
    await db.commit()

    buf = io.StringIO()
    result_df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(buf, media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={fname}"})
