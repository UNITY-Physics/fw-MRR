import os
import flywheel
import json
import fnmatch

# Read config.json file to:
# 1. Get the API key
# 2. Get the input file id
# 3. Get the file object container
# 4. Get the list of files in the container
# 5. Loop through the list of files and get the file object information & download the file

def find_files():
    # Read config.json file
    p = open('/flywheel/v0/config.json')
    config = json.loads(p.read())

    # Read API key in config file
    api_key = (config['inputs']['api-key']['key'])
    fw = flywheel.Client(api_key=api_key)

    print(dir(fw))

    # Get the parent id from inputs in config file
    input_container_type = config.get("inputs", {}).get("axi", {}).get("hierarchy", {}).get("type")
    if input_container_type == 'session':
            session_id = config.get("inputs", {}).get("axi", {}).get("hierarchy", {}).get("id")
            session_container = fw.get(session_id)
            print("running from session level...")
            print("session_container is : ", session_container.label)
    else:
        parent_id = config.get("inputs", {}).get("axi", {}).get("hierarchy", {}).get("id")
        parent = fw.get(parent_id)
        print(parent.parents)
        # get the session id from the parent
        session_id = parent.parents.session
        session_container = fw.get(session_id)
        print("session_container is : ", session_container.label)

    # --- fast vs slow --- #
    speed = 'standard'
    for file in os.listdir('/flywheel/v0/input/axi/'):
        if fnmatch.fnmatch(file.upper(), '*FAST*'):
            speed = 'Fast'
        else:
            speed = 'standard'

    if speed == 'Fast':
        # get the acquisition from the session
        for acq in session_container.acquisitions.iter():
            if 'T2' in acq.label and 'QC-failed' not in acq.tags: # restrict to T2 acquisitions
                print("acq is : ", acq.label)
                print("acq tags are : ", acq.tags)
                for file in acq.files: # get the files in the acquisition
                    # Screen file object information & download the desired file
                    if file['type'] == 'nifti' and 'T2' in file.name.upper() and 'FAST' in file.name.upper():
                        if 'SAG' in file.name.upper():
                            print("downloading SAG file...")
                            sag = file
                            download_dir = ('/flywheel/v0/input/sag')
                            if not os.path.exists(download_dir):
                                os.mkdir(download_dir)
                            download_path = download_dir + '/' + sag.name
                            sag.download(download_path)

                        elif 'COR' in file.name.upper():
                            print("downloading COR file...")
                            cor = file
                            download_dir = ('/flywheel/v0/input/cor')
                            if not os.path.exists(download_dir):
                                os.mkdir(download_dir)
                            download_path = download_dir + '/' + cor.name
                            cor.download(download_path)

    elif speed == 'standard':
        # get the acquisition from the session
        for acq in session_container.acquisitions.iter():
            if 'T2' in acq.label and 'QC-failed' not in acq.tags: # restrict to T2 acquisitions
                print("acq is : ", acq.label)
                print("acq tags are : ", acq.tags)
                for file in acq.files: # get the files in the acquisition
                    # Screen file object information & download the desired file
                    if file['type'] == 'nifti' and 'T2' in file.name.upper() and 'FAST' not in file.name.upper():
                        if 'SAG' in file.name.upper():
                            sag = file
                            download_dir = ('/flywheel/v0/input/sag')
                            if not os.path.exists(download_dir):
                                os.mkdir(download_dir)
                            download_path = download_dir + '/' + sag.name
                            sag.download(download_path)

                        elif 'COR' in file.name.upper():
                            cor = file
                            download_dir = ('/flywheel/v0/input/cor')
                            if not os.path.exists(download_dir):
                                os.mkdir(download_dir)
                            download_path = download_dir + '/' + cor.name
                            cor.download(download_path)