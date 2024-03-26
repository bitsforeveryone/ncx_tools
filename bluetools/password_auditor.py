import subprocess
import sys
import os

def main(passwd_path, shadow_path, wordlist_path):
    # Check if files exist
    if not os.path.exists(passwd_path):
        print(f"Error: Passwd file '{passwd_path}' does not exist.")
        return
    if not os.path.exists(shadow_path):
        print(f"Error: Shadow file '{shadow_path}' does not exist.")
        return
    if not os.path.exists(wordlist_path):
        print(f"Error: Wordlist file '{wordlist_path}' does not exist.")
        return

    # Run unshadow to combine passwd and shadow files
    unshadow_process = subprocess.Popen(['/sbin/unshadow', passwd_path, shadow_path], stdout=subprocess.PIPE)
    unshadow_output, _ = unshadow_process.communicate()

    #Write output to /tmp/unshadow_output
    with open('/tmp/unshadow_output', 'wb') as f:
        f.write(unshadow_output)


    # Run John the Ripper with the combined file and wordlist
    john_process = subprocess.Popen(['/sbin/john', '--format=crypt', '--wordlist=' + wordlist_path, '/tmp/unshadow_output'], stdout=subprocess.PIPE)
    john_output, _ = john_process.communicate()
    print(john_output.decode('utf-8'))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <passwd_file> <shadow_file> <wordlist_file>")
        sys.exit(1)
    passwd_file = sys.argv[1]
    shadow_file = sys.argv[2]
    wordlist_file = sys.argv[3]
    main(passwd_file, shadow_file, wordlist_file)