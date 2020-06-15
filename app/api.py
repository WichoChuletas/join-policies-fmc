import requests, json, re
from progress.bar import Bar, ChargingBar



def get_data(server, path, headers):

    url = 'https://' + server + path
    elements = []
    
    def requester():

        try:

            r = requests.get( 
                url, 
                headers=headers,
                verify=False
            )
            
            status_code = r.status_code
            resp = r.text
            json_resp = json.loads(resp)
            if status_code == 200:
                return json_resp
            else:
                error = json_resp["error"]
                for mens in error["messages"]:
                    print("\n"+cleanhtml(mens["description"]))

        except requests.exceptions.HTTPError as err:
                print ("Error in connection --> "+str(err)) 
    
    json_response = requester()
    
    items = json_response["items"] #Elementos obtenidos de response
    paging = json_response["paging"] #Datos de paging de objetos
    count = (paging["offset"] + paging["limit"]) #Objetos por paging

    print("\n")
    progress = Bar('Charging '+ items[0]["type"]+ ' Objects:', max=paging["limit"])
    for item in items:
        if item['type'] == 'AccessPolicy':   
            elements.append({ 'type': item['type'] , 'name': item['name'], 'id': item['id'] })
        else:
            elements.append(item)
        progress.next()
    progress.finish()

    return elements

def post_data(server, path, headers, data):

    url = 'https://' + server + path

    def requester():

        try:

            r = requests.post(
                url, json=json.dumps(data),
                headers=headers,
                verify=False
            )
            
            status_code = r.status_code
            resp = r.text
            json_resp = json.loads(resp)
            if status_code == 201 or status_code == 202:
                print('POST SUCCESSFULLY!')
            else:
                error = json_resp["error"]
                print(error)

        except requests.exceptions.HTTPError as err:
                print ("Error in connection --> "+str(err)) 

    requester()


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext