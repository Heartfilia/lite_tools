package main

import (
	"fmt"
	"strconv"
)

func in(target string) bool {
	str_array := []string{"嗷", "呜", "啊", "~"}
	for _, element := range str_array {
		if target == element {
			return true
		}
	}
	return false
}

func judge_mode(s []rune) int {
	// 0 输入  1 解析

	for _, each_s := range s {
		// fmt.Printf("[%d] %d --> %s\n", ind, each_s, string(each_s))
		result := in(string(each_s))

		if result == false {
			return 0
		}
	}
	return 1
}

func Hex2Dec(val string) int {
	n, err := strconv.ParseUint(val, 16, 32)
	if err != nil {
		fmt.Println(err)
	}
	return int(n)
}

func RoarEncode(s string) string {
	str_array := []string{"嗷", "呜", "啊", "~"}
	d := ""
	ss := []rune(s)
	for ind := range ss {
		d = fmt.Sprintf("%s%04x", d, ss[ind])
	}

	b := ""
	for ind, char := range d {
		c := Hex2Dec(string(char)) + ind%16
		if 16 <= c {
			c -= 16
		}
		b = fmt.Sprintf("%s%s%s", b, str_array[c/4], str_array[c%4])
	}
	result := fmt.Sprintf("%s%s%s%s%s", str_array[3], str_array[1], str_array[0], b, str_array[2])
	return result
}

func RoarDecode(s string) string {
	str_array := []string{"嗷", "呜", "啊", "~"}
	if 4 > len([]rune(s)) {
		return ""
	}
	s = string([]rune(s)[3 : len([]rune(s))-1])

	d := ""
	for ind := range []rune(s) {
		e := 0

		if ind%2 == 0 {
			e = ind
		} else {
			continue
		}
		f := 0
		g := ""
		b := []rune(s)

		for {
			g = string(b[e])
			if 3 >= f && g != str_array[f] {
				f++
				g = string(b[e])
				continue
			} else {
				break
			}
		}

		// fmt.Printf("[1]g= %s    e= %d\n", g, e)
		h := 0
		for {
			g = string(b[e+1])
			if 3 >= h && g != str_array[h] {
				h++
				g = string(b[e+1])
				continue
			} else {
				break
			}
		}

		gn := 4*f + h - (e/2)%16
		if 0 > gn {
			gn += 16
		}
		d = fmt.Sprintf("%s%x", d, gn)
	}

	a := ""
	i := 0
	for b := 4; b <= len(d); b += 4 {
		te := d[i:b]
		che := string(rune(Hex2Dec(te)))
		a = fmt.Sprintf("%s%s", a, che)
		i += 4
	}

	return a
}

func circle_run() {
	var input_str string
	var string_info []rune

	for {
		fmt.Print("说>>> ")
		_, err := fmt.Scanln(&input_str)
		if err != nil {
			return
		}

		string_info = []rune(input_str)
		mode := judge_mode(string_info)
		if mode == 0 {

			fmt.Println("输入:", RoarEncode(input_str)) // 当前是输入模式
		} else {
			fmt.Println("翻译:", RoarDecode(input_str)) // 当前是翻译模式
		}
		fmt.Println("-----------------------------------------------------------------------------")
	}
}

func main() {
	fmt.Println("基于与熊论道兽音板块制作而成[http://hi.pcmoe.net/roar.html] MadeBy:Heartfilia")
	fmt.Println()
	circle_run()
	// result := RoarEncode("测试一下a")
	// result := RoarDecode("~呜嗷呜啊~啊呜啊~啊~嗷嗷嗷嗷~~嗷~嗷呜~啊啊啊~嗷嗷啊~~啊啊啊嗷嗷嗷呜啊嗷呜嗷啊")
	// fmt.Println(result)
}
