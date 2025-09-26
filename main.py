from fastapi import FastAPI, Path, HTTPException, Query
import json
app = FastAPI()

def load_data():
    with open("patients.json","r") as f:
        data = json.load(f)
    return data


@app.get("/")
def hello():
    return {"message": "Welcome to Patient Management API"}

@app.get("/about")
def about():
    return {"message": "A fully functional API to manage patient information."}

@app.get("/view_all")
def view_all():
    data = load_data()
    return data


@app.get("/view_patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description = "ID of the patient to view", example = "P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code=404, detail="Patient not found")


@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):
    valid_fields = ['height', 'weight', 'bmi']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by field. Must be one of {valid_fields}")
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid order. Must be 'asc' or 'desc'")
    
    data = load_data()
    sorted_data = sorted(data.values(), key=lambda x: x[sort_by], reverse=(order=='desc'))
    return sorted_data
