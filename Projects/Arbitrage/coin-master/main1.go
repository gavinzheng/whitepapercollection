package main

import (
	"./huobi"
	"fmt"
)

func main() {
	c := huobi.NewHuobiClient()

	//获取BTC-CNY行情，返回解析好的struct
	QuoData, err := c.Quotation(huobi.COIN_BTC, huobi.CURRENCY_CNY)
	checkError(err)
	fmt.Printf("当前BTC-CNY报价(golang struct)：%+v \r\n", QuoData)

	//获取BTC-CNY行情，返回火币api的原始JSON
	jsonBlob, err := c.QuotationJson(huobi.COIN_BTC, huobi.CURRENCY_CNY)
	checkError(err)
	fmt.Print("当前BTC-CNY报价(火币API原始json)：", string(jsonBlob))

}

func checkError(err error) {
	if err != nil {
		fmt.Println(err.Error())
	}
}
