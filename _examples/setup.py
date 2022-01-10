#!/usr/bin/env python3

import os
import base64
import requests
from distutils.dir_util import copy_tree

ROOT_PATH = ".tmp/"
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

    
    # NOTE: folder starting with '_' will be ignored by CLI

    index = 1
    for item in json_content:
        if item['type'] == 'dir' and not item['name'].startswith("_"):
            print(f"  {index}) {item['name']}")
            index += 1

    return json_content

def handle_dir(resource, library):
    
    if not os.path.isdir(f"{ROOT_PATH}{library}/{resource['name']}"):
        os.mkdir(f"{ROOT_PATH}{library}/{resource['name']}")

    response = requests.get(resource['url'])
    
    if response.status_code != 200:
        print("ERROR: Error while fetching uri")
    
    next_resources = response.json()
    
    for res in next_resources:
        download_resource(res, library)

def handle_blob(resource, library):
    # TODO
    pass
    
def handle_file(resource, library):
    download_uri = resource['download_url']
    
    response = requests.get(download_uri)
    
    if response.status_code != 200:
        print("ERROR: encountered an error while fetching file ", resource['name'])
        
    file_bytes = response.content
    
    with open(ROOT_PATH + resource['path'], "wb") as output:
        output.write(file_bytes)
        output.close()
    
def handle_tree(resource, library):
    # TODO
    pass

def download_resource(resource, library):
    mapping = {
        'dir': handle_dir,
        'blob': handle_blob,
        'tree': handle_tree,
        'file': handle_file
    }
    
    return mapping[resource['type']](resource, library)

def download_extension(index, extensions):
    extension_name = extensions[index-2]['name']

    download_uri = MAIN_REPO + extension_name
    response = requests.get(download_uri)
    
    if response.status_code != 200:
        print("ERROR: error while requesting uri, status code = ", response.status_code)
        
    data = response.json()
    
    for resource in data:
        download_resource(resource, extension_name)

    return extension_name

def push_inside_template(extension_name, template_folder="./"):
    # NOTE: in case of 'example' template_folder is equal to './template-folder'
    copy_tree(f".tmp/{extension_name}", template_folder)

if __name__ == "__main__":

    if not os.environ.get("GIT_USER") or not os.environ.get("GIT_TOKEN"):
        print("ERROR: GIT_USER or GIT_TOKEN has not been provided as ENV variable")
        exit(1)

    if not os.path.isdir(ROOT_PATH):
        os.mkdir(ROOT_PATH)

    print("** Avaiable extensions for flask-template-extensions")

    extensions = list_extensions()
    choice = int(input("Choose an extension and input here the corresponding number: "))

    if choice > len(extensions) or choice < 0:
        print("ERROR: Invalid extensions index provided")
        exit(1)

    if not os.path.isdir(ROOT_PATH + extensions[choice-2]['name']):
        os.mkdir(ROOT_PATH + extensions[choice-2]['name'])

    extension = download_extension(choice, extensions)

    push_inside_template(extension, "./template-folder")

    exit(0)

    
