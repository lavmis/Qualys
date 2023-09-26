import requests
import base64

# Set Qualys API credentials
qualys_username = "xxxxx"  # Enter your Qualys API username
qualys_password = "xxxxx"  # Enter your Qualys API password

# Encode the credentials
encoded_credentials = base64.b64encode(f"{qualys_username}:{qualys_password}".encode()).decode()

# Prompt the user for asset_group_ids and output file path
asset_group_ids = input("Enter the asset_group_ids value (comma-separated if multiple): ")
output_file_path = input("Enter the path where you want to save the downloaded report (e.g., report.csv): ")

# Set API endpoint and parameters for launching the report
api_endpoint = "https://qualysapi.qualys.com/api/2.0/fo/report/"
query_params = {
    "action": "launch",
    "template_id": "123456",  # Replace with the correct template ID
    "output_format": "csv",
    "asset_group_ids": asset_group_ids,
}

# Create the headers with Basic authentication
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "X-Requested-With": "QualysPostman",
}

try:
    # Make the API request and get the XML response
    response = requests.post(api_endpoint, params=query_params, headers=headers)
    xml_response = response.text
    print(xml_response)

    # Extract the report ID from the XML response
    report_id = xml_response.split("<VALUE>")[1].split("</VALUE>")[0]

    if report_id:
        print(f"Report launched. Report ID: {report_id}")

        # Wait for the report to finish (up to 10 minutes with 10 seconds interval)
        max_retries = 10000
        retry_interval = 10

        for i in range(1, max_retries + 1):
            import time
            time.sleep(retry_interval)

            # Get the report status
            status_endpoint = "https://qualysapi.qualys.com/api/2.0/fo/report/"
            status_params = {"action": "list", "id": report_id}

            status_response = requests.get(status_endpoint, params=status_params, headers=headers)
            status = status_response.text.split("<STATE>")[1].split("</STATE>")[0]

            if status == "Finished":
                print("Report is finished. Downloading the report...")

                # Download the report
                download_endpoint = "https://qualysapi.qualys.com/api/2.0/fo/report/"
                download_params = {"action": "fetch", "id": report_id}

                # Make the API request to download the report
                download_response = requests.get(download_endpoint, params=download_params, headers=headers)

                # Save the downloaded report to the user-provided file path
                with open(output_file_path, "wb") as f:
                    f.write(download_response.content)

                print(f"Report downloaded and saved to: {output_file_path}")
                break
            else:
                print(f"Report is still in progress. Checking again in {retry_interval} seconds...")
    else:
        print("Failed to launch the scan report.")
except Exception as e:
    print(f"Error occurred: {e}")
