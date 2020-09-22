import requests, json

path_token = '/api/fmc_platform/v1/auth/generatetoken'

def get_token(server, user_data):
    r = None
    try:
        r = requests.post( 
            ('https://' + server) + path_token, 
            headers={'Content-Type': 'application/json'}, 
            auth=requests.auth.HTTPBasicAuth(user_data.username, user_data.password), 
            verify=False
        )
        headers = r.headers
        auth_token = headers.get('X-auth-access-token', default=None)
        if auth_token == None:
            print("auth_token not found. Exiting...")
            return None
    except Exception as err:
        print ("Error in generating auth token --> "+str(err))
        return None    
    return auth_token