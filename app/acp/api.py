import json

from app.api import get_data, post_data

acp_path = '/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/accesspolicies?limit=1000&expanded=true'
acr_path = '/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/accesspolicies/{}/accessrules?limit=1000&expanded=true'

acr_path_post = '/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/accesspolicies/{}/accessrules?bulk=true'

acp_fmc_json_directory = 'app\\temp\\acp\\json\\fmc\\' 
acp_post_json_directory = 'app\\temp\\acp\\json\\post\\'


def get_acp(server, headers):
    
    elements = []

    def get_acr(acp_id, acp_name, sufix):
        acrs = get_data(server, acr_path.format(acp_id), headers)
        json_save(acp_fmc_json_directory, acrs, acp_name)
        for acr in acrs:
            if len(acr.name) <= 27:
                print(acr.name)
            del acr['links']
            del acr['metadata']
            del acr['id']
            del acr['vlanTags']
            elements.append(acr)

        json_save(acp_post_json_directory, elements, acp_name)

    continuar = True

    while(continuar):

        acps = get_data(server, acp_path, headers)

        print('\n')
        i = 1
        for i in range(1, len(acps)):
            print( str(i) + '. ' + acps[i]['name'])
        print(str(i+1) + '. ' + 'Salir')

        print('\n')
        option = int(input("Option : "))
    
        if option == len(acps):

            continuar = False

        else :

            option_acp = acps[option]
            print(option_acp['id'])
            sufix = input("Sufix name rule : ")
            get_acr(option_acp['id'], option_acp['name'], sufix)


def post_acp(server, headers):
    elements = []

    continuar = True

    while(continuar):

        acps = get_data(server, acp_path, headers)

        print('\n')
        i = 1
        for i in range(1, len(acps)):
            print( str(i) + '. ' + acps[i]['name'])
        print(str(i+1) + '. ' + 'Salir')

        print('\n')
        option = int(input("Option : "))
    
        if option == len(acps):
            continuar = False

        else :
            option_acp = acps[option]
            print('\n')
            directory = input("JSON file : ")
            data = json_open(directory)
            print(option_acp['id'])
            post_data(server, acr_path_post.format(option_acp['id']), headers, data)


def json_save(directory, json_acr, acp_name):
    with open('{}{}.json'.format(directory, acp_name), 'w+') as json_file:
        json.dump(list(json_acr), json_file, indent=4)

def json_open(directory):
    with open(directory) as json_file:
        return json.load(json_file)
