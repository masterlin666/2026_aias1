CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -pedantic

TARGET = emulator
TESTS = $(wildcard test_assembly/*.txt) test_m_ext.txt

.PHONY: all test clean

all: $(TARGET)

$(TARGET): emulator.cpp
	$(CXX) $(CXXFLAGS) emulator.cpp -o $(TARGET)

test: $(TARGET)
	@for test in $(TESTS); do \
		echo "=== $$test ==="; \
		./$(TARGET) $$test; \
		echo; \
	done

clean:
	rm -f $(TARGET)
