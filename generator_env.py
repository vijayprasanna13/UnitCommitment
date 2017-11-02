
loads =[360, 204, 369, 340, 101, 565, 609, 479, 248, 261, 541, 286, 502, 570, 194, 407, 369, 521, 178, 379, 214, 109, 166, 253]

generators = []

generators.append({
	"index":1 ,"p_max":150, "p_min":10, "a":200, "b":3, "c":0.05, "startup_cost":1000
})


generators.append({
	"index":2 ,"p_max":250, "p_min":20, "a":300, "b":3, "c":0.04, "startup_cost":2000
})

generators.append({
	"index":3 ,"p_max":300, "p_min":30, "a":100, "b":2, "c":0.02, "startup_cost":3000
})