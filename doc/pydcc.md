# PyDCC user guide

This document is a user guide for those who want to use PyDCC for their application.

## Installing the PyDCC library

However, we decided to postpone the publication of our software module. Thus, we have to use this alternative.
```python
git pull
git checkout <version>
python setup.py sdist
pip install -e .
```

Explanation of the steps:
- Make sure being in the root from the git repository.
- git pull to get the latest changes.
- git checkout followed by the version you want to install. Versions are declared in the README.md.
- python setup.py bdist to build the projects. You will need to install setuptools therefore: pip install setuptools
- pip install -e . to install pydcc on a local machine.


Usually, we would use PyPi for distributing and installing our open source software. 
```python
python install pydcc
```

## Loading an DCC from file

DCCs were defined as XML files [1]. The code below loads an example provided by the PTB. By loading the XML file will be loaded and translated to an object structure.

Load DCC from file
```python
from dcc import dcc
dcco = DCC('dcc_gp_temperature_typical_v12.xml') # Load DCC from file
```

In case the DCC was revived from another system as a string or byte array (dcc_byte_array).
```python
dcco = DCC(byte_array = dcc_byte_array) # Load DCC from file
```

In case a compressed DCC was revived, previously compressed by PyDCC (compressed_dcc_byte_array).
```python
dcco = DCC(compressed_dcc = compressed_dcc_byte_array) # Load DCC from file
```

## Get the identification of the DCC

The DCC contains multiple identifications. However, this identification is identifying the DCC itself.

```python
dcco.uid()
```

## DCC version

The version of the DCC schema.

```python
dcco.version()
```


## Check if DCC was loaded successfully.

```python
if not dcco.status_report.is_loaded:
    print("Error: DCC was not loaded successfully!")
```



## Perform schema verification

The schema verification must be executed after loading the DCC.

Verify DCC file according to the official XML schema [2] when internet connection is available. 
```python
dcco.verify_dcc_xml(online=True)
```

Verify the DCC file according to the official XML schema [2] when the internet connection is unavailable. 
In this case, please make sure to download all required schema files to the local repository using the schema downloader class.
```python
dcco.verify_dcc_xml(online=False)
```

## Signature verification

The signature verification is executed automatically if not deactivate explicitly in the constructor.
However, make sure to provide a trust store before creating the DCC object, for example:
```python
trust_store = DCCTrustStore()
trust_store.load_trusted_root_from_file("../data/trusted_certs/root.crt")
trust_store.load_intermediate_from_file("../data/trusted_certs/sub.crt")
dcco = DCC(xml_file_name='../data/dcc/dcc_gp_temperature_typical_v12_signed.xml', trust_store=trust_store)
```
The trust store object can be reused for loading any other DCCs. The trust stores in the examples can not be used for your own signed DCCs. You have to use your respective trusted certificates. 

Remarks concerning signature verification:

- A XADES Baseline-B, Baseline-T or Baseline-LT signature is expected.
- In case of Baseline-T or Baseline-LT signatures the timestamp is currently not verified.
- The signature verification is performed based on chain model, i.e. the signing time is used as verification time. This means that all certificates in the certificate path must be valid at signing time.
- The signature verification currently does not support counter signatures or parallel signatures.
- After signature verification was performed, the variable 'root' contains the verified DCC without the signature element. The signature element is stored in the variable 'signature_section'.

If the DCC does not have a digital signature, no signature verification is performed.

If the signature verification fails e.g. due to an invalid signature, an invalid certificate chain, a revoked certificate etc. a DCCSignatureError is raised.

## Signer certificate
Returns the X.509 public key certificate corresponding to the private key that was used to sign the DCC. 
```python
dcco.get_signer_certificate()
```
## Signing time
Returns the signing time of the DCC. 
```python
dcco.get_signing_time()
```

## Calibration Date

Returns calibration date as datetime object. Note that the DCC defines the start date (beginPerformanceDate) and the end date (endPerformanceDate) of calibration. The date returned by this API refers to the end of calibration (endPerformanceDate).
```python
dcco.calibration_date()
```

Returns the number of days since calibration (endPerformanceDate). This function was designed for checking the calibration date against the requirements of a quality management system (QMS). A QMS may define a maximum number of days until a device has to be calibrated.
```python
dcco.days_since_calibration()
```



## Calibration Laboratory Name

Returns the name of the calibration laboratory.
```python
dcco.calibration_laboratory_name()
```



## Links to other documents

Return true if a link to a previous DCC exists.
```python
dcco.has_previous_report()
```



## Evaluate the Uncertainty

Processing of DCC automatically is a key motivation for PyDCC.
Thus, evaluation the uncertainty of a DCC according to specific requirements was evaluated. 
Note that to process DCC automatically, data within the DCC must follow particular format requirements defined by [Good Practice](https://dccwiki.ptb.de/en/gp_home).

The essential method to get the calibration results is get_calibration_results. However, the evaluation of measurement results is an advanced task. 
Therefore, please try the example  ../examples/uncertainty_check_example.py



## Compressed DCC

This example generates a compressed DCC that can be embedded on a device with constraint resources. 

```python
# Generate compressed DCC
embdcc = dcco.generate_compressed_dcc()   
compression_ratio_100 = embdcc['compression_ratio'] * 100
print('DCC size %d bytes' % embdcc['bytes_uncompressed'])
print('Compressed DCC size %d bytes' % embdcc['bytes_compressed'])
print('Embedded DCC compression ratio %.1f%%' % compression_ratio_100)
print('CRC32 of raw data: %x' % embdcc['crc32'])
compressed_data = embdcc['dcc_xml_raw_data_compressed']
```
In the second step, the compressed data (compressed_data) would be transferred to the corresponding sensor system.

Compression results:
The original DCC size for Siliziumkugel.xml in version 2.4.0 was 30926 bytes.
The compressed DCC size was 5324 bytes.
DCC compression ratio 17.2%.
CRC32 of raw data: efc19810

## Get a specific identification

The DCC can store multiple item identifications for the calibrated item. Identification can be a serial number, a manufacturer id, a product name, or any custom string identifying the calibrated item.
With the method get_item_id_by_name, a specific identification can be returned. However, the exact name of this identification must be known.
```python
serial_number = dcco.get_item_id_by_name('Serial no.')
```

Try the example code in ../examples/read_identifications.py

## Get metadata from DCC

Metadata in a DCC includes information about the calibration, such as the basic calibration value, the basic conformity, or the data quality (QoX) parameters. This information can be retrieved using the `get_calibration_metadata` method.

```python
metadata = dcco.get_calibration_metadata(refType='QoX_parameter')
for item in metadata:
    print(item)
```

Try the example code in ../examples/read_QoX_metadata.py

## Get the mandatory language

```python
dcco.mandatory_language()
```

Return example: 'de'

