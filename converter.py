Blocks = {
	"!": "0000",
	" ": "0010",
	"@": "0011",
	"#": "0100",
	"$": "0101",
	".": "0110",
	"*": "0111",
	"+": "1000"
}

def bitstring_to_bytes(s):
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])

with open("Put a file here!", "r") as f:
	data = f.readlines()

started = False
lvl_num = 1

for line in data:
	if line[0] == ";":
		if started:
			for x in lvl:
				for y in x:
					lvl_binary += Blocks[y]
				lvl_binary += "0000"
			if len(lvl_binary) % 8:
				lvl_binary += "0000"
			print(lvl_binary)
			to_write = bitstring_to_bytes(lvl_binary)
			with open(str(lvl_num).zfill(3) + ".lvl", "w+b") as out:
				out.write(to_write)
			lvl_num += 1
			lvl = []
			lvl_binary = ""
		else:
			started = True
			lvl = []
			lvl_binary = ""
	elif line.rstrip():
		lvl += [line.rstrip()]

