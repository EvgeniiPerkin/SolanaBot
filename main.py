import json
import os
import os.path
import glob
import re
import logging
import subprocess
import sys
import argparse

import constant
from querydata import QueryData

# Arguments
parser = argparse.ArgumentParser(description='Solana telegram bot')
parser.add_argument('-c', '--cluster', default='t', type=str,
                    help='type of cluster - m(main) or t(test))')
parser.add_argument("-v", "--verbose", help="increase output verbosity to DEBUG", action="store_true")
args = parser.parse_args()

# Logging
SOLANA_CLUSTER = args.cluster
if SOLANA_CLUSTER != 't' and SOLANA_CLUSTER != 'm':
    sys.exit()

logging.getLogger('urllib3').setLevel(logging.WARNING)
if args.verbose:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(f'{constant.CURRENT_DIR}/bot_{SOLANA_CLUSTER}.log'),
            logging.StreamHandler(sys.stdout),
        ]
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(f'{constant.CURRENT_DIR}/bot_{SOLANA_CLUSTER}.log'),
            logging.StreamHandler(sys.stdout),
        ]
    )
logger = logging.getLogger(__name__)


def get_balance(pub_key):
    process = subprocess.run([constant.SOLANA_PATH, 'balance', pub_key, f'-u{SOLANA_CLUSTER}'],
                             stdout=subprocess.PIPE,
                             universal_newlines=True)

    balance_txt = process.stdout
    balance_txt = balance_txt.replace(' SOL', '')
    return round(float(balance_txt), 2)


def run_task(_cmd, full_name_file):
    try:
        process = subprocess.run(_cmd, shell=True, bufsize=1, universal_newlines=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

        with open(full_name_file, 'w') as fl:
            fl.write(process.stdout)
        fl.close()

        logger.debug(f"Write to file:{full_name_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error write file:{full_name_file} | {e.output} | {e.returncode}")


def get_validator_info(pub_key):
    skip = 0.0
    account = ""
    version = ""
    delinquent = ""
    path = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/validators.json')
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
    path = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/validators.json')
    if os.path.isfile(path):
        file_json = open(path)
        data_json = json.load(file_json)
        skip = data_json['averageStakeWeightedSkipRate']
        file_json.close()
    return skip


def get_list_stakes(vote_address):
    active_stake = 0
    activating_stake = 0
    deactivating_stake = 0
    path = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/stake_' + vote_address + '.json')
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
    path = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/leader_schedule.json')
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
    path = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/block_production.json')
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
    path = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/epoch.txt')
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
    path = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/gossip.json')
    if os.path.isfile(path):
        file_json = open(path)
        data_json = json.load(file_json)
        for i in data_json:
            if i['identityPubkey'] == pub_key:
                ip = i['ipAddress']
                break
        file_json.close()
    return ip


logger.info("Remove old files_t.")
path_files = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}')
for file in glob.glob(path_files + "/*"):
    os.remove(file)

logger.info("Loading new files_t.")
cmd = f"{ constant.SOLANA_PATH } -u{ SOLANA_CLUSTER } validators --output json-compact"
path_files = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/validators.json')
run_task(cmd, path_files)

path_files = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/gossip.json')
cmd = f"{ constant.SOLANA_PATH } -u{ SOLANA_CLUSTER } gossip --output json-compact"
run_task(cmd, path_files)

path_files = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/leader_schedule.json')
cmd = f"{ constant.SOLANA_PATH } -u{ SOLANA_CLUSTER } leader-schedule --output json-compact"
run_task(cmd, path_files)

path_files = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/block_production.json')
cmd = f"{ constant.SOLANA_PATH } -u{ SOLANA_CLUSTER } -v block-production --output json-compact"
run_task(cmd, path_files)

path_files = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/epoch.txt')
if SOLANA_CLUSTER == 't':
    cmd = f"{ constant.SOLANA_PATH } epoch-info"
else:
    cmd = f"{ constant.SOLANA_PATH } -u{ SOLANA_CLUSTER } epoch-info"
run_task(cmd, path_files)

avg_skip = round(float(get_avg_skip_rate()), 2)
list_epoch = get_epoch_info()

logger.info("Collecting information.")
path_files = os.path.join(constant.CURRENT_DIR, f'addresses_{SOLANA_CLUSTER}.txt')
with open(path_files, 'r') as f:
    for line in f:
        list_word = line.split()
        q = QueryData()
        q.set_cluster(SOLANA_CLUSTER)
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
            path_files = os.path.join(constant.CURRENT_DIR, f'files_{SOLANA_CLUSTER}/stake_{vote_key}.json')
            cmd = f"{constant.SOLANA_PATH} -u{SOLANA_CLUSTER} stakes {vote_key} --output json-compact"
            run_task(cmd, path_files)
            lst = get_list_stakes(vote_key)
            q.set_stake(lst[0])
            q.set_activation(lst[1])
            q.set_d_stake(lst[2])
        q.set_balance(get_balance(list_word[1]))
        q.set_version(info_validator[2])
        q.set_epoch_num(list_epoch[0])
        q.set_epoch_percent(list_epoch[1])
        q.set_epoch_end(list_epoch[2])
        q.set_ip(get_ip(list_word[1]))
        q.send()
f.close()

logger.info("Done!!!")
