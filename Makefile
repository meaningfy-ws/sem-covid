BUILD_PRINT = \e[1;34mSTEP: \e[0m

#-----------------------------------------------------------------------------
# Basic commands
#-----------------------------------------------------------------------------

install:
	@ echo "$(BUILD_PRINT)Installing the requirements"
	@ pip install --upgrade pip
	@ pip install -r requirements.txt

test:
	@ echo "$(BUILD_PRINT)Running the tests"
	@ pytest
