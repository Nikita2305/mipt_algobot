#include <iostream>
#include <time.h>

int main() {
    clock();
    srand(10 * time(0) + clock()); // To make it more randomized
    std::cout << 1 + rand() % 2;
}
