// +build dev

package main

func main() {
	test("I hat‏e‏ ass", true)
	test("Ắ  ‏   ‏‏ṧ ‏Ṡ", true)
	test("assassin", false)
	test("jackass", true)
	test("cocktail", false)
	test("cockroach", false)
	test("Penistone", false)
	test("assassin", false)
	test("bass", false)
	test("snigger", false)
	test("b", false)
	test("cоcktаil", false)
	test("cοcktaіl", false)
	test("Реnistоne", false)
	test("Ρenistοne", false)
	test("аssаssin", false)
	test("bаss", false)
	test("sniggеr", false)
	test("Аss", true)
	test("SHIT", true)
	test("a", false)
	test("ls.h.i.t.l", true)
	test("\ufffd\u041d\ufffd\u041eIST MY ROLE", true)

	test("Assassins are cool tho", false)
}
