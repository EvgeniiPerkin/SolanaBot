import constant
import requests


def get_queue_number(address):
    url = "https://kyc-api.vercel.app/api/validators/list?"
    params = {'search_term': address, 'limit': 1, 'order_by': 'name', 'order': 'asc'}
    r = requests.get(url=url, params=params)
    json_str = r.json()
    return json_str['data'][0]['onboarding_number']


def send_msg_telegram(token, chat_id, body):
    url = "https://api.telegram.org/bot" + token + "/sendMessage"
    param = {'chat_id': chat_id, 'text': body, 'parse_mode': 'html'}
    r = requests.post(url=url, params=param)


class QueryData:
    def __init__(self):
        self.__cluster = ""
        self.__max_cluster_skip = 0.0
        self.__last_name = ""
        self.__first_name = ""
        self.__number = 0
        self.__chat_id = ""
        self.__icon = ""
        self.__name = ""
        self.__public_key = ""
        self.__vote_key = ""
        self.__queue_number = 0
        self.__skip = 0.0
        self.__cluster_skip = 0.0
        self.__stake = 0.0
        self.__leader = 0
        self.__leader_all = 0
        self.__activation = 0.0
        self.__d_stake = 0.0
        self.__balance = 0.0
        self.__vote_balance = 0.0
        self.__epoch_num = 0
        self.__epoch_percent = 0.0
        self.__epoch_end = ""
        self.__version = ""
        self.__ip = ""
        self.__delinquent = False

    def set_cluster(self, cluster):
        self.__cluster = cluster
        if cluster == 't':
            self.__max_cluster_skip = 30.0
        elif cluster == 'm':
            self.__max_cluster_skip = 20.0

    def load_queue_number(self):
        tmp = get_queue_number(self.__public_key)
        self.__queue_number = tmp

    def set_number(self, number):
        self.__number = number

    def set_first_name(self, firstname):
        self.__first_name = firstname

    def set_last_name(self, lastname):
        self.__last_name = lastname

    def set_public_key(self, public_key):
        self.__public_key = public_key

    def set_vote_key(self, vote_key):
        self.__vote_key = vote_key

    def set_skip(self, skip):
        self.__skip = skip

    def set_cluster_skip(self, cluster_skip):
        self.__cluster_skip = cluster_skip

    def set_stake(self, stake):
        self.__stake = stake

    def set_leader(self, leader):
        self.__leader = leader

    def set_leader_all(self, leader_all):
        self.__leader_all = leader_all

    def set_activation(self, activation):
        self.__activation = activation

    def set_d_stake(self, d_stake):
        self.__d_stake = d_stake

    def set_balance(self, balance):
        self.__balance = balance

    def set_vote_balance(self, vote_balance):
        self.__vote_balance = vote_balance

    def set_epoch_num(self, epoch_num):
        self.__epoch_num = epoch_num

    def set_epoch_percent(self, epoch_percent):
        self.__epoch_percent = epoch_percent

    def set_epoch_end(self, epoch_end):
        self.__epoch_end = epoch_end

    def set_version(self, version):
        self.__version = version

    def set_ip(self, ip):
        self.__ip = ip

    def set_delinquent(self, delinquent):
        self.__delinquent = delinquent

    def send(self):
        if self.__cluster == 't':
            if self.__delinquent:
                self.__send_test_network(constant.T_CHAT_ALARM, constant.T_CHAT_ALARM_EK, constant.T_CHAT_ALARM_SIA, self.__first_name)
            elif self.__skip > (self.__cluster_skip + self.__max_cluster_skip) and self.__epoch_percent > 25.00:  # and self.__queue_number is not None:
                self.__send_test_network(constant.T_CHAT_ALARM, constant.T_CHAT_ALARM_EK, constant.T_CHAT_ALARM_SIA, self.__first_name)
            self.__send_test_network(constant.T_CHAT_COMMON, constant.T_CHAT_EK, constant.T_CHAT_SIA, self.__first_name)
        elif self.__cluster == 'm':
            if self.__delinquent:
                self.__send_main_network(constant.M_CHAT_ALARM, constant.M_CHAT_ALARM_EK, self.__first_name)
            elif self.__is_skip() and self.__epoch_percent > 25.00:  # and self.__queue_number is not None:
                self.__send_main_network(constant.M_CHAT_ALARM, constant.M_CHAT_ALARM_EK, self.__first_name)
            elif self.__is_balance():
                self.__send_main_network(constant.M_CHAT_ALARM, constant.M_CHAT_ALARM_EK, self.__first_name)
            self.__send_main_network(constant.M_CHAT_COMMON, constant.M_CHAT_EK, self.__first_name)

    def __send_test_network(self, id_common, id_ek, id_sia, name_group):
        self.__send(id_common, True)
        if name_group == 'EK':
            self.__send(id_ek, False)
        elif name_group == 'SIA':
            self.__send(id_sia, False)

    def __send_main_network(self, id_common, id_ek, name_group):
        self.__send(id_common, True)
        if name_group == 'EK':
            self.__send(id_ek, False)

    def __get_ico(self):
        if self.__delinquent:
            return u'\U0001f534'
        if self.__is_skip():
            return u'\U0001f536'
        if self.__skip == "null":
            return u'\U0001f536'
        if self.__ip == "":
            return u'\u2753'
        if self.__is_balance():
            return u'\U0001f536'
        return u'\u2705'

    def __is_skip(self):
        return self.__skip >= (self.__cluster_skip + self.__max_cluster_skip)

    def __is_balance(self):
        return self.__balance < constant.MIN_BALANCE

    def __get_message_body(self, is_number):
        w = ""
        if self.__is_skip():
            w = f"Skip > cluster+{self.__max_cluster_skip}%\n"

        if self.__delinquent == 'true':
            w += "Delinquent!\n"

        if self.__is_balance():
            w += "Balance!\n"

        cl = ""
        if self.__cluster == 'm':
            cl = "Main."
        elif self.__cluster == 't':
            cl = "TdS."

        if self.__first_name == self.__last_name:
            self.__name = self.__first_name
        else:
            self.__name = f"{self.__first_name}-{self.__last_name}"

        self.__icon = self.__get_ico()
        icon_money = u'\U0001f4b8'
        icon_ready_main = u'\U0001f4a5'

        if is_number:
            body = f'{ self.__icon } <b>{ self.__number }. { cl } { w }</b>[{ self.__name }] <b>{ self.__public_key[:7] }</b>'
        else:
            body = f'{ self.__icon } <b>[{ self.__last_name }] { self.__public_key[:7] }</b>'

        if self.__cluster == 't':
            if self.__queue_number is None:
                body += f' [ main ]'
            elif self.__queue_number <= 25:
                body += f' [ { icon_ready_main } { self.__queue_number } ]'
            else:
                body += f' [ { self.__queue_number } ]'

        body += "\n"
        body += f'<b>Skip</b>: { self.__skip }, <b>cluster skip</b>: { self.__cluster_skip }\n'
        body += f'<b>Stake</b>: { self.__stake }, <b>leader</b>: { self.__leader } [{ self.__leader_all }]\n'
        body += f'<b>Activating</b>: { self.__activation }, <b>deactivating</b>: { self.__d_stake }\n'
        body += f'<b>Balance</b>: { self.__balance } { 	icon_money }'
        if self.__cluster == 'm':
            body += f', <b>vote</b>: {self.__vote_balance} { icon_money }'
        body += f'\n'
        body += f'<b>Epoch</b>: { self.__epoch_num }, { self.__epoch_percent }%, { self.__epoch_end }\n'
        body += f'<b>Version</b>: { self.__version }, <b>IP</b>: <u>{ self.__ip }</u>'
        return body

    def __send(self, chat_id, is_number):
        body = self.__get_message_body(is_number)
        send_msg_telegram(constant.TELEGRAM_TOKEN, chat_id, body)
