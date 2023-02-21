#-----------------------------------------------------------------------#
#- GLOBAL DEFS ---------------------------------------------------------#
#-----------------------------------------------------------------------#

# Keep this as generic as possible.

NAME=solver
VERSION=

#-----------------------------------------------------------------------#
# Solver signatures have to be both valid file names and C symbols.

SIG=$(NAME)$(VERSION)
TARGET=libipafair$(SIG).so

#-----------------------------------------------------------------------#

CC=g++
CFLAGS=-Wall -DNDEBUG -O3 -std=c++17 -fPIC

AF_SOLVER?=/Users/andreasn/mu-toksia/mu-toksia
CFLAGS+=-DEXTERNAL_AF_SOLVER=\"$(AF_SOLVER)\"

#-----------------------------------------------------------------------#
#- REQUIRED TOP RULES --------------------------------------------------#
#-----------------------------------------------------------------------#

all: $(TARGET)

clean:
	rm -f *.o *.so

#-----------------------------------------------------------------------#
#- INVISIBLE INTERNAL SUB RULES ----------------------------------------#
#-----------------------------------------------------------------------#

$(NAME).o: $(NAME).cpp ipafair.h makefile
	$(CC) $(CFLAGS) -c $(NAME).cpp

$(TARGET): $(NAME).o
	$(CC) -shared -o $(TARGET) $(NAME).o
