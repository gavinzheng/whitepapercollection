from web3 import Web3, HTTPProvider, IPCProvider,eth
import sys,time
import erc20token
import json
from DBUtils.PooledDB import PooledDB
import pymysql as mysql
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

base = None

if r.get("ETH_BLOCK_NUMBER") is None:
    base = 4940200 #4927008
else:
    base = int(r.get("ETH_BLOCK_NUMBER"))
base = 4939264
print(base)

ETH_COIN = None

#Get Coin Name
coin_name = "ETH" #sys.argv[1]

#Connect to Ethereun Wallet
web3 = Web3(IPCProvider())

erc20token_config = None

current_block_number = web3.eth.blockNumber
print("latest block number =%s" % current_block_number)

#Get Database Configuration
database_config = None

with open("database.json",'r') as f:
    database_config = json.load(f)



#Create Database Connection pool
pool = PooledDB(mysql,host=database_config["Host"],
                             user=database_config["UserName"],
                             password=database_config["Password"],
                             db=database_config["DB"],
                             charset='utf8',
                             cursorclass=mysql.cursors.SSDictCursor,
                             setsession=['SET AUTOCOMMIT = 1'])

cfg_connection = pool.connection()



#Get Token Json
with open("token.json", 'r') as f:
    erc20token_config = json.load(f)



token_address = []
token_label = {}
token_coin = {}

for key in erc20token_config:
    token_address.append(erc20token_config[key]["address"].lower())
    token_label[erc20token_config[key]["address"].lower()] = key

    c = cfg_connection.cursor()
    sql = "SELECT `id`,`name` FROM `coins` where name = '{}'".format(key)
    c.execute(sql)

    coin = c.fetchone()
    if coin is None:
        continue

    token_coin[key] = coin


print(token_address)
print(token_label)
print(token_coin)
cfg_connection.close()

eth_conn = None

#################################################################################################################################
#Process Blocks
def handleLoadCoin(blocknumber):
    blockinfo = web3.eth.getBlock(blocknumber)

    iloop = 0
    print("######################################################## BLOCK = {0} TRANSACTION TOTAL={1}".format(base,len(blockinfo['transactions'])))
    #print(len(blockinfo['transactions']))
    for txid in blockinfo['transactions']:
        print('Block = %s Transaction ID=%s iloop=%s' % (blocknumber, txid, iloop))
        iloop = iloop + 1
        trans = web3.eth.getTransaction(txid)
        handleTransaction(trans, iloop)



##################################################################################################################################################

#Filter txid, based on ETH or ERC20
def handleTransaction(transactions, transactionno):
    if (transactions["to"] == None) :
        return
    else:
        to_address = transactions["to"].lower()

    #if ERC20 then call handleERC20token()
    if to_address in token_address:
        print("ERC20 tokens")
        #handleERC20Token(token_label[to_address],transactions)
        return

    #Charge ETH
    # print(to_address)
    handleETH(transactions,transactionno)

###################################################################################################################

def handleETH(transactions, transactionno):
    to_address = transactions["to"].lower()
    txid = transactions['hash'].lower()
    blockNumber = transactions['blockNumber']

    value = web3.fromWei(transactions['value'], 'ether')
    confirmations = current_block_number - blockNumber + 1

    table_name = "exchange_eth"
    try:
        eth_conn = pool.connection()
        eth_cursor = eth_conn.cursor()

        #1 if to address is platform address then it is charge
        sql = "SELECT `user_id` FROM `address_deposit_{1}` WHERE `address` = '{0}'".format(
            to_address, "eth")
        #print("sql=%s" % sql)
        eth_cursor.execute(sql)

        address_info = eth_cursor.fetchone()
        if address_info is None:
            return
        else :
            print("sql in range of platform=%s" % sql)
            print("to Address = %s" % to_address)
            if to_address == '0x9fd3582ec616e391324a2688376cb7aa53c400f4':
                print('Bingo!!! Joe account')
                print('BlockNumber = %s Value =%s to_address=%s' % (blockNumber, value, to_address))
                #exit(1)

        # print("{0} {1} {2} {3} {4}".format(from_address,to_address,blockNumber,value,hash))
        #3 Check Hash if existing

        # check if txid has been recorded
        sql = "SELECT `id`,`confirmations` FROM `exchange_eth` WHERE `txid` = '{0}' AND `opt_type` = 1;".format(txid)

        # print(sql)
        eth_cursor.execute(sql)

        exchange_result = eth_cursor.fetchone()

        eth_cursor.fetchall()

        #  if existing , then add record or update confirmations
        if exchange_result is None:
            insert_sql = "INSERT INTO {0}(`confirmations`,`address`,`user_id`,`number`,`number_u`,`opt_type`,`status`,`created_at`,`updated_at`,`txid`,`blocknumber`) VALUES ({1},'{2}',{3},{4},{5},{6},{7},{8},{9},'{10}','{11}')".format(
                table_name, confirmations, to_address, address_info["user_id"], value,value, 1, 1, int(time.time()), int(time.time()),txid,blockNumber)

            print("insert sql =%s" % insert_sql)
            eth_cursor.execute(insert_sql)
        else:
            update_sql = "UPDATE {0} SET `confirmations`={1} WHERE `id` = {2}".format(table_name, confirmations,exchange_result["id"])
            print("update_sql=%s" % update_sql)
            eth_cursor.execute(update_sql)

        eth_conn.commit()
        eth_cursor.close()
    except :
        eth_conn.rollback()
    finally:
        #eth_conn.rollback()
        eth_conn.close()
        #print("finally")
    return


