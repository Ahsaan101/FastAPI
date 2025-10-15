from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json
app = FastAPI()


class Patient(BaseModel):
    id: Annotated[str, Field(..., description="ID of the patient", example="P001")]
    name: Annotated[str, Field(..., description="Name of the patient", example="John Doe")]
    city: Annotated[str, Field(..., description="City of the patient", example="Islamabad")]
    age: Annotated[int, Field(..., gt=0, lt=120, example=30)]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description="Gender of the patient")]
    height: Annotated[float, Field(..., gt=0, description="Height of the patient in mtrs", example=1.75)]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the patient in kgs", example=70.0)]


    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        bmi = self.bmi
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default = None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

#A function to load patient data from a JSON file
def load_data():
    with open("patients.json","r") as f:
        data = json.load(f)
    return data

#A function to save patient data to a JSON file
def save_data(data):
    with open("patients.json","w") as f:
        json.dump(data, f)


# Basic endpoint to check if the API is working
@app.get("/")
def hello():
    return {"message": "Welcome to Patient Management API"}

# Endpoint to provide information about the API
@app.get("/about")
def about():
    return {"message": "A fully functional API to manage patient information."}

# Endpoint to view all patient data
@app.get("/view_all")
def view_all():
    data = load_data()
    return data

# Endpoint to view a specific patient's data by their PatientID
@app.get("/view_patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description = "ID of the patient to view", example = "P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code=404, detail="Patient not found")

# Endpoint to sort patients based on height, weight, or BMI and order (ascending or descending)
@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):
    fields = ['height', 'weight', 'bmi']
    orders = ['asc', 'desc']

    sort_by = sort_by.lower()
    order = order.lower()
    if sort_by not in fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by field. Must be one of {fields}")
    if order not in orders:
        raise HTTPException(status_code=400, detail=f"Invalid order. Must be one of {orders}")
    
    data = load_data()
    sorted_data = sorted(data.values(), key=lambda x: x[sort_by], reverse=(order=='desc'))
    return sorted_data

# Endpoint to create patients
@app.post("/create_patient")
def create_patient(patient: Patient):
    #Load existing data
    data = load_data()

    #Checking if patient with same ID already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    
    # to convert Pydantic model to dictionary
    patient_dict = patient.model_dump(exclude=['id'])
    data[patient.id] = patient_dict

    #Save updated data
    save_data(data)

    return JSONResponse(status_code=201, content={"message": "Patient created successfully", "patient": data[patient.id]})

# Endpoint to update patient data
@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    #-> dict -> pydantic object
    existing_patient_info['id'] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)

    #-> pydantic object -> dict
    existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)
    
    # return response
    return JSONResponse(status_code=200, content={'message':'patient updated Successfully'})


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    # load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient deleted Successfully'})
