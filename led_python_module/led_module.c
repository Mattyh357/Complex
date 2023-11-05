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
#define GPIO_VALUE_PATH_FORMAT GPIO_PATH "gpio%s/value"
#define GPIO_DIRECTION_PATH_FORMAT GPIO_PATH "gpio%s/direction"

#define DIRECTION_OUT "out"
#define DIRECTION_IN "in"
#define HIGH "1"
#define LOW "0"


static char* stored_gpio = NULL;    // store the GPIO pin
static int _isBlinking = 0;         // Is led blinking?
static pthread_t blinking_thread;   // Blinking thread


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


// TODO blink blink blinkity blink!
// TODO probably could pass the time there tbh...
void* blink(void* arg) {
    char* gpio = (char*) arg;

    while (_isBlinking) {
        write_gpio(gpio, HIGH);
        usleep(250000);
        write_gpio(gpio, LOW);
        usleep(250000);
    }

    return NULL;
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
    const char* gpio;
    if (!PyArg_ParseTuple(args, "s", &gpio))
        return NULL;

    stored_gpio = strdup(gpio); // Store the GPIO pin


    export_gpio(stored_gpio);
    set_gpio_direction(stored_gpio, DIRECTION_OUT);
    write_gpio(stored_gpio, LOW);

    Py_RETURN_NONE;
}

/**
 * @brief Start blinking the LED on a separate thread.
 *
 * This function initiates the blinking of an LED by starting a new thread
 * and setting a flag that to indicate that led is blinking.
 * The LED will keep blinking until stopBlinking() is called.
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject representing the arguments (unused).
 *
 * @return PyObject* Py_None.
 */
static PyObject* startBlinking(PyObject* self, PyObject* args) {
    _isBlinking = 1;
    pthread_create(&blinking_thread, NULL, blink, stored_gpio);
    Py_RETURN_NONE;
}

/**
 * @brief Stop blinking the LED and wait for the thread to finish.
 *
 * This function sets a flag to stop the blinking of an LED and joins the
 * blinking thread, effectively waiting for the thread to terminate.
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject representing the arguments (unused).
 *
 * @return PyObject* Py_None.
 */
static PyObject* stopBlinking(PyObject* self, PyObject* args) {
    _isBlinking = 0;
    pthread_join(blinking_thread, NULL);
    Py_RETURN_NONE;
}

/**
 * @brief Turn on the LED.
 *
 * This function sets the GPIO level to HIGH, effectively turning on the LED.
 *
 * @note if LED was blinking before, it's not anymnore
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject representing the arguments (unused).
 *
 * @return PyObject* Py_None.
 */
static PyObject* turn_on(PyObject* self, PyObject* args) {
    // If blinking -> stop
    if (_isBlinking) {
        _isBlinking = 0;
        pthread_join(blinking_thread, NULL);
    }

    write_gpio(stored_gpio, HIGH);

    Py_RETURN_NONE;
}

/**
 * @brief Turn off the LED.
 *
 * This function sets the GPIO level to LOW, effectively turning off the LED.
 *
 * @note if LED was blinking before, it's not anymnore
 *
 * @param self The PyObject representing the module (unused).
 * @param args The PyObject representing the arguments (unused).
 *
 * @return PyObject* Py_None.
 */
static PyObject* turn_off(PyObject* self, PyObject* args) {
    // If blinking -> stop
    if (_isBlinking) {
        _isBlinking = 0;
        pthread_join(blinking_thread, NULL);
    }

    write_gpio(stored_gpio, LOW);
    Py_RETURN_NONE;
}


// ***********************************************
// * Module definitions                          *
// ***********************************************


static PyMethodDef LedMethods[] = {
    {"init_led", init_led, METH_VARARGS, "Initialize LED"},
    {"turn_on", turn_on, METH_VARARGS, "Turn on LED"},
    {"turn_off", turn_off, METH_VARARGS, "Turn off LED"},

    {"startBlinking", startBlinking, METH_VARARGS, "Start blinking like crazy"},
    {"stopBlinking", stopBlinking, METH_VARARGS, "Stop blinking"},

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


// TODO closing it would probably be nice: D

// void close_gpio() {
//     int fd;
//
//     // Unexport the pin
//     fd = open(GPIO_UNEXPORT, O_WRONLY);
//     if (fd == -1) {
//         perror("Unable to open /sys/class/gpio/unexport");
//         exit(1);
//     }
//     if (write(fd, GPIO_DHT22, strlen(GPIO_DHT22)) != strlen(GPIO_DHT22)) {
//         perror("Error writing to /sys/class/gpio/unexport");
//         exit(1);
//     }
//     close(fd);
// }
























