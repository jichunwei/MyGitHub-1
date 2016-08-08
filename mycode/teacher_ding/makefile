
CC = gcc -g -Wall 
bin/mmath_test:obj/mmath_test.o obj/mmath.o
	${CC} obj/mmath_test.o obj/mmath.o -o  bin/mmath_test

obj/mmath_test.o:mmath_test.s
	${CC} -c mmath_test.s -o obj/mmath_test.o

obj/mmath.o:mmath.s
	${CC} -c mmath.s -o obj/mmath.o

mmath_test.s:mmath_test.i
	${CC} -S mmath_test.i -o mmath_test.s

mmath.s:mmath.i
	${CC} -S mmath.i -o mmath.s

mmath_test.i:include/mmath.h src/mmath_test.c
	${CC} -E -I./include src/mmath_test.c -o mmath_test.i

mmath.i :include/mmath.h src/mmath.c
	${CC} -E -I./include src/mmath.c -o mmath.i

clean:
	rm -fr *.i *.s
