import numpy as np

from fastapi import APIRouter, HTTPException, status

from pydantic import BaseModel, model_validator

from api.processing.read_ranges import SWIFTProcessor, get_dataset_alias_map
import json

router = APIRouter()

dataset_map = get_dataset_alias_map()


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class SWIFTDataSpec(BaseModel):
    alias: str | None = None
    filename: str | None = None
    mask: None | str = None
    mask_size:  None | int = None
    columns: None | list[list[int]] = None

class SWIFTDataSpecException(HTTPException):
    def __init__(self, status_code: int, detail: str | None = None):
        if not detail:
            detail = "Error validating SWIFT particle dataset specification provided."
        super().__init__(status_code, detail = detail)


@router.post("/remote_data")
async def get_masked_array_data(data_spec: SWIFTDataSpec):

    processor = SWIFTProcessor(dataset_map)
    
    file_path = None

    if data_spec.filename:
        file_path = data_spec.filename
    else:
        file_path = processor.retrieve_filename(data_spec.alias)

    
    if file_path == None:
        raise SWIFTDataSpecException(status_code=status.HTTP_400_BAD_REQUEST, detail="SWIFT filename or file alias not found.")
    

    # retrieved filename, now call helper functions which load data
    

    

@router.get("/unmasked_dataset")
async def get_unmasked_array_data():
    return {
        "data": "A test user"
    }