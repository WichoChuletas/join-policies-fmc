import csv, json, sys, requests, time, urllib3, getpass
import pandas as pd
from authToken import AuthToken
from time import time
from progress.bar import Bar, ChargingBar
from json import JSONEncoder

#Deshabilitar Warnings de Certificado
urllib3.disable_warnings()

class GetPolicy():

    server = ""
    username = ""
    password = ""
    policyName = ""
    csv = ""
    

    #ApiPath AccessRules
    apiPath = ["/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/accesspolicies/{containerUUID}/accessrules?limit=1000&expanded=true"]
    
    #Declaración de parametros del header del requests
    headers = {'Content-Type': 'application/json'}

    #Abriendo el archivo de excel de url category
    #excelFileURL = pd.read_csv("ExcelFiles/urlRules.csv") 
    
    #Abriendo el archivo de excel de application category
    #excelFileApp = pd.read_csv("ExcelFiles/appRules.csv") 

    #Archivos de FMC Data
    def __init__(self, server, policyName, csv, token):
        self.server = server
        self.policyName = policyName
        self.csv = csv
        self.objectDontFound = []
        self.token = token
        self.apiPath = ["/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/accesspolicies/{containerUUID}/accessrules?limit=1000&expanded=true"]

    def getAccessRules(self):
        print(self.policyName)
        id = (self.getDataPolicy(self.policyName))
        print(id)
        if id != None:
            self.apiPath[0] = self.server+self.apiPath[0].replace("{containerUUID}", id)
            print(self.apiPath)
            self.headers['X-auth-access-token'] = self.token
            self.getData()
            return True
        else:
            return None


    #limpiar campos vacios de los access rules creados
    def limpiarVacio(self, d):
        if not isinstance(d, (dict, list)):
            return d
        if isinstance(d, list):
            return [v for v in (self.limpiarVacio(v) for v in d) if v]
        return {k: v for k, v in ((k, self.limpiarVacio(v)) for k, v in d.items()) if v}

    #Identificacion de Objetos No encontrados
    def DidntFound(self, forFind, foundIt, files):
        listForFind = []
        listFoundIt = []
        for obj in forFind:
            listForFind.append({"name": obj})
        for obj in foundIt:
            listFoundIt.append({"name": obj["name"]})
        if(len(listForFind) != len(listFoundIt)):
            didntFound = {each['name'].lower(): each for each in listForFind if each not in listFoundIt}.values()
            for obj in didntFound:
                print("\n Objetos no encontrado:", obj["name"])
            self.objectDontFound.append({
                "name": didntFound,
                "files": files
            })

    #Para Encontrar Objetos Direcciones IP, URLs, Puertos y grupos de los mismos
    def getDataExcel(self, cell, files):
        #print(str(files[0]))
        fileAux=files[len(files)-1].split("/")
        #print(fileAux[len(fileAux)-1] + "FMCintrusionpolicy.json")
        if fileAux[len(fileAux)-1] == "FMCintrusionpolicy.json" or fileAux[len(fileAux)-1] == "FMCFilePolicy.json":
            cell = [cell]
            #print(cell)
        else:
            cell = cell.split()
            #print(cell)
        objFound = []
        for name in cell:
            for file in files:
                with open(file, "r+") as jsonFile:
                    jsonLoad = json.load(jsonFile)
                    for jsonObj in jsonLoad:
                        if(jsonObj["name"].lower() == name.lower()):
                            objFound.append({"type": jsonObj["type"], "name": jsonObj["name"], "id": jsonObj["id"]}) 
        self.DidntFound(cell, objFound, files)
        return objFound

    def getUsers(self, cell, files):
        objFound = []
        print(cell)
        for file in files:
            with open(file, "r+") as jsonFile:
                jsonLoad = json.load(jsonFile)
                for jsonObj in jsonLoad:
                    if(jsonObj["name"].lower() == cell.lower()):
                        objFound.append({"type": jsonObj["type"], "name": jsonObj["name"], "id": jsonObj["id"]}) 
        print(objFound)
        return objFound

    def getApp(self, cell, files):
        cell = cell.split("-")
        objFound = []
        for name in cell:
            for file in files:
                with open(file, "r+") as jsonFile:
                    jsonLoad = json.load(jsonFile)
                    for jsonObj in jsonLoad:
                        if(jsonObj["name"].lower() == name.lower()):
                            objFound.append({"type": jsonObj["type"], "name": jsonObj["name"], "id": jsonObj["id"]}) 
        return objFound

    #Para Encontrar Objetos Direcciones IP, URLs, Puertos y grupos de los mismos
    def getURLCat(self, cell):
        files = ["APIFMCv2/FMCFiles/FMCURLCategory.json"]
        cell = cell.split("-")
        objFound = []
        for name in cell:
            for file in files:
                with open(file, "r+") as jsonFile:
                    jsonLoad = json.load(jsonFile)
                    for jsonObj in jsonLoad:
                        if(jsonObj["name"].lower() == name.lower()):
                            objFound.append({"type": 
                                "UrlCategoryAndReputation", 
                                    "category": { 
                                        "name": jsonObj["name"], 
                                        "id": jsonObj["id"], 
                                        "type": jsonObj["type"] 
                                    }, 
                                "reputation": "NEUTRAL",
                                "type": "UrlCategoryAndReputation" 
                            }) 
        return objFound

    #Función para realizar get de AccessRules
    def Requests(self, url):
        try:
            print(url)
            r = requests.get(url, headers=self.headers, verify=False)
            
            status_code = r.status_code
            resp = r.text
            if (status_code == 200):
                json_resp = json.loads(resp)
                return json_resp
            else:
                r.raise_for_status()
                print("Error occurred in GET --> "+resp)
        except requests.exceptions.HTTPError as err:
                print ("Error in connection --> "+str(err)) 

    #Extraccion de AccessRules
    def getData(self):
        ObjectFMC = []
        # variables para obtención de objetos por pagina
        i=0
        for uri in self.apiPath:
            print(uri)
            json_resp = self.Requests(uri)
            paging = json_resp["paging"] # Datos de Paginación de Objetos
            try: 
                items = json_resp["items"]   # Objetos del Requets Ejecutado
            except:
                print("No Hay Datos")
                continue
            count = (paging["offset"] + paging["limit"]) #objetos por pagina
            print("\n")
            progress = Bar('Charging '+ items[0]["type"]+ ' Objects:', max=paging["limit"])
            for item in items:
                #print(json.dumps(item,sort_keys=True,indent=4, separators=(',', ': ')))         
                item = self.getNameData(item)
                #input("Pausa")
                progress.next()
                ObjectFMC.append(item)
            if(paging["count"] != count):
                auxURL = str(paging["next"][0]).replace("['", "").replace("']", "") 
                print(auxURL)
                self.apiPath.insert(i+1, auxURL)
            else:
                with open("APIFMCv2/FMCFiles/FMC"+self.policyName+".json", "w+") as fileFMC:
                    json.dump(list(ObjectFMC), fileFMC, indent=4)
                dfNet = pd.DataFrame(ObjectFMC, columns=["name", "action", "enable", "sendEventsToFMC", "logFiles", "logEnd", "logBegin","sourceZones", "destinationZones", "sourceNetworks", "destinationNetworks", 
                                        "destinationPorts", "urlCategoriesWithReputation", "urls", "applications", "inlineApplicationFilters", "tags", "filePolicy", "ipsPolicy", "users"])
                dfNet.to_csv("APIFMCv2\ProcesedFiles\CSVFiles\policies-out-fmc.csv")
                print("\nReady!")
                ObjectFMC = []
            i=i+1
        progress.finish()

    start_time = time()

    #Identificacion de Politica por medio de ID
    def getDataPolicy(self, cell):
        cell = cell.split()
        for name in cell:
            file = "APIFMCv2/FMCFiles/FMCAccessPolicy.json"
            with open(file, "r+") as jsonFile:
                jsonLoad = json.load(jsonFile)
                for jsonObj in jsonLoad:
                    print(jsonObj["name"].lower(), name.lower())
                    if(jsonObj["name"].lower() == name.lower()):
                        return jsonObj["id"]
        return None

    def getNameData(self, item):

        objects = []
        newItem = []
        name = ""
        action = ""
        enable = ""
        destinationNetworks = ""
        destinationZones = ""
        sourceZones = ""
        sourceNetworks = ""
        filePolicy = ""
        ipsPolicy = ""
        destinationPorts = ""
        urls = ""
        urlCategoriesWithReputation = ""
        applications = ""
        inlineApplicationFilters = ""
        sendEventsToFMC = ""
        logFiles = ""
        logEnd = ""
        logBegin = ""
        tags = ""
        users = ""

        try:
            sendEventsToFMC = item["sendEventsToFMC"] 
        except KeyError as er:
            print("No existe el campo", er)

        try:
            name = item["name"]
        except KeyError as er:
            print("No existe el campo", er)

        try:
            action = item["action"]
        except KeyError as er:
            print("No existe el campo", er)

        try:
            enable = item["enabled"]
        except KeyError as er:
            print("No existe el campo", er)

        try:
            ipsPolicy = item["ipsPolicy"]["name"]
        except KeyError as er:
            print("No existe el campo", er)
        try:
            filePolicy = item["filePolicy"]["name"]
        except KeyError as er:
            print("No existe el campo", er)

        try:
            logFiles = item["logFiles"]
        except KeyError as er:
            print("No existe el campo", er)

        try:
            logEnd = item["logEnd"]
        except KeyError as er:
            print("No existe el campo", er)

        try:
            logBegin = item["logBegin"]
        except KeyError as er:
            print("No existe el campo", er)


        try:
            usersObj = item["users"]["objects"]
            #Url Categories With Reputation
            if len(usersObj) > 1:
                for obj in usersObj:
                    users =  users + "-" + obj["name"]
                users = users.strip("-")
            else:
                users = usersObj[0]["name"]
            
            print(users)

        except KeyError as er:
            print("No existe el campo", er)
            
        try:

            #Destination Networks
            objects = item["destinationNetworks"]["objects"]
            if len(objects) > 1:
                for obj in objects:
                    destinationNetworks = destinationNetworks + " " + obj["name"]
                destinationNetworks = destinationNetworks.strip()
            else:
                destinationNetworks = objects[0]["name"]

        except KeyError as er:
            print("No existe el campo", er)

        try:

            #Destination Zones
            objects = item["destinationZones"]["objects"]
            if len(objects) > 1:
                for obj in objects:
                    destinationZones =  destinationZones + " " + obj["name"]
                destinationZones = destinationZones.strip()
            else:
                destinationZones = objects[0]["name"]

        except KeyError as er:
            print("No existe el campo", er)

        try:

            #Source Zones
            objects = item["sourceZones"]["objects"]
            if len(objects) > 1:
                for obj in objects:
                    sourceZones = sourceZones + " " + obj["name"]
                sourceZones = sourceZones.strip()
            else:
                sourceZones = objects[0]["name"]

        except KeyError as er:
            print("No existe el campo", er)

        try:

            #Source Networks
            objects = item["sourceNetworks"]["objects"]
            if len(objects) > 1:
                for obj in objects:
                    sourceNetworks = sourceNetworks + " " + obj["name"]
                sourceNetworks = sourceNetworks.strip()
                #print(sourceNetworks)
            else:
                sourceNetworks = objects[0]["name"]

        except KeyError as er:
            print("No existe el campo", er)



        try:

            #Destination Ports
            objects = item["destinationPorts"]["objects"]
            if len(objects) > 1:
                for obj in objects:
                    destinationPorts =  destinationPorts + " " + obj["name"]
                destinationPorts = destinationPorts.strip()
            else:
                destinationPorts = objects[0]["name"]

        except KeyError as er:
            print("No existe el campo", er)

        try:

            #Urls
            objects = item["urls"]["objects"]
            if len(objects) > 1:
                for obj in objects:
                    urls =  urls + " " + obj["name"]
                urls = urls.strip()
            else:
                urls = objects[0]["name"]

        except KeyError as er:
            print("No existe el campo", er)

        try:

            #Url Categories With Reputation
            objects = item["urls"]["urlCategoriesWithReputation"]
            if len(objects) > 1:
                for obj in objects:
                    urlCategoriesWithReputation =  urlCategoriesWithReputation + "-" + obj["category"]["name"]
                urlCategoriesWithReputation = urlCategoriesWithReputation.strip("-")
            else:
                urlCategoriesWithReputation = objects[0]["category"]["name"]

        except KeyError as er:
            print("No existe el campo", er)

        try:

            #Applications
            objects = item["applications"]["applications"]
            if len(objects) > 1:
                for obj in objects:
                    applications =  applications + "-" + obj["name"]
                applications = applications.strip("-")
            else:
                applications = objects[0]["name"]

        except KeyError as er:
            print("No existe el campo", er)

        try:

            #Inline Application Filters Categories
            objects = item["applications"]["inlineApplicationFilters"][0]["categories"]
            if len(objects) > 1:
                for obj in objects:
                    inlineApplicationFilters =  inlineApplicationFilters + "-" + obj["name"]
                inlineApplicationFilters = inlineApplicationFilters.strip("-")

            else:
                inlineApplicationFilters = objects[0]["name"]

        except KeyError as er:
            print("No existe el campo", er)

        try:
            
           #Inline Application Filters Tags
            objects = item["applications"]["inlineApplicationFilters"][0]["tags"]
            if len(objects) > 1:
                for obj in objects:
                    tags =  tags + "-" + obj["name"]
                tags = tags.strip("-")
            else:
                tags = objects[0]["name"]
        
        except KeyError as er:
            print("No existe el campo", er)
        

        newItem = {
            "name": name,
            "action": action,
            "enable": enable,
            "sourceZones": sourceZones,
            "destinationZones": destinationZones,
            "sourceNetworks": sourceNetworks,
            "destinationNetworks": destinationNetworks,
            "destinationPorts": destinationPorts,
            "filePolicy": filePolicy,
            "ipsPolicy": ipsPolicy,
            "urls": urls,
            "urlCategoriesWithReputation": urlCategoriesWithReputation,
            "sendEventsToFMC": sendEventsToFMC,
            "applications": applications,
            "inlineApplicationFilters": inlineApplicationFilters,
            "logFiles": logFiles,
            "logEnd": logEnd,
            "logBegin": logBegin,
            "tags": tags,
            "users": users
        }

        return newItem

    def generateJSON(self):

        filesObjAddress = ["APIFMCv2/FMCFiles/FMCNetwork.json", "APIFMCv2/FMCFiles/FMCHost.json", "APIFMCv2/FMCFiles/FMCRange.json", "APIFMCv2/FMCFiles/FMCNetworkGroup.json"]
        filesObjPorts = ["APIFMCv2/FMCFiles/FMCProtocolPortObject.json", "APIFMCv2/FMCFiles/FMCPortObjectGroup.json"]
        filesApp = ["APIFMCv2/FMCFiles/FMCApplication.json"]
        filesAppTag = ["APIFMCv2/FMCFiles/FMCApplicationTag.json"]
        filesAppCat = ["APIFMCv2/FMCFiles/FMCApplicationCategory.json"]
        filesObjZones = ["APIFMCv2/FMCFiles/FMCSecurityZone.json"]
        filesObjPolicy = ["APIFMCv2/FMCFiles/FMCAccessPolicy.json"]
        filesObjIntrutionPolicy = ["APIFMCv2/FMCFiles/FMCintrusionpolicy.json"]
        filesObjFilePolicy = ["APIFMCv2/FMCFiles/FMCFilePolicy.json"]
        filesObjURL = ["APIFMCv2/FMCFiles/FMCUrlGroup.json", "APIFMCv2/FMCFiles/FMCUrl.json"]
        #filesAD = ["JSONFiles\FMCData\FMCRealmUserGroupSIGNA_FWMX_Tol.json", "JSONFiles\FMCData\FMCRealmUserSIGNA_FWMX_Tol.json"]


        try:
            excelFile = pd.read_csv(self.csv) #Abriendo el archivo de excel de politicas
        except:
            print("Archivo No Encontrado")
            sys.exit()

        #numero de filas de archivo de excel de accessrules
        limit = excelFile.count()["action"]

        start_time = time()
        documentJSON = []

        progressPolicy = Bar('Processing AccessRules:', max=limit)
        for i in range(0, limit) :
            print(str(excelFile.iloc[i]["filePolicy"]))
            documentJSON.append({            
                "action": excelFile.iloc[i]["action"],
                "enabled": bool(excelFile.iloc[i]["enable"]),
                "type": "AccessRule",
                "logFiles": bool(excelFile.iloc[i]["logFiles"]),
                "logEnd": bool(excelFile.iloc[i]["logEnd"]),
                "logBegin": bool(excelFile.iloc[i]["logBegin"]),
                "sendEventsToFMC": bool(excelFile.iloc[i]["sendEventsToFMC"]),
                "name": excelFile.iloc[i]["name"],
                "urls": {
                    "objects": 
                        self.getDataExcel(excelFile.iloc[i]["urls"], filesObjURL) if (str(excelFile.iloc[i]["urls"]) != "nan") else None,
                    "urlCategoriesWithReputation": 
                        None if (str(excelFile.iloc[i]["urlCategoriesWithReputation"]) == "nan") else self.getURLCat(str(excelFile.iloc[i]["urlCategoriesWithReputation"])),
                },
                "sourceZones": {
                    "objects": self.getDataExcel(excelFile.iloc[i]["sourceZones"], filesObjZones) if (str(excelFile.iloc[i]["sourceZones"]) != "nan") else None
                },
                "destinationZones": {
                    "objects": self.getDataExcel(excelFile.iloc[i]["destinationZones"], filesObjZones) if (str(excelFile.iloc[i]["destinationZones"]) != "nan") else None
                },
                "destinationNetworks": {
                    "objects": self.getDataExcel(excelFile.iloc[i]["destinationNetworks"], filesObjAddress) if str(excelFile.iloc[i]["destinationNetworks"]) != "nan" else None
                },
                "sourceNetworks": {
                    "objects": self.getDataExcel(excelFile.iloc[i]["sourceNetworks"], filesObjAddress) if str(excelFile.iloc[i]["sourceNetworks"]) != "nan" else None
                },
                "destinationPorts": {
                    "objects": self.getDataExcel(excelFile.iloc[i]["destinationPorts"], filesObjPorts) if str(excelFile.iloc[i]["destinationPorts"]) != "nan" else None
                },
                "applications": {
                    "applications": 
                        None if (str(excelFile.iloc[i]["applications"]) == "nan") else self.getApp(excelFile.iloc[i]["applications"], filesApp)
                    ,
                    "inlineApplicationFilters": [
                        {
                            "categories": 
                                None if (str(excelFile.iloc[i]["inlineApplicationFilters"]) == "nan") else self.getApp(excelFile.iloc[i]["inlineApplicationFilters"], filesAppCat),
                            "tags": 
                                None if (str(excelFile.iloc[i]["tags"]) == "nan") else self.getApp(excelFile.iloc[i]["tags"], filesAppTag)
                        }
                    ],
                },
                #"users": {
                #    "objects": self.getUsers(str(excelFile.iloc[i]["users"]), filesAD) if str(excelFile.iloc[i]["users"]) != "nan" else None
                #},
                "ipsPolicy": 
                    self.getDataExcel(str(excelFile.iloc[i]["ipsPolicy"]), filesObjIntrutionPolicy)[0] if str(excelFile.iloc[i]["action"]) == "ALLOW" and str(excelFile.iloc[i]["ipsPolicy"]) != "nan" else None
                ,
                "filePolicy": 
                    self.getDataExcel(str(excelFile.iloc[i]["filePolicy"]), filesObjFilePolicy)[0] if str(excelFile.iloc[i]["action"]) == "ALLOW" and str(excelFile.iloc[i]["filePolicy"]) != "nan"else None
            })        
            progressPolicy.next()
        progressPolicy.finish()
        fieldscleaned = self.limpiarVacio(documentJSON)
        with open("APIFMCv2\ProcesedFiles\JSONFiles\jsonAccessRules.json", "w+") as file1:
            json.dump(list(fieldscleaned), file1, indent=4)

if __name__ == "__main__":


    try:
        print("\nWelcome to Get Bulk Program")

        continuar = True

        while(continuar):
            print("1.Extraer Politica del FMC")
            print("2.Transformar Excel en Politica")
            print("3.Salir")
            opcion = int(input("Opcion : "))
            if opcion == 1:

                server = ("https://" + input("FMC IP\n ->: ")).strip()
                username = input("Username: \n ->:").strip()
                password = getpass.getpass().strip()
                policyName = input("Policy Name\n ->: ").strip()
                csv = ""

                Get = GetPolicy(server, policyName, "", token)
                Get.getAccessRules()

            elif opcion == 2:

                server = ""
                username = ""
                password = ""
                csv = input("CSV \n ->: ").strip()
                policyName = ""

                Get = GetPolicy(server, username, password, policyName, csv)
                Get.generateJSON()

            elif opcion == 3:
                sys.exit()

    except KeyboardInterrupt as ms:

        print("\n ******** Adios! ********")

