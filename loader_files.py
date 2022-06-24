import subprocess

import constant


class Loader:
    """ Класс загрузчик данных по солана """
    def __init__(self):
        self.__path_solana = constant.SOLANA_PATH
        self.__cluster = constant.SOLANA_CLUSTER

    def get_validators(self):
        """ Возвращает список валидаторов и их данные """
        process = subprocess.run([self.__path_solana, f'-u{ self.__cluster }', 'validators', '--output', 'json-compact'],
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        return process.stdout

    def get_gossip(self):
        process = subprocess.run([self.__path_solana, f'-u{ self.__cluster }', 'gossip', '--output', 'json-compact'],
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        return process.stdout

    def get_leader_schedule(self):
        process = subprocess.run([self.__path_solana, f'-u{ self.__cluster }', 'leader-schedule', '--output', 'json-compact'],
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        return process.stdout

    def get_block_production(self):
        process = subprocess.run([self.__path_solana, f'-u{ self.__cluster }', '-v', 'block-production', '--output', 'json-compact'],
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        return process.stdout

    def get_validators_credits(self):
        process = subprocess.run([self.__path_solana, 'validators', f'-u{ self.__cluster }', '--sort=credits', '-r', '-n', '--output', 'json-compact'],
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        return process.stdout

    def get_epoch(self):
        process = subprocess.run([self.__path_solana, 'epoch-info'],
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        return process.stdout

    def get_balance(self, pub_key):
        process = subprocess.run([self.__path_solana, 'balance', pub_key, f'-u{ self.__cluster }'],
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)

        balance_txt = process.stdout
        balance_txt = balance_txt.replace(' SOL', '')
        return round(float(balance_txt), 2)

    def get_stake(self, vote_key):
        process = subprocess.run([self.__path_solana, f'-u{ self.__cluster }', 'stakes', vote_key, '--output', 'json-compact'],
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        return process.stdout
