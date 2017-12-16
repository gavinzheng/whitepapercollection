cd "/Users/phil/work/X-work/xrypto/"

insheet using "snapshot_ALL_balance.csv", clear

gen datetime = timestamp*1000 + Clock("1 Jan 1970", "DMY")+ Clock("08:00", "hm")
format %tCDD/HH:MM datetime

graph twoway line total_btc datetime, yaxis(1) || connected total_bch datetime, yaxis(2) 
