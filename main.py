import json
import os
import os.path
import glob
import re

import constant
from loader_files import Loader
from querydata import QueryData


def get_validator_info(pub_key):
    skip = 0.0
    account = ""
    version = ""
    delinquent = ""
    path = os.path.join(constant.CURRENT_DIR, 'files/validators.json')
    if os.path.isfile(path):
        file_json = open(path)
        data_json = json.load(file_json)
        for i in data_json['validators']:
            if i['identityPubkey'] == pub_key:
                skip = i['skipRate']
                account = i['voteAccountPubkey']
                version = i['version']
                delinquent = i['delinquent']
                break
        file_json.close()
        if skip is None:
            skip = 0.0
    return [round(skip, 2), account, version, delinquent]


def get_avg_skip_rate():
    skip = 0.0
    path = os.path.join(constant.CURRENT_DIR, 'files/validators.json')
    if os.path.isfile(path):
        file_json = open(path)
        data_json = json.load(file_json)
        skip = data_json['averageStakeWeightedSkipRate']
        file_json.close()
    return skip


def write_stake_file(vote_address):
    path = os.path.join(constant.CURRENT_DIR, 'files/stake_' + vote_address + '.json')
    with open(path, 'w') as f_stake:
        f_stake.write(loader.get_stake(vote_address))
    f_stake.close()


def get_list_stakes(vote_address):
    active_stake = 0
    activating_stake = 0
    deactivating_stake = 0
    path = os.path.join(constant.CURRENT_DIR, 'files/stake_' + vote_address + '.json')
    if os.path.isfile(path):
        file_json = open(path)
        data_json = json.load(file_json)
        for i in data_json:
            if 'activeStake' in i:
                active_stake += i['activeStake']
            if 'activatingStake' in i:
                activating_stake += i['activatingStake']
            if 'deactivatingStake' in i:
                deactivating_stake += i['deactivatingStake']
        file_json.close()
        active_stake /= 1000000000
        activating_stake /= 1000000000
        deactivating_stake /= 1000000000
        active_stake = round(active_stake, 1)
        activating_stake = round(activating_stake, 1)
        deactivating_stake = round(deactivating_stake, 1)
    return [active_stake, activating_stake, deactivating_stake]


def get_leader_all(pub_key):
    j = 0
    path = os.path.join(constant.CURRENT_DIR, 'files/leader_schedule.json')
    if os.path.isfile(path):
        file_json = open(path)
        data_json = json.load(file_json)
        for i in data_json['leaderScheduleEntries']:
            if i['leader'] == pub_key:
                j += 1
        file_json.close()
    return j


def get_leader_current(pub_key):
    j = 0
    path = os.path.join(constant.CURRENT_DIR, 'files/block_production.json')
    if os.path.isfile(path):
        file_json = open(path)
        data_json = json.load(file_json)
        for i in data_json['individual_slot_status']:
            if i['leader'] == pub_key:
                j += 1
        file_json.close()
    return j


def get_epoch_info():
    number = []
    percent = []
    completed_time = ""
    path = os.path.join(constant.CURRENT_DIR, 'files/epoch.txt')
    if os.path.isfile(path):
        with open(path, 'r') as file_e:
            for ln in file_e:
                list_w = ln.split(sep=':')
                if list_w[0] == "Epoch":
                    number = [int(s) for s in re.findall(r'-?\d+\.?\d*', list_w[1])]
                if list_w[0] == "Epoch Completed Percent":
                    percent = [float(s) for s in re.findall(r'-?\d+\.?\d*', list_w[1])]
                if list_w[0] == "Epoch Completed Time":
                    sw = re.findall(r'\(([^)]+)\)', list_w[1])
                    completed_time = str(sw[0]).replace(' remaining', '')[:-3].strip()
        file_e.close()
    return [number[0], percent[0], completed_time]


def get_ip(pub_key):
    ip = ""
    path = os.path.join(constant.CURRENT_DIR, 'files/gossip.json')
    if os.path.isfile(path):
        file_json = open(path)
        data_json = json.load(file_json)
        for i in data_json:
            if i['identityPubkey'] == pub_key:
                ip = i['ipAddress']
                break
        file_json.close()
    return ip


loader = Loader()

print("Remove old files.")
path_files = os.path.join(constant.CURRENT_DIR, 'files')
for file in glob.glob(path_files + "/*"):
    os.remove(file)

print("Loading new files.")
path_files = os.path.join(constant.CURRENT_DIR, 'files/validators.json')
with open(path_files, 'w') as f_validators:
    f_validators.write(loader.get_validators())
f_validators.close()

path_files = os.path.join(constant.CURRENT_DIR, 'files/gossip.json')
with open(path_files, 'w') as f_gossip:
    f_gossip.write(loader.get_gossip())
f_gossip.close()

path_files = os.path.join(constant.CURRENT_DIR, 'files/leader_schedule.json')
with open(path_files, 'w') as f_leader_schedule:
    f_leader_schedule.write(loader.get_leader_schedule())
f_leader_schedule.close()

path_files = os.path.join(constant.CURRENT_DIR, 'files/block_production.json')
with open(path_files, 'w') as f_block_production:
    f_block_production.write(loader.get_block_production())
f_block_production.close()

path_files = os.path.join(constant.CURRENT_DIR, 'files/epoch.txt')
with open(path_files, 'w') as f_epoch:
    f_epoch.write(loader.get_epoch())
f_epoch.close()

avg_skip = round(float(get_avg_skip_rate()), 2)
list_epoch = get_epoch_info()

print("Collecting information.")
path_files = os.path.join(constant.CURRENT_DIR, 'addresses.txt')
with open(path_files, 'r') as f:
    for line in f:
        list_word = line.split()
        q = QueryData()
        q.set_number(list_word[0])
        q.set_first_name(list_word[2])
        q.set_last_name(list_word[3])
        info_validator = get_validator_info(list_word[1])
        q.set_delinquent(info_validator[3])
        q.set_public_key(list_word[1])
        vote_key = info_validator[1]
        q.set_vote_key(vote_key)
        q.load_queue_number()
        q.set_skip(info_validator[0])
        q.set_cluster_skip(avg_skip)
        q.set_leader_all(get_leader_all(list_word[1]))
        q.set_leader(get_leader_current(list_word[1]))
        if vote_key != '':
            write_stake_file(vote_key)
            lst = get_list_stakes(vote_key)
            q.set_stake(lst[0])
            q.set_activation(lst[1])
            q.set_d_stake(lst[2])
        q.set_balance(loader.get_balance(list_word[1]))
        q.set_version(info_validator[2])
        q.set_epoch_num(list_epoch[0])
        q.set_epoch_percent(list_epoch[1])
        q.set_epoch_end(list_epoch[2])
        q.set_ip(get_ip(list_word[1]))
        q.send()
f.close()

print("Done!!!")
