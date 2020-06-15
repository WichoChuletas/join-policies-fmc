import sys, getpass, urllib3

from app.models import UserData
from app.auth.get_token import get_token
from app.acp.api import get_acp, post_acp

#Deshabilitar Warnings de Certificado
urllib3.disable_warnings()

if __name__ == "__main__":
    print('\n')
    print('Welcome!')

    try:
        continuar = True

        while(continuar):
            print('\n')
            print("1.GET Policy from FMC")
            print("2.POST Policy to FMC")
            print("3.Salir")
            print('\n')
            option = int(input("Option : "))
            
            if option == 1:
                print('\n')
                server = input("FMC IP \n ->:").strip()
                print('\n')
                print('Enter Credentials')
                print('\n')
                username = input("Username \n ->:").strip()
                password = getpass.getpass().strip()

                user_data = UserData(username, password)

                headers = get_token(server, user_data)

                if headers is None:
                    continue

                get_acp(server, headers)

            if option == 2:

                print('\n')
                server = input("FMC IP \n ->:").strip()
                print('\n')
                print('Enter Credentials')
                print('\n')
                username = input("Username \n ->:").strip()
                password = getpass.getpass().strip()

                user_data = UserData(username, password)

                headers = get_token(server, user_data)

                if headers is None:
                    continue

                post_acp(server, headers)

            elif option == 3:
                sys.exit()

    except KeyboardInterrupt as ms:
        print("\n ******** Adios! ********")