# Installer script for the thermal camera UI.

apt update
apt full-upgrade

pip install -r requirements.txt --break-system-packages # Installs the required module. This almost certainly isn't the reccommended way but we ball
python3 initialiser.py # Creates the setup file.
python setup.py build_ext --inplace # cythonizes each of the python files to speed them up
cp thermalCamBoot.service /etc/systemd/system # Puts the service file that starts run.py on boot into systemd
systemctl daemon-reload
systemctl enable thermalCamBoot # Enables the boot service
echo 'Installer has finished!'
read -p 'Reboot now? (Y/n)' confirm
if [$confirm == true] ; then
    echo 'Rebooting now!'
    reboot
else
    echo 'Remember to reboot sometime in the near future to properly finish the installation.'