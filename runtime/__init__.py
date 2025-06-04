import requests

def get_metadata(path):
    url = f'http://metadata.google.internal/computeMetadata/v1/{path}'
    headers = {'Metadata-Flavor': 'Google'}
    return requests.get(url, headers=headers).text

def get_creds():
    url = 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token'
    headers = {'Metadata-Flavor': 'Google'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to retrieve credentials from metadata server")

def delete_instance():
    creds = get_creds()
    project_id = get_metadata("project/project-id")
    zone = get_metadata("instance/zone").split("/")[-1]
    instance_name = get_metadata("instance/name")
    headers = {"Authorization": f"Bearer {creds['access_token']}"}
    requests.delete(
        f"https://www.googleapis.com/compute/v1/projects/{project_id}/zones/{zone}/instances/{instance_name}",
        headers=headers,
    )
