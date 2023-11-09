/**
 *  @file led_module.c
 *  @brief Python LED control module
 *
 * Pythom module implementing an interface for controlling a single LED connected to GPIO pin.
 *
 * It provides methods to turn on, turn off, or blink the led.
 *
 * The module defines the following methods:
 *  - init_led: Exports the PIO pin and sets its directions
 *  - turn_on: Turns the LED on by setting the GPIO pin to HIGH (overrides blinking)
 *  - turn_off: Turn the LED off by setting the GPIO pin to LOW (overrides blinking)
 *  - startBlinking: Starts a separate thread to meke the LED blink untill stopBlinking, turn_on, turn_off is called
 *  - stopBlinking: Stop the blinking thread and turns the LED off
 *
 *  TODO something about permissions
 *
 *  TODO disclamer? just to meke it look cool :D
 *
 *  TODO dependancies
 *
 *  TODO Compile with to add python.h
 * gcc -shared -o led_module.so led_module.c -fPIC $(python3-config --includes) $(python3-config --libs)
 *
 *
 *  @TODO Implemnent cleanup method that will close/unexport the GPIO pin when closing
 *
 *  @warning using /sys/class/gpio was DEPRECATED and should used! This module is only to be used for EDUCATIONAL purposes.
 *
 *  @author Matt (Martin) Hnizdo
 *
 *  @date 05/11/2023
 *
 *  @version 0.1
 *
 *  @bug might throw and error when the os a bit sluggish and takes a while to export the pin
 */


#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

#include <Python.h>
#include <pthread.h>


// ***********************************************
// * Definitions and variables                   *
// ***********************************************

#define GPIO_PATH "/sys/class/gpio/"
#define GPIO_EXPORT_PATH GPIO_PATH "export"
#define GPIO_UNEXPORT_PATH GPIO_PATH "unexport"
#define GPIO_VALUE_PATH_FORMAT GPIO_PATH "gpio%s/value"
#define GPIO_DIRECTION_PATH_FORMAT GPIO_PATH "gpio%s/direction"

#define DIRECTION_OUT "out"
#define DIRECTION_IN "in"
#define HIGH "1"
#define LOW "0"


static char* gpio_red    = NULL;    // store the GPIO pin for red LED
static char* gpio_yellow = NULL;    // store the GPIO pin for yellow LED
static char* gpio_green  = NULL;    // store the GPIO pin for green LED


// ***********************************************
// * GPIO handling - export,set direction,write  *
// ***********************************************


/**
 * @brief Exports the specified GPIO to make it visible in /sys/class/gpio
 *
 * By writing to the GPIO export file, the specified GPIO is made available
 * in the /sys/class/gpio directory.
 *
 * @note This function will terminate the program if it fails to open the
 * GPIO export file or fails to write to it.
 *
 * TODO: Implement a check to see if the GPIO is already exported.
 *
 * @param gpio The GPIO number as a string to be exported.
 */
static void export_gpio(const char* gpio) {
    int fd = open(GPIO_EXPORT_PATH, O_WRONLY);
    if (fd == -1) {
        perror("Unable to open " GPIO_EXPORT_PATH);
        exit(1);
    }

    write(fd, gpio, strlen(gpio));

    // TODO check if the write was ok
    // it throws error if the write tries to write to already exported
    // so should probably check that? :D

    // for now.. let's just assume :D  assume, assume - everything is fine.. right? :)

    // if (write(fd, gpio, strlen(gpio)) != strlen(gpio)) {
    //     perror("Error writing to " GPIO_EXPORT_PATH);
    //     exit(1);
    // }

    close(fd);

    usleep(500000); // small delay to make sure linux has time to add it
}


/**
 * @brief Sets direction of specicied GPIO pin
 *
 * By writing in or out to the direction file,
 * the GPIO will set to the appropriate direction.
 *
 * @note This function will terminate the program if it fails to open the
 * GPIO export file or fails to write to it.
 *
 * @param gpio The GPIO number as a string.
 * @param direction The direction as a string ("in" or "out").
 *
 */
