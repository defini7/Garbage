#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

int main(int argc, char* argv[])
{
    if (argc != 2)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    for (int j = 0, n = strlen(argv[1]); j < n; j++)
    {
        if (!isdigit(argv[1][j]))
        {
            printf("Usage: ./caesar key\n");
            return 1;
        }
    }

    int k = atoi(argv[1]);
    if (k < 1)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    printf("plaintext (max 128 chars): ");

    char code[128];
    scanf("%s", code);

    printf("ciphertext: ");

    int len = strlen(code);
    for (int i = 0; i < len; i++)
    {
        int out = code[i];

        if (islower(code[i]))
            out = (out + k - 97) % 26 + 97;
        else if (isupper(code[i]))
            out = (out + k - 65) % 26 + 65;

        putchar(out);
    }
    
    putchar('\n');
    return 0;
}
