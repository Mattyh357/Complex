/* TODO header stuff */

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
static int _isBlinking = 0;         // Is led blinking? TODO can be bool?
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
}

//TODO comments
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

//TODO comments
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


// TODO comments
static PyObject* startBlinking(PyObject* self, PyObject* args) {
    _isBlinking = 1;
    pthread_create(&blinking_thread, NULL, blink, stored_gpio);
    Py_RETURN_NONE;
}

// TODO comments
static PyObject* stopBlinking(PyObject* self, PyObject* args) {
    _isBlinking = 0;
    pthread_join(blinking_thread, NULL);
    Py_RETURN_NONE;
}


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


static PyObject* turn_on(PyObject* self, PyObject* args) {
    write_gpio(stored_gpio, HIGH);

    Py_RETURN_NONE;
}

static PyObject* turn_off(PyObject* self, PyObject* args) {
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
