###################################################################################################################3

# Process ERC20
def handleERC20Token(coin_name,transactions):

    txid = transactions['hash'].lower()
    blockNumber = transactions['blockNumber']


    coin = token_coin.get(coin_name)

    if coin is None:
        return

    confirmations = current_block_number - blockNumber + 1
    token = erc20token_config[coin_name]

    contractAddress = token["address"]
    abi = token["abi"]

    token_sdk = erc20token.SDK(provider=IPCProvider(), contract_address=contractAddress, contract_abi=abi)
    tx_data = token_sdk.get_transaction_data(txid)
    print("From {0} To {1} Send {2} {3} confirmations {4}".format(tx_data.from_address,tx_data.to_address,tx_data.token_amount,coin_name,tx_data.num_confirmations))


    erc20_conns = pool.connection()
    erc20_conn = erc20_conns.cursor()
    sql = "SELECT `user_id`,`coin_id` FROM `address_deposit` WHERE `address` = '{0}' AND coin_id = {1}".format(tx_data.to_address,coin['id'])
    # Check if address already in database
    erc20_conn.execute(sql)

    address_info = erc20_conn.fetchone()
    if address_info is None:
        return

    erc20_conn.fetchall()

    #check txid if recorded
    table_name = "exchange_{0}".format(coin_name.lower())

    sql = "SELECT `id`,`confirmations` FROM {0} WHERE `txid` = '{1}' AND `opt_type` = 1;".format(table_name,txid)

    erc20_conn.execute(sql)

    results = erc20_conn.fetchone()

    erc20_conn.fetchall()
    print(sql)
    #  If existing , then add record or update confirmations
    # if results is None:
    #     insert_sql = "INSERT INTO {0}(`confirmations`,`address`,`user_id`,`number`,`number_u`,`opt_type`,`status`,`created_at`,`updated_at`,`txid`,`blocknumber`) VALUES ({1},'{2}',{3},{4},{5},{6},{7},{8},{9},'{10}',{11})".\
    #         format(table_name,confirmations,tx_data.to_address,address_info["user_id"],tx_data.token_amount,tx_data.token_amount,1,1,int(time.time()),int(time.time()),txid,blockNumber)
    #     print(insert_sql)
    #     erc20_conn.execute(insert_sql)
    # else:
    #     update_sql = "UPDATE {0} SET `confirmations`={1} WHERE `id` = {2}".format(table_name,confirmations,results["id"])
    #     print(update_sql)
    #
    #     erc20_conn.execute(update_sql)

    erc20_conns.commit()
    erc20_conn.close()

################################################################################################################################################################################


try:
    connection = pool.connection()
    check = connection.cursor()
    sql = "SELECT `id`,`name` FROM `coins` WHERE name = 'ETH';"
    check.execute(sql)
    ETH_COIN = check.fetchone()
    connection.close()

    while base < current_block_number - 12:
        handleLoadCoin(base)
        base = base + 1
        r.set("ETH_BLOCK_NUMBER",base)
        #print("base = {}".format(base))

finally:
    #connection.close()
    exit(1)





