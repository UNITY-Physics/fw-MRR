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
    """
    Detect modality (T1/T2) and acquisition speed (Fast/standard)
    from the axial input file, download matching acquisitions,
    and return the modality label.
    """
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


    # --- determine modality + speed from axial input --- #
    axial_files = os.listdir('/flywheel/v0/input/axi/')
    if not axial_files:
        raise RuntimeError("No axial input file found in /flywheel/v0/input/axi/")

    # assume single axial file
    axial_file = axial_files[0].upper()

    if 'T1' in axial_file:
        modality = 'T1'
    elif 'T2' in axial_file:
        modality = 'T2'
    else:
        raise RuntimeError(f"Axial input file does not contain T1 or T2: {axial_file}")

    speed = 'Fast' if 'FAST' in axial_file else 'standard'
    print(f"Detected modality: {modality}, speed: {speed}")

    # --- process acquisitions --- #
    for acq in session_container.acquisitions.iter():
        if modality.lower() in acq.label.lower() and 'QC-failed' not in acq.tags:
            print("acq is : ", acq.label)
            print("acq tags are : ", acq.tags)
            for file in acq.files:
                fname = file.name.upper()
                if file['type'] == 'nifti' and modality in fname:
                    # filter by speed
                    if speed == 'Fast' and 'FAST' not in fname:
                        continue
                    if speed == 'standard' and 'FAST' in fname:
                        continue

                    # orientation-specific downloads
                    if 'SAG' in fname:
                        print(f"downloading SAG {modality} file...")
                        download_dir = '/flywheel/v0/input/sag'
                        os.makedirs(download_dir, exist_ok=True)
                        file.download(os.path.join(download_dir, file.name))

                    elif 'COR' in fname:
                        print(f"downloading COR {modality} file...")
                        download_dir = '/flywheel/v0/input/cor'
                        os.makedirs(download_dir, exist_ok=True)
                        file.download(os.path.join(download_dir, file.name))

    # return modality label for downstream use
    return modality
