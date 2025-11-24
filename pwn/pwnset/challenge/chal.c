#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>

#define MAX_USERS 128

struct User {
    char username[1000];
    long long age;
};

static struct User users[MAX_USERS];
static size_t user_count = 0;

static int age_exists(long long age) {
    for (size_t i = 0; i < user_count; i++) {
        if (users[i].age == age) {
            return 1;
        }
    }
    return 0;
}

static void add_user(const char *username, long long age) {
    if (user_count >= MAX_USERS) {
        return;
    }
    strncpy(users[user_count].username, username,
            sizeof(users[user_count].username) - 1);
    users[user_count].username[sizeof(users[user_count].username) - 1] = '\0';
    users[user_count].age = age;
    user_count++;
}

static int find_age_by_username(const char *username, long long *age_out) {
    for (size_t i = 0; i < user_count; i++) {
        if (strcmp(users[i].username, username) == 0) {
            *age_out = users[i].age;
            return 0;
        }
    }
    return -1;
}

static int parse_age(const char *s, long long *out) {
    errno = 0;
    char *end;
    long long val = strtoll(s, &end, 10);
    if (errno == ERANGE || *end != '\0' || val < 0) {
        return -1;
    }
    *out = val;
    return 0;
}

void init() {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

int main(void) {
    init();
    int choice;
    char username[1000];
    char age_str[16];

    for (;;) {
        printf("Select your options:\n");
        printf("1. register username\n");
        printf("2. get age\n");
        printf("3. exit\n");
        printf("> ");

        if (scanf("%d", &choice) != 1) {
            return 0;
        }

        if (choice == 1) {
            printf("Enter your username: ");
            if (scanf("%999s", username) != 1) {
                return 0;
            }
            printf("Enter your age: ");
            if (scanf("%15s", age_str) != 1) {
                return 0;
            }

            long long age_val;
            if (parse_age(age_str, &age_val) != 0) {
                printf("Invalid age\n");
                continue;
            }

            if (age_exists(age_val)) {
                printf("A user already has this age\n");
            }

            pid_t pid = fork();
            if (pid == -1) {
                perror("fork");
                return 1;
            } else if (pid == 0) {
                execl("./log", "log", "-u", username, "-a", age_str, (char *)NULL);
                perror("execl");
                _exit(1);
            } else {
                int status;
                waitpid(pid, &status, 0);
            }

            add_user(username, age_val);

        } else if (choice == 2) {
            printf("Enter username to look up: ");
            if (scanf("%999s", username) != 1) {
                return 0;
            }
            long long found_age;
            if (find_age_by_username(username, &found_age) == 0) {
                printf("%s is %lld years old\n", username, found_age);
            } else {
                printf("No age found for %s\n", username);
            }

        } else if (choice == 3) {
            return 0;
        } else {
            printf("Invalid choice\n");
        }
    }
}


