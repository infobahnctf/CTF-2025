// log.c
#include <stdio.h>
#include <stdlib.h>
#include <syslog.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <regex.h>

void* cleaner(void* s, int c, size_t n) {
    openlog("cleaner_wrapper", LOG_PID, LOG_USER);
    syslog(LOG_INFO, "ACTION: Clearing %zu bytes at address %p", n, s);
    closelog();
    return memset(s, c, n);
}

long long convert(char* age) {
    errno = 0;
    long long ll_age;
    char *endptr;
    ll_age = strtoull(age, &endptr, 10);
    if (errno == ERANGE) {
        printf("Error.");
    } else if (*endptr != '\0') {
        printf("Error!");
    }
    return ll_age;
}

char age[16];

int main(int argc, char *argv[]) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    char username[1000];
    void* (*cleaner_ptr)(void*, int, size_t) = cleaner;
    cleaner_ptr(username, 0, sizeof(username));

    char *cli_username = NULL;
    char *cli_age = NULL;
    int opt;

    while ((opt = getopt(argc, argv, "u:a:")) != -1) {
        switch (opt) {
        case 'u':
            cli_username = optarg;
            break;
        case 'a':
            cli_age = optarg;
            break;
        default:
            fprintf(stderr, "Usage: %s -u username -a age\n", argv[0]);
            return 1;
        }
    }

    if (!cli_username || !cli_age) {
        fprintf(stderr, "Usage: %s -u username -a age\n", argv[0]);
        return 1;
    }

    strncpy(username, cli_username, sizeof(username) - 1);
    username[sizeof(username) - 1] = '\0';

    regex_t regex_obj;
    int ret = regcomp(&regex_obj, "^[[:print:]]+$", REG_EXTENDED);
    if (ret) {
        printf("Error: Could not compile regex.\n");
        return 1;
    }

    ret = regexec(&regex_obj, username, 0, NULL, 0);
    if (ret == REG_NOMATCH) {
        printf("Error: Username contains non-printable characters.\n");
        regfree(&regex_obj);
        return 1;
    } else if (ret != 0) {
        printf("Error: Regex match failed.\n");
        regfree(&regex_obj);
        return 1;
    }
    regfree(&regex_obj);

    strncpy(age, cli_age, sizeof(age) - 1);
    age[sizeof(age) - 1] = '\0';

    openlog("chall", LOG_PID, LOG_USER);
    long long ll_age;
    ll_age = convert(age);
    char *log = (char *)malloc(1100 * sizeof(char));
    if (!log) {
        perror("malloc");
        closelog();
        return 1;
    }

    snprintf(log, 1030, "{'username':'%s','age':%lld}", username, ll_age);
    syslog(5, log);

    free(log);
    closelog();
}


