build:
	buildozer android debug

copy:
	cp *.py ~/Code/ssgb/duel/ -f
	cp *.kv ~/Code/ssgb/duel/ -f
	cp *.spec ~/Code/ssgb/duel/ -f
	cp Makefile ~/Code/ssgb/duel/ -f
