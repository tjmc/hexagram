# hexagram

Hexagram model 8150DD6

Frequency shift keying

Protocol:

Example

```
011111111110101010101010101010101011001100110011001100110011010010101011010101010100101011001101010100101010110101001011010010110011001100110101010100110010110011010011001101010010110011001010110010110011001011010101001010101100110011010011001011010011001011001100110101010000'
```

Find the prefix (at least 8 bits of 1)
```
111111110101010101010101010101011001100110011001100110011010010101011010101010100101011001101010100101010110101001011010010110011001100110101010100110010110011010011001101010010110011001010110010110011001011010101001010101100110011010011001011010011001011001100110101010000'
```

Decode with Differential Manchester

```
100000000000111111111111101000100000100111000100010010101011111110000111011101111001011110011011110100010001111101110101110111110001
```

```
Hex: 800fffa209c44abf8777979bd11f75df0

sync word                   0xfffa      32bit
packet length               0x20        16bit
MTU ID                      0x9c44ab    24bit
Unknown                     0xf8        16bit     Maybe tamper flags? I've only see 0xf8 and 0xb8. I'm pretty sure it's not a leak flag based on experience.
Meter #1                    0x777979    24bit     Binary Coded Decimal format
Meter #2                    0xbd11f7    24bit     Binary Coded Decimal format
CRC16                       0x5df0      32bit
```

To further decode
MTU ID, Meter #1 and #2 
The bits need to be negated and are little endian *bits* and big endian *bytes*
For example MTU ID
```
0x9c44ab
~100111000100010010101011
011000111011101101010100
```

Little endian *bits*
```
001010101101110111000110
```

Big endian *bytes*
MTU ID: 2809286

For the meter readings do the same thing
```
0x777979
011101110111100101111001
```
~
```
100010001000011010000110
```
to hex for BCD
```
0x247701
```
Reverse the order and treat as an integer
```
107742
```


CRC looks like CRC16-CCITT with a different initial value using bytes 0 - 28

Width = 16 bits
Truncated polynomial = 0x1021
Initial value = 0xf492
Input data is NOT reflected
Output CRC is NOT reflected
No XOR is performed on the output CRC

I find sometimes the last bit is incorrect. Not sure if it's my radio capture code or an decoded error

The CRC should be 0x5df1, but the packet is 0x5df0
```
