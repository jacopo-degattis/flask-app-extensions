import os
import base64
import requests

MAIN_REPO = "https://api.github.com/repos/jacopo-degattis/ftext/contents/"

# TODO: add caching for repo response
def list_extensions():

    to_encode = f"{os.environ.get('GIT_USER')}:{os.environ.get('GIT_TOKEN')}".encode()
    encoded_auth = base64.b64encode(to_encode).decode()

    response = requests.get(MAIN_REPO, headers={
        "Authorization": f"Basic {encoded_auth}"
    })

    if response.status_code != 200:
        print("ERROR: github api returned a %d as status code" % response.status_code)

    json_content = response.json()

    
    index = 1
    for item in json_content:
        if item['type'] == 'dir':
            print(f"  {index}) {item['name']}")
            index += 1

    return json_content

def download_extension(index, extensions):
    extension_name = extensions[index-1]

    download_uri = MAIN_REPO + extension_name

if __name__ == "__main__":

    if not os.environ.get("GIT_USER") or not os.environ.get("GIT_TOKEN"):
        print("ERROR: GIT_USER or GIT_TOKEN has not been provided as ENV variable")
        exit(1)

    print("** Avaiable extensions for flask-template-extensions")

    extensions = list_extensions()
    choice = int(input("Choose an extension and input here the corresponding number: "))

    if choice > len(extensions) or choice < 0:
        print("ERROR: Invalid extensions index provided")
        exit(1)

    
