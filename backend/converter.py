import cloudconvert
import os
import io
import requests
from dotenv import load_dotenv

load_dotenv()

class CloudConvertService:
    def __init__(self):
        self.api_key = os.getenv("CLOUDCONVERT_API_KEY")
        if not self.api_key or self.api_key == "your_api_key_here":
            print("WARNING: CLOUDCONVERT_API_KEY is not set or is a placeholder.")
            self.configured = False
        else:
            print(f"DEBUG: Loading CloudConvert API Key: {self.api_key[:10]}...")
            cloudconvert.configure(api_key=self.api_key)
            self.configured = True

    def convert_to_pdf(self, input_file_path: str, output_dir: str) -> str:
        """
        Converts a file to PDF using CloudConvert.
        Returns the path to the converted PDF file.
        """
        if not self.configured:
            raise Exception("CloudConvert not configured. Check your API key.")

        filename = os.path.basename(input_file_path)
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}.pdf"
        output_path = os.path.join(output_dir, output_filename)

        print(f"Converting {filename} to PDF...")
        
        try:
            # Create a conversion job
            job = cloudconvert.Job.create(payload={
                "tasks": {
                    "import-my-file": {
                        "operation": "import/upload"
                    },
                    "convert-my-file": {
                        "operation": "convert",
                        "input": "import-my-file",
                        "output_format": "pdf"
                    },
                    "export-my-file": {
                        "operation": "export/url",
                        "input": "convert-my-file"
                    }
                }
            })

            # Upload the file
            upload_task = [t for t in job["tasks"] if t["name"] == "import-my-file"][0]
            cloudconvert.Task.upload(file_name=input_file_path, task=upload_task)

            # Wait for the job to finish
            job = cloudconvert.Job.wait(job["id"])

            # Download the converted file
            export_task = [t for t in job["tasks"] if t["name"] == "export-my-file"][0]
            file_info = export_task["result"]["files"][0]
            
            # Use requests to download the file as CloudConvert SDK doesn't support Task.download()
            print(f"Downloading converted PDF from {file_info['url']}...")
            response = requests.get(file_info["url"])
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"Conversion successful: {output_path}")
                return output_path
            else:
                raise Exception(f"Failed to download converted file: {response.status_code}")

        except Exception as e:
            print(f"CloudConvert error: {e}")
            raise e