static void set_gpio_direction(const char* gpio, const char* direction) {
    char path[40];
    sprintf(path, GPIO_DIRECTION_PATH_FORMAT, gpio);
    int fd = open(path, O_WRONLY);

    if (fd == -1) {
        perror("Unable to open GPIO direction file");
        exit(1);
    }

    if (write(fd, direction, strlen(direction)) != (ssize_t)strlen(direction)) {
        perror("Error writing to GPIO direction file");
        exit(1);
    }

    close(fd);
}

/**
 * @brief Write a value to specicied GPIO pin
 *
 * By writing value (1/0) to the value file,
 * the GPIO will set to set to either HIGH or Low.
 *
 * @note This function will terminate the program if it fails to open the
 * GPIO export file or fails to write to it.
 *
 * @param gpio The GPIO number as a string.
 * @param direction The value as a string ("0" or "1").
 *
 */
static void write_gpio(const char* gpio, const char* value) {
    char path[40];
    sprintf(path, GPIO_VALUE_PATH_FORMAT, gpio);
    int fd = open(path, O_WRONLY);

    if (fd == -1) {
        perror("Unable to open GPIO value file");
        exit(1);
    }

    if (write(fd, value, strlen(value)) != (ssize_t)strlen(value)) {
        perror("Error writing to GPIO value file");
        exit(1);
    }

    close(fd);
}

// TODO comment
static void close_gpio(const char* gpio) {
    int fd = open(GPIO_UNEXPORT_PATH, O_WRONLY);

    if (fd == -1) {
        perror("Unable to open /sys/class/gpio/unexport");
        exit(1);
    }

    write(fd, gpio, strlen(gpio));

    // if (write(fd, GPIO_DHT22, strlen(GPIO_DHT22)) != strlen(GPIO_DHT22)) {
    //     perror("Error writing to /sys/class/gpio/unexport");
    //     exit(1);
    // }
    close(fd);
}


// ***********************************************
// * Exposed python methods                      *
// ***********************************************

/**
 * @brief Initialize the LED GPIO.
 *
 * This function sets up a GPIO pin for use as an LED.
 * Exports -> set direction -> write low  (to start off)
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject containing a string representing the GPIO pin number.
 *
 * @return PyObject* Py_None on success, or NULL on failure with an exception set.
 */
static PyObject* init_led(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "sss", &gpio_red, &gpio_yellow, &gpio_green))
        return NULL;

    // Initialize red
    export_gpio(gpio_red);
    set_gpio_direction(gpio_red, DIRECTION_OUT);
    write_gpio(gpio_red, LOW);

    // Initialize yellow
    export_gpio(gpio_yellow);
    set_gpio_direction(gpio_yellow, DIRECTION_OUT);
    write_gpio(gpio_yellow, LOW);

    // Initialize green
    export_gpio(gpio_green);
    set_gpio_direction(gpio_green, DIRECTION_OUT);
    write_gpio(gpio_green, LOW);

    Py_RETURN_NONE;
}

/**
 * @brief Turn on the red LED.
 *
 * This function sets the red GPIO level to HIGH, effectively turning on the LED.
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject representing the arguments (unused).
 *
 * @return PyObject* Py_None.
 */
static PyObject* red_on(PyObject* self, PyObject* args) {
    write_gpio(gpio_green, LOW);
    write_gpio(gpio_yellow, LOW);

    write_gpio(gpio_red, HIGH);
    Py_RETURN_NONE;
}

/**
 * @brief Turn off the red LED.
 *
 * This function sets the red GPIO level to LOW, effectively turning off the LED.
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject representing the arguments (unused).
 *
 * @return PyObject* Py_None.
 */
static PyObject* red_off(PyObject* self, PyObject* args) {
    write_gpio(gpio_red, LOW);
    Py_RETURN_NONE;
}

