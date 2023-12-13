#!/usr/bin/env bash





# App data
app_dir="./app"

# Kernel module data
ko_module_name="sbtn_module"
ko_module_dir="./sbtn_kernel_module"
ko_module_install_path="/lib/modules/$(uname -r)/extra"


#remove old!!!
rm "${ko_module_dir}/${ko_module_name}.ko"


# ***********************************************
# * Kernel module - compile and and run on boot *
# ***********************************************

# Compile the module
pushd "$ko_module_dir"
make
popd

# Check if compilation was successful
if [ ! -f "${ko_module_dir}/${ko_module_name}.ko" ]; then
    echo "Compilation failed."
    exit 1
fi

#
# # Copy the compiled module to the system's module directory
# mkdir -p "${ko_module_install_path}"
# cp "${ko_module_dir}/${ko_module_name}.ko" "${ko_module_install_path}"
#
# # Add the module to /etc/modules if it's not already there
# if ! grep -qw "$ko_module_name" /etc/modules; then
#     echo "$ko_module_name" >> /etc/modules
# fi
#
# # Run depmod to update module dependencies
# depmod

# Load
# modprobe ${ko_module_name}
insmod sbtn_kernel_module/sbtn_module.ko



# Check if the module was loaded successfully
if ! lsmod | grep -q "$ko_module_name"; then
    echo "Failed to load the ${ko_module_name} kernel module."
    exit 1
fi



# REMOVE
cat /dev/sbtn
rmmod sbtn_kernel_module/sbtn_module.ko


echo "Kernel module installation complete."
