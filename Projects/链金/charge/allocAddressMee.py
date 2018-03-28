import json
from web3 import Web3, HTTPProvider, IPCProvider,eth
import sys,string
from DBUtils.PooledDB import PooledDB
import pymysql as mysql

coin_name = "ETH" #sys.argv[1]

database_config = None

with open("database.json",'r') as f:
    database_config = json.load(f)


print(database_config)


pool = PooledDB(mysql,host=database_config["Host"],
                             user=database_config["UserName"],
                             password=database_config["Password"],
                             db=database_config["DB"],
                             charset='utf8',
                             cursorclass=mysql.cursors.SSDictCursor,
                             setsession=['SET AUTOCOMMIT = 1'])

connection = pool.connection()


#连接 以太坊钱包  用户处理分配代币
web3 = Web3(IPCProvider())

coin = None

def addAddress(user_id):
    insert_conn = pool.connection()
    address = web3.personal.newAccount(password='ceshi123123')
    add_sql = "INSERT INTO `address_deposit_%s`(`user_id`,`coin_id`,`address`) VALUES (%s,%s,'%s');" % (coin_name.lower(),user_id, coin['id'], address)
    print(add_sql)
    cursor_insert= insert_conn.cursor()
    cursor_insert.execute(add_sql)
    cursor_insert.close()


#connection.autocommit(True)
try:
    cursor = connection.cursor()
    #with connection.cursor() as cursor:
    # 获取币的相关信息
    cursor.execute("SELECT * FROM `coins` WHERE name = %s;",(coin_name.lower()))
    coin = cursor.fetchone()

    if coin is None:
        print("%s not exist" % (coin_name))
        exit(1)
    cursor.fetchall()
    #查询哪些用户没有地址
    sql = "SELECT id,name FROM `users` WHERE id NOT IN (SELECT `user_id` FROM `address_deposit` WHERE `coin_id` = {0});".format(coin['id'])

    cursor.execute(sql)

    #循环处理
    while True:
        results = cursor.fetchone()
        if results is None:
            print("over")
            break
        print(results)
        #添加地址在这里处理
        addAddress(results['id'])
        #
    connection.commit()
    cursor.close()
finally:
    connection.rollback()

connection.close()
