#include <iostream>
#include <random>
#define print printf
#define EXIT 0;
#define py auto

using namespace std;

// TODO killing myself

int main(void){

    srand(455);

    for(int i=0; i<256; i++){
        print("ID %i Hello, World!\n", rand());
    }
    
    return EXIT
}