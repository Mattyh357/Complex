#!/usr/bin/env bash



# App data
app_dir="./app"

# Python module data
py_module_name="led_module"
py_module_dir="./led_python_module"
py_module_c_file="${py_module_dir}/${py_module_name}.c"
py_module_output="${py_module_dir}/${py_module_name}.so"


# ***********************************************
# * Python module - compile and copy            *
# ***********************************************


PYTHON_INCLUDES=$(python3-config --includes)
PYTHON_LIBS=$(python3-config --ldflags)

# Compile the Python module
gcc -shared -o "${py_module_output}" "${py_module_c_file}" -fPIC ${PYTHON_INCLUDES} ${PYTHON_LIBS}

# Check if compilation was successful
if [ ! -f "${py_module_output}" ]; then
    echo "Compilation of Python module failed."
    exit 1
fi

# Copy into app
cp "${py_module_output}" "${app_dir}/${py_module_name}.so"


echo "Python module compiled successfully."

./test_module.py

