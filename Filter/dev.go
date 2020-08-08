// +build dev

package main

import "C"

func main() {
	test(C.CString("I hat‏e‏ ass"), true)
	test(C.CString("Ắ  ‏   ‏‏ṧ ‏Ṡ"), true)
	test(C.CString("assassin"), false)
	test(C.CString("jackass"), true)
	test(C.CString("cocktail"), false)
	test(C.CString("cockroach"), false)
	test(C.CString("Penistone"), false)
	test(C.CString("assassin"), false)
	test(C.CString("bass"), false)
	test(C.CString("snigger"), false)
	test(C.CString("b"), false)
	test(C.CString("cоcktаil"), false)
	test(C.CString("cοcktaіl"), false)
	test(C.CString("Реnistоne"), false)
	test(C.CString("Ρenistοne"), false)
	test(C.CString("аssаssin"), false)
	test(C.CString("bаss"), false)
	test(C.CString("sniggеr"), false)
	test(C.CString("Аss"), true)
	test(C.CString("SHIT"), true)
	test(C.CString("a"), false)
	test(C.CString("ls.h.i.t.l"), true)
	test(C.CString("\ufffd\u041d\ufffd\u041eIST MY ROLE"), true)

	test(C.CString("Assassins are cool tho"), false)
}
