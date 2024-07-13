import requests
from bs4 import BeautifulSoup

def get_link(file_path):
    url = "https://nostr.build/upload.php"
    with open(file_path, "rb") as file:
        if file_path.lower().endswith(".jpg"):
            content_type = "image/jpeg"
        elif file_path.lower().endswith(".mp4"):
            content_type = "video/mp4"
            print(1)
        else:
            raise ValueError("Unsupported file format")

        files = {"fileToUpload": (file_path, file, content_type)}

        response = requests.post(url, files=files)
        
        soup = BeautifulSoup(response.content, "html.parser")

        the_list_element = soup.find(id="theList")
        if the_list_element:
            the_list_text = the_list_element.get_text()
            print(the_list_text)
            return the_list_text
        else:
            print("Element with id 'theList' not found in the response.")


