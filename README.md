# Plant Disease Detection App

This is a full-stack web application that uses a deep learning model to detect 38 different plant diseases from uploaded images.

## How to Run Locally (On any PC)

If you have downloaded or transferred these files to a new computer, follow these simple steps to get the app running:

### Prerequisites
1. **Python**: Make sure Python (version 3.9 - 3.11 is recommended) is installed. You can download it from [python.org](https://www.python.org/downloads/).
   - *Important:* When installing Python on Windows, make sure to check the box **"Add Python to PATH"** at the bottom of the installer.

### Setup Instructions

1. **Open Terminal / Command Prompt**
   Open a terminal and navigate to this folder.
   ```bash
   cd path/to/this/folder
   ```

2. **Create a Virtual Environment (Recommended but optional)**
   It's best practice to create a virtual environment to avoid interfering with other Python projects.
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - On **Mac/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install Required Libraries**
   Install all the necessary dependencies using the `requirements.txt` file.
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**
   Start the Flask backend server.
   ```bash
   python app.py
   ```

6. **Open the App**
   Once the server is running, open your web browser and go to:
   ```
   http://127.0.0.1:5000
   ```
   
You can now upload a picture of a leaf, and the AI will analyze it!
