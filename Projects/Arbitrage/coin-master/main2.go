package main

import (
	"fmt"
	"github.com/lemtree/coin/huobi"
)

func main() {
	c := huobi.NewHuobiClient()

	// 获取我的账户信息,需要在火币网获取访问秘钥,然后设置你的API key
	c.SetApiKey("your-access-key", "your-secret-key")

	accountInfo, err := c.GetAccountInfo()
	if err != nil {
		fmt.Println(err.Error())
	} else {
		fmt.Printf("我的资产：%+v", accountInfo)
	}
}