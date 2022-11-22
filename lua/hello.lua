local c = 0

function hello(msg)
	print("Hello "..msg)
	c = c + 1
end

hello("World")
hello(c)
hello(c)
