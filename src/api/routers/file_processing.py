import numpy as np

from fastapi import APIRouter, HTTPException

from pydantic import BaseModel, model_validator

from api.processing.read_ranges import SWIFTProcessor, get_dataset_alias_map

router = APIRouter()

dataset_map = get_dataset_alias_map()

class SWIFTDataSpec(BaseModel):
    alias: str | None = None
    filename: str | None = None
    mask: None | np.ndarray = None
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
    if data_spec.alias:
        file_path = processor.retrieve_filename(data_spec.alias)
    elif data_spec.file_path:
        file_path = data_spec.file_path
    
    if file_path == None:
        raise 

    

@router.get("/unmasked_dataset")
async def get_unmasked_array_data():
    return {
        "data": "A test user"
    }