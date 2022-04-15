from pathlib import Path
import os

import re

import pandas as pd

import ssl
import requests, json
import urllib
import codecs
ssl._create_default_https_context = ssl._create_unverified_context

class PharmaciesChile:

    def __init__(self):
        self.url_pharmacies_operational = self.stored_url_pharmacies
        self.url_pharmacies_on_shift = self.stored_url_pharmacies_on_shift

    @property    
    def stored_url_pharmacies_operational(self):

        url = 'https://farmanet.minsal.cl/index.php/ws/getLocales'

        return url
    
    @stored_url_pharmacies_operational.setter
    def stored_url_pharmacies(self, url):

        self.url_pharmacies_operational = url

    @property    
    def stored_url_pharmacies_on_shift(self):

        url = 'https://farmanet.minsal.cl/index.php/ws/getLocalesTurnos'

        return url

    @stored_url_pharmacies_on_shift.setter
    def stored_url_pharmacies_on_shift(self, url):

        self.url_pharmacies_on_shift = url

    def response_url(self, url):

        # GET-Request
        try:
            print(f'Generating connection to: {url}')
            response = requests.get(url)
        
        except urllib.error.HTTPError as http:
            print('\nHTTP error: ' + http)

        except urllib.error.URLError as ue:
            print('\nThe server is not operational, please try again later')
        
        else:
            print(f'\nSuccessful connection\n')

        return response

    def __get_data(self, url):

        data = self.response_url(url)
        data = codecs.decode(data.text.encode(), 'utf-8-sig')
        data = json.loads(data)

        data = pd.DataFrame(data)

        return data

    def __data_pharmacies_operational(self):

        data = self.__get_data(self.url_pharmacies_operational)

        return data

    def __data_pharmacies_on_shift(self):
        
        data = self.__get_data(self.url_pharmacies_on_shift)

        return data

    def data_pharmacies(self):

        data_pharmacies_operational = self.__data_pharmacies_operational()
        data_pharmacies_on_shift = self.__data_pharmacies_on_shift()

        data_pharmacies_on_shift.rename(columns = 
            {
                'funcionamiento_hora_apertura' : 'funcionamiento_hora_apertura_turno',
                'funcionamiento_hora_cierre' : 'funcionamiento_hora_cierre_turno'
            },
            inplace = True
        )

        data_pharmacies_on_shift['turno'] = 'Si'

        data_pharmacies = pd.merge(
            data_pharmacies_operational,
            data_pharmacies_on_shift.loc[:, ['local_id', 'turno', 'funcionamiento_hora_apertura_turno', 'funcionamiento_hora_cierre_turno']],
            on = 'local_id',
            how = 'left'
        )

        data_pharmacies['turno'].fillna(
            'No',
            inplace = True
        )

        return data_pharmacies

    def download_data_pharmacies(self, format = ('csv', 'xlsx'), path = None):

        """
        DOWNLOAD DATA PHARMACIES

        Args:

            format (str):
            path (str):

        Returns:


        """

        if type(format) != str:

            raise TypeError(
                'format argument must be of type str'
            )

        if format not in ('csv', 'xlsx'):

            raise ValueError(
                'the export format can only be csv or xlsx' 
            )

        if path is not None and type(path) != str:

            raise TypeError(
                'path argument must be of type str'
            ) 

        data = self.data_pharmacies()
        
        reg_exp = re.compile('.*(D|d)ownloads$|.*(D|d)escargas$')
        directorys = [os.path.join(Path.home(), p) for p in os.listdir(Path.home())]

        directory_downloads = list(filter(reg_exp.match, directorys))[0]

        get_cwd = os.getcwd()

        if path is None:
            if len(directory_downloads) != 0:

                path = directory_downloads
            
            else:

                path = get_cwd

        if format == 'csv':

            data.to_csv(path + '/data.csv')

        else:

            data.to_excel(path + '/data.xlsx')