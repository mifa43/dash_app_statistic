import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
from dropbox.exceptions import DropboxException
import os
from pathlib import Path
from analytics import Analytic

class DropBoxConnection(Analytic):

    def allow_access(self):
        """### Kreiramo OAuth flow za token (long-lived token type)"""


        APP_KEY = f"{os.getenv('DBX_APP_KEY')}"
        APP_SECRET = f"{os.getenv('DBX_APP_SECRET')}"

        # Vraca url za autorizaciju
        self.auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

        authorize_url = self.auth_flow.start()

        return authorize_url
    
    def get_dropbox_client(self, auth_code: str):
        """### OAuth Dropbox klijent"""
        try:
            # Dobijamo tokene refresh i access token 
            self.oauth_result = self.auth_flow.finish(auth_code)

        except Exception as e:

            print('Error: %s' % (e,))

            exit(1)

        print("Successfully set up client!")
    
        return dropbox.Dropbox(oauth2_access_token=self.oauth_result.access_token)

    def delete_old_files(self):

        folder = Path("./hr_statistic/app")

        if folder.exists() and folder.is_dir():

            is_file_excel = folder.glob("*.xlsx")
            
            for file in is_file_excel:
                
                if os.path.isfile(file):

                    os.remove(file)

                    print(f"Located and removed old file: {file}")

    
    def download_files(self, remote_path: list, local_path: list, auth_code) -> None:
        """### Pomocna funkcija koja skida azurne datoteke sa dropbox-a
        ---

        #### :params
        - `remote_path: str` -> Dropbox putanja do ciljane datoteke
        - `local_path: str` -> Putanja na lokalnoj masini
        
        ---
        #### :return
        - `New files: File`
        """
        try:

            self.delete_old_files()

            dbx = self.get_dropbox_client(auth_code)

            for dbx_path, loc_path  in zip(remote_path, local_path):

                
                dbx.files_download_to_file(download_path=loc_path, path=dbx_path)

                print(f"Dropbox: successfully downloaded to {dbx_path}")
            
        except DropboxException as err:

            print(f"Something went wrong from dropbox: {err}")

# d = DropBoxConnection()
# d.allow_access()
# # d.get_dropbox_client()
# res = d.download_files(
#     ["/test/KOMERCIJALA - OPTI - BETA.xlsx", 
#      "/test/TELEMARKETING OPTI - BETA(1).xlsx"
#      ], 
#     ["./hr_statistic/app/KOMERCIJALA - OPTI - BETA.xlsx", 
#      "./hr_statistic/app/TELEMARKETING OPTI - BETA(1).xlsx"
#      ]
#     )
# print(res)