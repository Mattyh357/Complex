/**
 *  @file sbtn_module.c
 *  @brief
 *
 *
 *  @TODO
 *
 *  @author Matt (Martin) Hnizdo
 *
 *  @date 05/11/2023
 *
 *  @version 0.1
 *
 *  @bug A LOT I would guess ;D
 */


#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/gpio.h>

#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>


// ***********************************************
// * Definitions and variables                   *
// ***********************************************

#define SBTN_GPIO_PIN 18

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Matt (Martin)");
MODULE_DESCRIPTION("A simple Linux Super-button driver");
MODULE_VERSION("0.0001");

static int sbtn_major;
static struct class* sbtn_class = NULL;
static struct cdev sbtn_cdev;
static struct device* sbtn_device = NULL;




// ***********************************************
// * Button specific functions                   *
// ***********************************************


/**
 * @brief Initialize GPIO for reading
 *
 * Requests GPIO pin and sets its direction to input to allow for reading.
 *
 * @note This function will terminate if it fails to request or set direction
 *
 * @return int Return 0 when all ok.
 */
static int sbtn_GPIO_init(void) {
    // Request the GPIO pin
    if (gpio_request(SBTN_GPIO_PIN, "sbtn_gpio")) {
        printk(KERN_ERR "SUPER BUTTON: Failed to request GPIO %d\n", SBTN_GPIO_PIN);
        return 1;
    }

    // Set the GPIO to input
    if (gpio_direction_input(SBTN_GPIO_PIN)) {
        printk(KERN_ERR "SUPER BUTTON: Failed to set GPIO %d as input\n", SBTN_GPIO_PIN);
        gpio_free(SBTN_GPIO_PIN);
        return 1;
    }

    return 0;
}

/**
 * @brief Get the status of the button.
 *
 * Reads the value of a GPIO pin connected to a button and inverts its logic to return 1 when button is pressed
 *
 * @return int Returns `1` if the button is pressed, and `0` if it is not pressed.
 */
static int sbtn_get_status(void) {
    return !gpio_get_value(SBTN_GPIO_PIN); // Returns 0 if not pressed, 1 if pressed
}

/**
 * @brief Free the GPIO pin.
 *
 * Releases the GPIO pin associated with the button when it's no longer needed.
 */
static void sbtn_GPIO_free(void) {
    gpio_free(SBTN_GPIO_PIN);
}


// ***********************************************
// * Device file functions                       *
// ***********************************************

/**
 * @brief Read the status of the button.
 *
 * Called when a red operation occurs on the device file.
 *
 * Reads the current status of the button and writes it to the user buffer
 * as a single character (0/1) and \n
 *
 * @param filp A pointer to the file object that represents the opened device file.
 * @param buffer The user buffer to write data to.
 * @param length The length of the user buffer.
 * @param offset The current position in the buffer.
 *
 * @return ssize_t The number of bytes written or a negative error code,
 */
static ssize_t sbtn_read(struct file *filp, char __user *buffer, size_t length, loff_t *offset) {
    const size_t btn_state_size = 2; // 0/1 + \n
    char btn_state[2]; // Buffer to hold the button state string

    btn_state[0] = sbtn_get_status() + '0'; // '0' or '1'
    btn_state[1] = '\n';

    // Already read
    if (*offset > 0) {
        return 0;
    }

    // Buffer check
    if (length < btn_state_size - 1) {
        return -EINVAL; // Invalid argument
    }

    if (copy_to_user(buffer, btn_state, bytes_to_write)) {
        return -EFAULT; // Bad address
    }

    // Update offset and return the number of bytes written
    *offset += btn_state_size;
    return btn_state_size;
}


/**
 * @brief File operations for the SUPER BUTTON device.
 *
 * This structure maps file operations to the corresponding functions.
 * Operations open and release are set to NULL as they are not used.
 */
static struct file_operations sbtn_file_ops = {
    .owner = THIS_MODULE,
    .open = NULL,
    .release = NULL,
    .read = sbtn_read,
};

// ***********************************************
// * Core kernel module functions                *
// ***********************************************

// TODO comments
static int __init sbtn_init(void) {
    int err;
    dev_t dev_num;

    printk(KERN_INFO "SUPER BUTTON: Initializing the sBTN LKM\n");

    // Call the button-specific init function.
    if (sbtn_GPIO_init() != 0) {
        return -1; //fail
    }

    // Allocate major number for the device
    err = alloc_chrdev_region(&dev_num, 0, 1, "sbtn");
    if (err < 0) {
        printk(KERN_ALERT "SUPER BUTTON: alloc_chrdev_region failed\n");
        return err;
    }
    sbtn_major = MAJOR(dev_num);

    // Create device class
    sbtn_class = class_create(THIS_MODULE, "sbtn");
    if (IS_ERR(sbtn_class)) {
        unregister_chrdev_region(MKDEV(sbtn_major, 0), 1);
        printk(KERN_ALERT "SUPER BUTTON: class_create failed\n");
        return PTR_ERR(sbtn_class);
    }

    // Initialize the cdev structure and add it to the kernel space
    cdev_init(&sbtn_cdev, &sbtn_file_ops);
    sbtn_cdev.owner = THIS_MODULE;
    err = cdev_add(&sbtn_cdev, dev_num, 1);
    if (err < 0) {
        class_destroy(sbtn_class);
        unregister_chrdev_region(MKDEV(sbtn_major, 0), 1);
        printk(KERN_ALERT "SUPER BUTTON: cdev_add failed\n");
        return err;
    }

    // Create the device and device file
    sbtn_device = device_create(sbtn_class, NULL, dev_num, NULL, "sbtn");
    if (IS_ERR(sbtn_device)) {
        cdev_del(&sbtn_cdev);
        class_destroy(sbtn_class);
        unregister_chrdev_region(MKDEV(sbtn_major, 0), 1);
        printk(KERN_ALERT "SUPER BUTTON: device_create failed\n");
        return PTR_ERR(sbtn_device);
    }

    printk(KERN_INFO "SUPER BUTTON: Device initialized\n");
    return 0;
}

// TODO comments
static void __exit sbtn_exit(void) {
    // Clean up
    device_destroy(sbtn_class, MKDEV(sbtn_major, 0));
    class_unregister(sbtn_class);
    class_destroy(sbtn_class);
    unregister_chrdev_region(MKDEV(sbtn_major, 0), 1);
    cdev_del(&sbtn_cdev);

    sbtn_GPIO_free();

    printk(KERN_INFO "SUPER BUTTON: Device exit\n");
}

module_init(sbtn_init);
module_exit(sbtn_exit);
