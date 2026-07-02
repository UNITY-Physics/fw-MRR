import flywheel
import json
import pydicom


def get_demo(context):
    """Get subject and session label from demo input file."""
    # Read config.json file
    p = open('/flywheel/v0/config.json')
    config = json.loads(p.read())

    # Read API key in config file
    api_key = (config['inputs']['api-key']['key'])
    fw = flywheel.Client(api_key=api_key)
    
    # Get the input file id
    input_file_id = (config['inputs']['axi']['hierarchy']['id'])
    print("input_file_id is : ", input_file_id)
    input_container = fw.get(input_file_id)

    # Get the session id from the input file id
    # & extract the session container
    session_id = input_container.parents['session']
    session_container = fw.get(session_id)
    session = session_container.reload()
    print("subject label: ", session.subject.label)
    print("session label: ", session.label)
    session_label = session.label
    subject_label = session.subject.label

    # # pull session comments from dicom & return to session notes
    for file in input_container.files:
        if file.type == 'dicom':
            try:
                #print(file.info.keys())
                session_notes = file.info.get("PatientComments")
                
            except Exception as e:
                print("Error pulling info:", e)
                session_notes = None
    
            print("Session notes (PatientComments):", session_notes)
            
            # Add note to session if present
            if session_notes:
                print("Session notes added to session container.")
                #Update session info 
                session.add_note(session_notes)

                session_info = session.info
                session_info["session_comments"] = session_notes
                session.update_info(session_info)

            print("Demographics:", subject_label, session_label)
            return subject_label, session_label
