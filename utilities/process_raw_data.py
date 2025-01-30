from uuid import uuid4
import os
import shutil
import json

def main():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to the raw data directory
    raw_data_dir = os.path.join(current_dir, "..", "data", "raw")

    # Verify the path (good practice)
    if os.path.exists(raw_data_dir):
        # Look up metadata file in the raw data directory
        metadata_file = os.path.join(raw_data_dir, "metadata.json")
        # Check if the metadata file exists
        if os.path.exists(metadata_file):
            # Load the metadata file
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        print(f"Raw data directory: {raw_data_dir}")
        # Now you can use raw_data_dir to access your files
        for filename in os.listdir(raw_data_dir):
            # Check if the file is a text file
            if filename.endswith(".txt"):
                # Extract the patient number from the filename
                patient_number = filename.split("_")[0]
                # Create a new patient directory
                create_patient_directory(patient_number, metadata, filename, raw_data_dir)
        # Save the metadata file
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)
    else:
        print(f"Error: Raw data directory not found: {raw_data_dir}")

# Create a new patient directory
def create_patient_directory(patient_number: str, metadata: dict, file_name: str, file_path: os.path):
    if patient_number not in metadata:
        # create a uuid for the patient
        patient_id = str(uuid4())
        # Create a new directory for the patient
        patient_path = os.path.join(file_path, "..", "processed", patient_id)
        os.makedirs(patient_path)
        metadata[patient_number] = patient_id
    else:
        patient_path = os.path.join(file_path, "..", "processed", metadata[patient_number])

    # Move transcript file to the new directory
    if "trans" in file_name:
        shutil.copy(os.path.join(file_path, file_name), os.path.join(patient_path, "transcript.txt"))
    elif "hist" in file_name:
        shutil.copy(os.path.join(file_path, file_name), os.path.join(patient_path, "history.txt"))

if __name__ == "__main__":
    main()