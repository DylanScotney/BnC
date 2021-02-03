# **B & C Order Processor Package**

A simple command line package that processes orders and stock
requirements for B & C 
## <u>Setup and Installation</u>
### **1. Downloading the Package**
1. [Install git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
2. Execute the following command on the command line
```
git clone https://github.com/DylanScotney/BnC.git
```
3. You can then update the package with
```
git pull
```
Note that after a new git pull you will need to reinstall the changes by following step 3. below.
### **2. Package Config**
The first step is to step up the 
[PackageConfig.py](lib/PackageConfig.py) file to and define the
following parameters. 

| Parameter                 | Description                           |
|---------------------------|---------------------------------------|
| DB_BASE_PATH              | This should be the path of the directory you would like to store the database                      |
| OS_IS_WINDOWS             | True/False if operating system is windows or MAC
| PATH_WKHTMLTOPDF          | If OS_IS_WINDOWS == True **then you must also install <u>[this](https://wkhtmltopdf.org/downloads.html)</u>**. This variable should be the path to the .exe file after install
| WORKING_DIRECTORY         | This is the path to a <u>**temporary**</u> directory that the package will use. **Ensure that nothing important is contained inside this directory as it will be continuously deleted/wiped.**
| DEFAULT_OUTPUT_LOCATION  | The directory where the packing slips and order summaries will be outputted

### **3. Installation**
<u>**After**</u> [PackageConfig.py](lib/PackageConfig.py) has been set
up you will be able to install the package with the following command
using the Anaconda Prompt command line
```
pip install <path to package directory>
```

## <u>Example Usage</u>
Once the package has been installed you will be able to provide a
csv of open orders and produce packing slips as well as a summary of
stock order requirements using the below command

```
BnC-process-orders -date <delivery date> -file <open orders file>
```

Where delivery date must be formatted yyyy/MM/dd, and (for safety) the
file path should use forward slashes. For example:

```
BnC-process-orders -date 2021/01/09 -file C:/Users/dylan/Documents/Programming/BnC/DB/OpenOrders_20210109.csv
```

## <u>Commands</u>
**Process all input orders and produce stock requirements**
```
BnC-process-orders -date <delivery date> -file <open orders csv>
```
**Produce packing slips for a given delivery date**
```
BnC-packing-slips -date <delivery date> -file <route stop numbers csv>
```
Note: route stop numbers csv is expecting columns: OrderID, Stop,
Driver, Postcode


## <u>Warnings & Things to Keep In Mind</u>
1. To correctly identify fortnightly Coffee orders, this package
requires that the previous week has been processed. If not you will be
greeted with the following warning message:
```
WARNING: No deliveries have been processed for last Saturday.

Continue? [Y/N]
```
There are several other warnings in place to help protect against
misuse with non-chronological delivery dates


