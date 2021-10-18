#include <iostream>
#include <ctime>

int main() {
    srand(std::time(0));
    std::cout << 1 + rand() % 10;
}
