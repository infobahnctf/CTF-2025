#include <stdio.h>
#include <stdlib.h>

int main(void) {
    const char *path = "/flag.txt";
    FILE *f = fopen(path, "r");
    if (!f) {
        perror("open");
        return 1;
    }
    int c;
    while ((c = fgetc(f)) != EOF) putchar(c);
    fclose(f);
    return 0;
}