/**
 * @brief Turn off the yellow LED.
 *
 * This function sets the yellow GPIO level to LOW, effectively turning off the LED.
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject representing the arguments (unused).
 *
 * @return PyObject* Py_None.
 */
static PyObject* yellow_on(PyObject* self, PyObject* args) {
    write_gpio(gpio_green, LOW);
    write_gpio(gpio_red, LOW);

    write_gpio(gpio_yellow, HIGH);
    Py_RETURN_NONE;
}

/**
 * @brief Turn off the yellow LED.
 *
 * This function sets the yellow GPIO level to LOW, effectively turning off the LED.
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject representing the arguments (unused).
 *
 * @return PyObject* Py_None.
 */
static PyObject* yellow_off(PyObject* self, PyObject* args) {
    write_gpio(gpio_yellow, LOW);
    Py_RETURN_NONE;
}

/**
 * @brief Turn off the green LED.
 *
 * This function sets the green GPIO level to LOW, effectively turning off the LED.
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject representing the arguments (unused).
 *
 * @return PyObject* Py_None.
 */
static PyObject* green_on(PyObject* self, PyObject* args) {
    write_gpio(gpio_yellow, LOW);
    write_gpio(gpio_red, LOW);

    write_gpio(gpio_green, HIGH);
    Py_RETURN_NONE;
}

/**
 * @brief Turn off the green LED.
 *
 * This function sets the green GPIO level to LOW, effectively turning off the LED.
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject representing the arguments (unused).
 *
 * @return PyObject* Py_None.
 */
static PyObject* green_off(PyObject* self, PyObject* args) {
    write_gpio(gpio_green, LOW);
    Py_RETURN_NONE;
}


/**
 * @brief Turn off all the LEDs.
 *
 * This function sets the all GPIO levels to LOW, effectively turning off all the LEDs.
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject representing the arguments (unused).
 *
 * @return PyObject* Py_None.
 */
static PyObject* all_off(PyObject* self, PyObject* args) {
    write_gpio(gpio_red, LOW);
    write_gpio(gpio_yellow, LOW);
    write_gpio(gpio_green, LOW);
    Py_RETURN_NONE;
}

/**
 * @brief Closes GPIO pins
 *
 * This function sets unexports all GPIO pins
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject representing the arguments (unused).
 *
 * @return PyObject* Py_None.
 */
static PyObject* close_led(PyObject* self, PyObject* args) {
    close_gpio(gpio_red);
    close_gpio(gpio_yellow);
    close_gpio(gpio_yellow);
}



// ***********************************************
// * Module definitions                          *
// ***********************************************


static PyMethodDef LedMethods[] = {
    {"init_led", init_led, METH_VARARGS, "Initialize LEDs - pass 'red', 'yellow', 'green' pins"},
    {"close_led", close_led, METH_VARARGS, "Unexports all the GPIO pins"},
    {"all_off", all_off, METH_VARARGS, "Turn off all LEDs"},

    {"red_on", red_on, METH_VARARGS, "Turn on red LED"},
    {"red_off", red_off, METH_VARARGS, "Turn off red LED"},
    {"yellow_on", yellow_on, METH_VARARGS, "Turn on yellow LED"},
    {"yellow_off", yellow_off, METH_VARARGS, "Turn off yellow LED"},
    {"green_on", green_on, METH_VARARGS, "Turn on green LED"},
    {"green_off", green_off, METH_VARARGS, "Turn off green LED"},


    {NULL, NULL, 0, NULL} // Sentinel
};


// Module definition
static struct PyModuleDef ledmodule = {
    PyModuleDef_HEAD_INIT,
    "led_module",   // name of module
    NULL,           // module documentation, may be NULL
    -1,             // size of per-interpreter state of the module
    LedMethods      // methods exposed to Python
};

// Module initialization
PyMODINIT_FUNC PyInit_led_module(void) {
    return PyModule_Create(&ledmodule);
}
























