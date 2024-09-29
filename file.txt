#include <iostream>
#define print printf
#define EXIT 0;

int main(void){
    for(int i=0; i<256; i++){
        print("ID %i Hello, World!\n", i);
    }
    return EXIT
}